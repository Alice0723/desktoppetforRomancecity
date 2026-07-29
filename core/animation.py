import os
import warnings

# 抑制 libpng 警告
warnings.filterwarnings("ignore")
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.png.*=false"

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from system import config


class Animation:
    """动画管理器，负责加载和显示宠物图片"""

    def __init__(self, label):
        self.label = label
        self.size = config.NORMAL_SIZE

    def set_size(self, size):
        """设置显示尺寸"""
        self.size = size

    def play(self, state):
        """播放指定状态的动画图片"""
        if state not in config.IMAGES:
            return

        path = config.IMAGES[state]

        # 检查文件是否存在
        if not os.path.exists(path):
            print(f"图片不存在: {path}")
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"图片加载失败: {path}")
            return

        # 缩放图片
        pixmap = pixmap.scaled(
            self.size,
            self.size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.label.setPixmap(pixmap)
