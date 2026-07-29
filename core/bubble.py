from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class Bubble(QLabel):
    """聊天气泡组件"""

    def __init__(self):
        super().__init__()

        # 设置窗口属性：工具窗口 + 无边框 + 置顶
        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        # 启用文字选择（方便复制）
        self.setTextInteractionFlags(Qt.NoTextInteraction)

        # 设置样式 - 更大字体，更清晰
        self.setStyleSheet("""
            QLabel {
                background: white;
                color: #333;
                border-radius: 18px;
                padding: 16px 20px;
                font-size: 18px;
                font-family: "Microsoft YaHei", "微软雅黑";
                font-weight: 500;
                border: 2px solid #ffb3c6;
            }
        """)

        self.hide()

    def show_text(self, text, x, y):
        """显示气泡文字"""
        self.setText(text)
        self._adjust_size()
        self.move(x, y)
        self.show()

    def show_permanent(self, text, x, y):
        """显示持久气泡（不会自动关闭）"""
        self.setText(text)
        self._adjust_size()
        self.move(x, y)
        self.show()

    def update_position(self, x, y):
        """更新气泡位置"""
        if self.isVisible():
            self.move(x, y)

    def _adjust_size(self):
        """调整气泡大小"""
        self.adjustSize()
        max_width = 350
        if self.width() > max_width:
            self.setFixedWidth(max_width)
            self.setWordWrap(True)
            self.adjustSize()

    def close_bubble(self):
        """隐藏气泡"""
        self.hide()
