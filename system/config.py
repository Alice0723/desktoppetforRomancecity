import os
import sys


def get_base_dir():
    """获取基础目录（兼容 PyInstaller 打包）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，资源在临时目录
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(__file__))


# ======================
# 火辣辣设置
# ======================
PET_NAME = "火辣辣"

# 原图250×250，固定显示尺寸
NORMAL_SIZE = 200
CLICK_SIZE = 200
WORK_SIZE = 200

# ======================
# 图片路径
# ======================
BASE_DIR = get_base_dir()
ASSET_DIR = os.path.join(BASE_DIR, "assets")

IMAGES = {
    "idle": os.path.join(ASSET_DIR, "idle.png"),
    "sit": os.path.join(ASSET_DIR, "sit.png"),
    "hello": os.path.join(ASSET_DIR, "hello.png"),
    "happy": os.path.join(ASSET_DIR, "happy.png"),
    "sleep": os.path.join(ASSET_DIR, "sleep.png"),
    "music": os.path.join(ASSET_DIR, "music.png"),
    "keyboard": os.path.join(ASSET_DIR, "keyboard.png"),
}

# ======================
# 数据存储路径（打包后可写）
# ======================
def get_data_dir():
    """获取数据目录（用户可写）"""
    if getattr(sys, 'frozen', False):
        # 打包后，数据保存在 exe 同目录
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(__file__))


DATA_DIR = get_data_dir()

# ======================
# 火辣辣语言库
# ======================
WORDS = {
    "idle": [
        "今天也一起努力吧！",
        "我在这里陪你哦。",
        "今天状态怎么样？",
        "记得喝水。"
    ],
    "keyboard": [
        "你的键盘声音好有节奏。",
        "今天输入好多呀！",
        "努力中的你很帅气。"
    ],
    "music": [
        "这首歌很好听诶。",
        "戴上耳机一起听吧。",
        "音乐时间～"
    ],
    "sleep": [
        "已经很晚啦。",
        "眼睛需要休息一下哦。"
    ],
    "happy": [
        "太棒了！继续加油！",
        "你做得真好！",
        "为你感到开心～"
    ],
    "sit": [
        "休息一下吧。",
        "放松放松。",
        "稍等片刻～"
    ]
}
