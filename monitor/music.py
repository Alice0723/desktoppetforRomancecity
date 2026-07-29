import threading
import time
import re

_win32gui = None
_win32process = None


def _init_win32():
    """延迟初始化 win32gui"""
    global _win32gui
    if _win32gui is None:
        try:
            import win32gui
            _win32gui = win32gui
        except ImportError:
            pass
    return _win32gui


def _init_win32process():
    """延迟初始化 win32process"""
    global _win32process
    if _win32process is None:
        try:
            import win32process
            _win32process = win32process
        except ImportError:
            pass
    return _win32process


# =====================
# 数据状态
# =====================
current_music = {
    "title": "暂无播放",
    "artist": ""
}

playing = False
_monitor_thread = None
_running = False

# 防抖机制：连续N次未检测到音乐才判定为停止
_not_playing_count = 0
_NOT_PLAYING_THRESHOLD = 3  # 3次 * 2秒 = 6秒

# 调试日志
_debug_log = []
DEBUG_MAX_LINES = 50


def _debug(msg):
    """调试日志"""
    global _debug_log
    line = f"[music] {msg}"
    _debug_log.append(line)
    if len(_debug_log) > DEBUG_MAX_LINES:
        _debug_log.pop(0)
    print(line, flush=True)


def get_debug_log():
    """获取调试日志"""
    return _debug_log.copy()


# =====================
# 已知音乐播放器窗口标题模式
# =====================
MUSIC_PLAYER_PATTERNS = [
    # 网易云音乐
    (r'网易云音乐\s*-\s*(.+)', '网易云音乐'),
    (r'(.+?)\s*-\s*网易云音乐', '网易云音乐'),
    (r'网易云音乐', '网易云音乐'),
    # 网页版音乐 / 视频站点
    (r'(.+?)\s*[-|_]\s*YouTube(?:\s*[-|_].+)?', 'YouTube'),
    (r'(.+?)\s*[-|_]\s*(?:Bilibili|哔哩哔哩)(?:\s*[-|_].+)?', 'Bilibili'),
    (r'(.+?)\s*[-|_]\s*网易云音乐(?:\s*[-|_].+)?', '网易云音乐'),
    # QQ音乐
    (r'QQ音乐\s*-\s*(.+)', 'QQ音乐'),
    (r'(.+?)\s*-\s*QQ音乐', 'QQ音乐'),
    (r'QQ音乐', 'QQ音乐'),
    # 酷狗音乐
    (r'酷狗音乐\s*-\s*(.+)', '酷狗音乐'),
    (r'(.+?)\s*-\s*酷狗', '酷狗音乐'),
    (r'酷狗音乐', '酷狗音乐'),
    # 酷我音乐
    (r'酷我音乐\s*-\s*(.+)', '酷我音乐'),
    (r'酷我音乐', '酷我音乐'),
    # Spotify
    (r'Spotify\s*-\s*(.+)', 'Spotify'),
    (r'Spotify:\s*(.+)', 'Spotify'),
    (r'Spotify', 'Spotify'),
    # foobar2000
    (r'foobar2000:\s*(.+)', 'foobar2000'),
    # VLC
    (r'VLC media player\s*-\s*(.+)', 'VLC'),
    # Poweramp
    (r'Poweramp\s*-\s*(.+)', 'Poweramp'),
    # 抖音
    (r'抖音', '抖音'),
    # B站
    (r'B站', 'Bilibili'),
    (r'bilibili', 'Bilibili'),
    (r'哔哩哔哩', 'Bilibili'),
    # YouTube
    (r'YouTube', 'YouTube'),
    (r'YouTube Music', 'YouTube Music'),
]

# 已知音乐播放器窗口标题关键字
MUSIC_KEYWORDS = [
    '网易云音乐', 'QQ音乐', '酷狗音乐', '酷我音乐',
    'Spotify', 'foobar2000', 'VLC', 'Poweramp',
    'MusicBee', 'winamp', 'Apple Music',
    'AIMP', 'PotPlayer', 'KMPlayer',
    '抖音', 'Bilibili', '哔哩哔哩', 'YouTube', 'YouTube Music',
]

# 已知音乐播放器进程名（小写匹配 → 显示名）
MUSIC_PROCESS_NAMES = {
    'netease': '网易云音乐',
    'cloudmusic': '网易云音乐',
    'qqmusic': 'QQ音乐',
    'kuwo': '酷我音乐',
    'kugou': '酷狗音乐',
    'spotify': 'Spotify',
    'foobar2000': 'foobar2000',
    'vlc': 'VLC',
    'poweramp': 'Poweramp',
    'musicbee': 'MusicBee',
    'aimp': 'AIMP',
    'winamp': 'Winamp',
    'potplayer': 'PotPlayer',
    'kmplayer': 'KMPlayer',
    'applemusic': 'Apple Music',
    'music': '音乐',
    'youtube': 'YouTube',
    'douyin': '抖音',
    'bilibili': 'Bilibili',
}


# =====================
# Windows 音频检测
# =====================
def _check_audio_active():
    """
    检测是否有音频正在播放，并获取歌名+歌手
    综合策略：pycaw检测音频 + psutil检测进程 + 窗口标题获取歌名
    """
    # Step 1: 确认是否有音乐在播放（pycaw + psutil 双重确认）
    is_playing = False
    player_name = ""

    # 1a: pycaw — 检查所有音频会话（包括 Inactive 的音乐播放器）
    try:
        pycaw_info = _check_with_pycaw()
        if pycaw_info:
            is_playing = True
            player_name = pycaw_info.get("artist", "")
            _debug(f"pycaw 检测到: {pycaw_info}")
    except Exception as e:
        _debug(f"pycaw异常: {e}")

    # 1b: psutil 进程检测（即使 pycaw 没检测到，只要播放器在运行就算）
    if not is_playing:
        try:
            proc_info = _detect_music_process()
            if proc_info:
                is_playing = True
                player_name = proc_info.get("artist", "")
                _debug(f"进程检测到音乐播放器: {proc_info}")
        except Exception as e:
            _debug(f"进程检测异常: {e}")

    if not is_playing:
        _debug("未检测到音频播放")
        return False, {"title": "暂无播放", "artist": ""}

    # Step 2: 尝试从窗口标题获取歌名和歌手
    try:
        title_info = _get_music_from_window_title()
        if title_info and title_info.get("title"):
            _debug(f"窗口标题获取歌名成功: {title_info}")
            return True, title_info
    except Exception as e:
        _debug(f"窗口标题异常: {e}")

    # Step 3: 窗口标题拿不到歌名，用 player_name 兜底
    if player_name:
        _debug(f"使用兜底方案: {player_name}")
        return True, {"title": f"♪ {player_name}", "artist": player_name}

    return True, {"title": "♪ 音乐播放中", "artist": ""}


def _check_with_pycaw():
    """使用 pycaw 检查音频会话（宽松模式：音乐播放器的 Inactive 会话也算）"""
    try:
        from pycaw.pycaw import AudioUtilities
        sessions = AudioUtilities.GetAllSessions()

        for session in sessions:
            process_name = ""
            try:
                if session.Process:
                    process_name = session.Process.name()
            except Exception:
                pass

            if not process_name:
                continue

            process_lower = process_name.lower()

            # 检查是否是音乐播放器进程
            is_music_player = False
            display_name = ""
            for key, display in MUSIC_PROCESS_NAMES.items():
                if key in process_lower:
                    is_music_player = True
                    display_name = display
                    break

            if not is_music_player:
                continue

            state_text = "Active" if session.State == 1 else f"Inactive({session.State})"

            # 尝试获取显示名
            try:
                if hasattr(session, 'GetDisplayName'):
                    dn = session.GetDisplayName() or ""
                    if dn and dn != "Default Sound":
                        display_name = dn
            except Exception:
                pass

            # 音乐播放器会话：无论 Active 还是 Inactive 都视为可能在播放
            # 因为很多播放器（如QQ音乐）使用 WASAPI 独占模式，会话可能显示为 Inactive
            _debug(f"pycaw 发现音乐播放器会话: {process_name} 状态={state_text} 显示名={display_name}")

            # 优先使用显示名
            if display_name and display_name not in MUSIC_PROCESS_NAMES.values():
                # 显示名不是播放器名本身，可能是歌曲名
                return {
                    "title": display_name[:60],
                    "artist": display_name
                }

            return {
                "title": f"♪ {display_name}",
                "artist": display_name
            }

        return None
    except ImportError:
        _debug("pycaw 未安装")
        return None
    except Exception as e:
        _debug(f"pycaw 异常: {e}")
        return None


# 非歌曲名的窗口标题（QQ音乐等播放器的内部窗口）
NON_SONG_TITLES = {
    '播放队列', 'DynamicLyricWindow', '歌词',
    'QQMusic_MolePluginWnd', 'QQMusic Dummy Window',
    'QQMusic_COM_WND', 'TXMenuWindow', 'GDI+ Window',
    'MSCTFIME UI', 'Default IME', 'Sogou_TSF_UI',
    'HintWnd', '已开始播放提示', 'Heysocks',
}


def _get_music_from_window_title():
    """
    从窗口标题获取当前播放的歌曲名
    优先：通过 psutil 找到音乐播放器进程，再通过 PID 找到对应的歌曲标题窗口
    其次：枚举所有可见窗口匹配已知播放器模式
    """
    win32gui = _init_win32()
    win32process = _init_win32process()
    if win32gui is None:
        return None

    # 方法1：通过 psutil 找到音乐播放器进程的 PID，然后找对应的歌曲标题窗口
    try:
        import psutil
        music_pids = {}  # pid -> display_name
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = (proc.info['name'] or '').lower()
                for key, display in MUSIC_PROCESS_NAMES.items():
                    if key in name:
                        music_pids[proc.info['pid']] = display
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if music_pids:
            result = None

            def _enum_by_pid(hwnd, _):
                nonlocal result
                if result is not None:
                    return
                if not win32gui.IsWindow(hwnd):
                    return
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                except Exception:
                    return
                if pid not in music_pids:
                    return

                title = win32gui.GetWindowText(hwnd)
                if not title:
                    return
                title = title.strip()
                if not title:
                    return

                # 跳过已知的非歌曲窗口
                for nontitle in NON_SONG_TITLES:
                    if nontitle.lower() in title.lower():
                        return

                # 跳过纯播放器名（如 "QQ音乐"）
                display_name = music_pids[pid]
                if title == display_name:
                    return

                # 尝试解析 "歌名 - 歌手" 格式
                song_info = _parse_song_title(title, display_name)
                if song_info:
                    result = song_info

            win32gui.EnumWindows(_enum_by_pid, None)
            if result:
                return result
    except ImportError:
        _debug("psutil 未安装，使用备用窗口匹配")
    except Exception as e:
        _debug(f"psutil窗口匹配异常: {e}")

    # 方法2：备用方案 — 枚举所有可见窗口用模式匹配
    try:
        result = None

        def _enum_callback(hwnd, _):
            nonlocal result
            if result is not None:
                return
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return

            # 精确模式匹配
            for pattern, player_name in MUSIC_PLAYER_PATTERNS:
                match = re.match(pattern, title)
                if match:
                    groups = match.groups()
                    if len(groups) >= 1 and groups[0]:
                        result = {
                            "title": groups[0].strip(),
                            "artist": player_name
                        }
                    else:
                        result = {
                            "title": title[:60],
                            "artist": player_name
                        }
                    return

            # 关键字模糊匹配
            title_lower = title.lower()
            for kw in MUSIC_KEYWORDS:
                if kw.lower() in title_lower:
                    result = {
                        "title": title[:60],
                        "artist": kw
                    }
                    return

        win32gui.EnumWindows(_enum_callback, None)
        return result
    except Exception:
        return None


def _parse_song_title(title, player_name):
    """
    解析歌曲标题
    常见格式：
    - "歌名 - 歌手" (QQ音乐、网易云音乐等)
    - "歌名 - 歌手   " (带尾部空格)
    - "歌名" (纯歌名)
    """
    # 清理尾部空格和特殊字符
    clean_title = title.strip().rstrip()

    # 尝试 "歌名 - 歌手" 格式（用 " - " 分隔）
    # 注意：只用第一个 " - " 分割，因为歌名里可能包含 "-"
    if ' - ' in clean_title:
        parts = clean_title.split(' - ', 1)
        song_name = parts[0].strip()
        artist_name = parts[1].strip()
        if song_name and artist_name:
            # 检查 artist 是否是播放器名（有些格式是 "歌名 - 播放器"）
            if artist_name not in MUSIC_PROCESS_NAMES.values() and artist_name not in MUSIC_KEYWORDS:
                return {
                    "title": song_name[:60],
                    "artist": artist_name[:60]
                }
            # artist 是播放器名，把整个作为歌名
            return {
                "title": song_name[:60],
                "artist": player_name
            }

    # 没有 " - " 分隔符，整个作为歌名
    if clean_title and len(clean_title) > 1:
        return {
            "title": clean_title[:60],
            "artist": player_name
        }

    return None


def _detect_music_process():
    """使用 psutil 检测音乐播放器进程"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = (proc.info['name'] or '').lower()
                for key, display_name in MUSIC_PROCESS_NAMES.items():
                    if key in name:
                        return {
                            "title": f"♪ {display_name}",
                            "artist": display_name
                        }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    except ImportError:
        _debug("psutil 未安装，尝试 win32 进程检测")
        return _detect_music_process_win32()
    except Exception as e:
        _debug(f"psutil 异常: {e}")
        return None


def _detect_music_process_win32():
    """使用 win32 枚举窗口检测音乐进程（备用方案）"""
    win32gui = _init_win32()
    win32process = _init_win32process()
    if win32gui is None:
        return None

    try:
        result = None

        def _enum_callback(hwnd, _):
            nonlocal result
            if result is not None:
                return
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
            title_lower = title.lower()
            for kw in MUSIC_KEYWORDS:
                if kw.lower() in title_lower:
                    result = {"title": title[:60], "artist": kw}
                    return

        win32gui.EnumWindows(_enum_callback, None)
        return result
    except Exception:
        return None


def _monitor_loop():
    """音频监控循环（带防抖）"""
    global playing, current_music, _not_playing_count

    _debug("音乐监控线程启动")
    check_count = 0

    while _running:
        try:
            is_playing, music_info = _check_audio_active()
            check_count += 1

            if is_playing:
                _not_playing_count = 0
                if not playing or current_music.get("title") != music_info.get("title"):
                    _debug(f"检测到音乐: {music_info}")
                playing = True
                current_music = music_info
            else:
                _not_playing_count += 1
                if _not_playing_count >= _NOT_PLAYING_THRESHOLD:
                    if playing:
                        _debug("音乐停止")
                    playing = False
                    current_music = {"title": "暂无播放", "artist": ""}
        except Exception as e:
            _not_playing_count += 1
            _debug(f"监控循环异常: {e}")
            if _not_playing_count >= _NOT_PLAYING_THRESHOLD:
                playing = False

        # 每2秒检查一次
        time.sleep(2)

    _debug("音乐监控线程停止")


# =====================
# 控制函数
# =====================
def get_music():
    """获取当前音乐信息"""
    return current_music


def set_music(title, artist):
    """设置当前音乐信息（手动设置）"""
    global current_music, playing, _not_playing_count
    current_music = {
        "title": title,
        "artist": artist
    }
    playing = True
    _not_playing_count = 0
    _debug(f"手动设置音乐: {title} - {artist}")


def is_playing():
    """判断是否正在播放音乐"""
    return playing


def start():
    """启动音乐监听"""
    global _monitor_thread, _running

    if _running:
        return

    _running = True
    _monitor_thread = threading.Thread(target=_monitor_loop, daemon=True)
    _monitor_thread.start()


def stop():
    """停止音乐监听"""
    global _running, _monitor_thread
    _running = False
    if _monitor_thread:
        _monitor_thread.join(timeout=3)
        _monitor_thread = None
