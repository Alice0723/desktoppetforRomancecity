from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal

from system import autorun


class Setting(QWidget):
    """设置面板"""

    size_changed = pyqtSignal(int)
    auto_start_changed = pyqtSignal(bool)

    def __init__(self, current_size=200):
        super().__init__()

        self.setWindowTitle("火辣辣设置")
        self.resize(440, 540)
        self.setWindowFlags(self.windowFlags() | Qt.Window)

        self.current_size = current_size

        self.setStyleSheet("""
            QWidget {
                background: #fff5f7;
                border-radius: 20px;
                font-family: "Microsoft YaHei";
            }
            QLabel#title {
                color: #ff6b8a;
                font-size: 26px;
                font-weight: bold;
                padding: 12px;
            }
            QLabel#section {
                color: #888;
                font-size: 20px;
                font-weight: bold;
                margin-top: 18px;
            }
            QLabel#value {
                color: #ff6b8a;
                font-size: 32px;
                font-weight: bold;
            }
            QLabel {
                color: #555;
                font-size: 18px;
            }
            QSlider::groove:horizontal {
                height: 10px;
                background: #ffd1dc;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #ff9fb5;
                width: 24px;
                height: 24px;
                margin: -7px 0;
                border-radius: 12px;
            }
            QPushButton {
                background: #ff9fb5;
                color: white;
                border-radius: 14px;
                padding: 14px 24px;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #ff85a1;
            }
            QCheckBox {
                color: #555;
                font-size: 18px;
                spacing: 12px;
                padding: 6px;
            }
            QCheckBox::indicator {
                width: 26px;
                height: 26px;
                border-radius: 7px;
                border: 2px solid #ffb3c6;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #ff9fb5;
                border-color: #ff85a1;
                image: none;
            }
            QCheckBox::indicator:hover {
                border-color: #ff85a1;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)

        # 标题
        title = QLabel("🔥 火辣辣设置")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 大小调节
        size_section = QLabel("⚙ 桌宠大小")
        size_section.setObjectName("section")
        layout.addWidget(size_section)

        size_layout = QHBoxLayout()

        self.size_value = QLabel(str(self.current_size))
        self.size_value.setObjectName("value")
        self.size_value.setFixedWidth(70)
        size_layout.addWidget(self.size_value)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(80, 300)
        self.slider.setValue(self.current_size)
        self.slider.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(self.slider)

        layout.addLayout(size_layout)

        # 提示
        hint = QLabel("拖动滑块调整桌宠显示尺寸")
        hint.setStyleSheet("color: #aaa; font-size: 15px;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        # 开机自启动
        auto_section = QLabel("🚀 启动设置")
        auto_section.setObjectName("section")
        layout.addWidget(auto_section)

        self.auto_start_box = QCheckBox("开机时自动启动火辣辣")
        self.auto_start_box.setChecked(autorun.is_auto_start_enabled())
        self.auto_start_box.toggled.connect(self.on_auto_start_toggled)
        layout.addWidget(self.auto_start_box)

        # 提示
        auto_hint = QLabel("开启后，下次开机会自动运行")
        auto_hint.setStyleSheet("color: #aaa; font-size: 15px;")
        layout.addWidget(auto_hint)

        # 关于信息
        about_section = QLabel("ℹ 关于")
        about_section.setObjectName("section")
        layout.addWidget(about_section)

        about = QLabel("本桌宠仅供娱乐，不商用，\n任何问题找🍠@明耀九粥")
        about.setAlignment(Qt.AlignCenter)
        about.setStyleSheet("color: #999; font-size: 15px;")
        about.setWordWrap(True)
        layout.addWidget(about)

        # 按钮
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def on_size_changed(self, value):
        """滑块值变化时更新"""
        self.size_value.setText(str(value))
        self.size_changed.emit(value)

    def on_auto_start_toggled(self, checked):
        """开机自启动开关"""
        success = autorun.set_auto_start(checked)
        if success:
            self.auto_start_changed.emit(checked)
        else:
            # 如果失败，恢复原状态
            self.auto_start_box.blockSignals(True)
            self.auto_start_box.setChecked(not checked)
            self.auto_start_box.blockSignals(False)

    def save_and_close(self):
        """保存并关闭"""
        self.hide()

    def closeEvent(self, event):
        """关闭时隐藏而不是退出"""
        event.ignore()
        self.hide()
