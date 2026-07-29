import time
from collections import Counter

_keyboard = None  # 延迟导入


# =====================
# 数据统计
# =====================
key_count = 0
char_count = 0
last_press_time = 0
_listener = None
_key_counter = Counter()

# 特殊键的友好名称映射
_SPECIAL_KEY_NAMES = {
    "Key.space": "空格",
    "Key.enter": "回车",
    "Key.backspace": "退格",
    "Key.tab": "Tab",
    "Key.caps_lock": "CapsLock",
    "Key.shift": "Shift",
    "Key.shift_l": "左Shift",
    "Key.shift_r": "右Shift",
    "Key.ctrl": "Ctrl",
    "Key.ctrl_l": "左Ctrl",
    "Key.ctrl_r": "右Ctrl",
    "Key.alt": "Alt",
    "Key.alt_l": "左Alt",
    "Key.alt_r": "右Alt",
    "Key.escape": "Esc",
    "Key.up": "↑",
    "Key.down": "↓",
    "Key.left": "←",
    "Key.right": "→",
    "Key.home": "Home",
    "Key.end": "End",
    "Key.page_up": "PageUp",
    "Key.page_down": "PageDown",
    "Key.insert": "Insert",
    "Key.delete": "Delete",
    "Key.f1": "F1",
    "Key.f2": "F2",
    "Key.f3": "F3",
    "Key.f4": "F4",
    "Key.f5": "F5",
    "Key.f6": "F6",
    "Key.f7": "F7",
    "Key.f8": "F8",
    "Key.f9": "F9",
    "Key.f10": "F10",
    "Key.f11": "F11",
    "Key.f12": "F12",
    "Key.print_screen": "PrintScreen",
    "Key.scroll_lock": "ScrollLock",
    "Key.pause": "Pause",
    "Key.num_lock": "NumLock",
}


def _get_key_name(key):
    """获取按键的友好名称"""
    try:
        if hasattr(key, 'char') and key.char is not None:
            if key.char == ' ':
                return '空格'
            return key.char
    except AttributeError:
        pass

    key_str = str(key)
    # 去掉引号
    if key_str.startswith("'") and key_str.endswith("'"):
        return key_str[1:-1]
    # 特殊键映射
    return _SPECIAL_KEY_NAMES.get(key_str, key_str)


# =====================
# 回调函数
# =====================
def on_press(key):
    """键盘按下回调"""
    global key_count, char_count, last_press_time

    key_count += 1
    last_press_time = time.time()

    # 统计按键
    key_name = _get_key_name(key)
    _key_counter[key_name] += 1

    # 统计普通字符（排除特殊键）
    try:
        if key.char:
            char_count += 1
    except AttributeError:
        pass


# =====================
# 控制函数
# =====================
def start():
    """启动键盘监听"""
    global _listener, _keyboard
    if _keyboard is None:
        try:
            from pynput import keyboard as _keyboard
        except Exception as e:
            print(f"[键盘监听] 启动失败: {e}")
            return
    try:
        _listener = _keyboard.Listener(on_press=on_press)
        _listener.start()
    except Exception as e:
        print(f"[键盘监听] 启动监听失败: {e}")


def stop():
    """停止键盘监听"""
    global _listener
    if _listener:
        _listener.stop()
        _listener = None


def get_data():
    """获取键盘统计数据"""
    # 找出最常按的键
    most_common = _key_counter.most_common(1)
    top_key = most_common[0][0] if most_common else "无"
    top_count = most_common[0][1] if most_common else 0

    # 找出 TOP 5
    top5 = _key_counter.most_common(5)

    return {
        "keys": key_count,
        "chars": char_count,
        "top_key": top_key,
        "top_count": top_count,
        "top5": top5,
    }


def is_typing():
    """判断最近是否正在输入（3秒内）"""
    return (time.time() - last_press_time) < 3
