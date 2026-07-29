from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from PyQt5.QtCore import Qt

from monitor import keyboard, mouse
from system import task

_MEDAL_ICONS = ["🥇", "🥈", "🥉"]


class Panel(QWidget):
    """今日报告面板"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("火辣辣 - 今日报告")
        self.resize(460, 720)
        self.setWindowFlags(self.windowFlags() | Qt.Window)

        self.setStyleSheet("""
            QWidget {
                background: #fff8fa;
                border-radius: 20px;
                font-family: "Microsoft YaHei";
            }
            QLabel#title {
                color: #ff6b8a;
                font-size: 26px;
                font-weight: bold;
            }
            QLabel#date {
                color: #ffc0cb;
                font-size: 13px;
            }
            QLabel#section {
                color: #ff8fa3;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#value {
                color: #4a4a4a;
                font-size: 28px;
                font-weight: bold;
            }
            QLabel#label {
                color: #bbb;
                font-size: 14px;
            }
            QLabel#num {
                color: #ff6b8a;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#rank_key {
                color: #333;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#rank_count {
                color: #ff99aa;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#rank_empty {
                color: #ddd;
                font-size: 14px;
            }
            QPushButton {
                background: #ffb3c6;
                color: white;
                border-radius: 20px;
                padding: 12px 32px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #ff8fa3;
            }
            QFrame#rankRow {
                background: #fff0f3;
                border-radius: 12px;
                padding: 4px 10px;
            }
            QFrame#rankRow1 {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #fffbe6,stop:1 #fff3cc);
                border-radius: 12px;
                padding: 6px 12px;
                border: 1px solid #ffe680;
            }
            QFrame#rankRow2 {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #fafafa,stop:1 #ededed);
                border-radius: 12px;
                padding: 6px 12px;
                border: 1px solid #d0d0d0;
            }
            QFrame#rankRow3 {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #fff5e8,stop:1 #ffe0bf);
                border-radius: 12px;
                padding: 6px 12px;
                border: 1px solid #d08a4a;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(0)

        # 标题行
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title = QLabel("🔥 今日报告")
        title.setObjectName("title")
        title_row.addWidget(title)

        title_row.addStretch()

        # 日期
        from datetime import datetime
        date_str = datetime.now().strftime("%m月%d日")
        date_label = QLabel(date_str)
        date_label.setObjectName("date")
        title_row.addWidget(date_label)

        layout.addLayout(title_row)

        layout.addSpacing(24)

        # ============ 输入统计 ============
        key_section = QLabel("⌨ 输入")
        key_section.setObjectName("section")
        layout.addWidget(key_section)

        key_row = QHBoxLayout()
        key_row.setSpacing(0)

        key_char_box = QVBoxLayout()
        key_char_box.setSpacing(2)
        key_char_box.addWidget(self._make_value_label("0", "chars"))
        key_char_box.addWidget(self._make_label("字符"))
        key_char_box.setAlignment(Qt.AlignCenter)
        key_row.addLayout(key_char_box)

        sep1 = QLabel("|")
        sep1.setStyleSheet("color: #ffe0e8; font-size: 20px;")
        sep1.setAlignment(Qt.AlignCenter)
        key_row.addWidget(sep1)

        key_key_box = QVBoxLayout()
        key_key_box.setSpacing(2)
        key_key_box.addWidget(self._make_value_label("0", "keys"))
        key_key_box.addWidget(self._make_label("按键"))
        key_key_box.setAlignment(Qt.AlignCenter)
        key_row.addLayout(key_key_box)

        layout.addLayout(key_row)

        layout.addSpacing(20)

        # 分隔点
        dot1 = QLabel("·")
        dot1.setStyleSheet("color: #ffd1dc; font-size: 18px;")
        dot1.setAlignment(Qt.AlignCenter)
        layout.addWidget(dot1)

        layout.addSpacing(12)

        # 今日键王排行榜 - 3行
        topkey_section = QLabel("👑 今日键王排行榜")
        topkey_section.setObjectName("section")
        layout.addWidget(topkey_section)

        # 颁奖榜单 TOP3
        self.rank_container = QWidget()
        self.rank_container.setStyleSheet("background: transparent;")
        self.rank_layout = QVBoxLayout()
        self.rank_layout.setContentsMargins(0, 8, 0, 4)
        self.rank_layout.setSpacing(6)
        self.rank_container.setLayout(self.rank_layout)

        # 创建3个排名行
        self.rank_rows = []
        for i in range(3):
            row = self._make_rank_row(i)
            self.rank_rows.append(row)
            self.rank_layout.addWidget(row["frame"])

        layout.addWidget(self.rank_container)

        layout.addSpacing(12)

        dot2 = QLabel("·")
        dot2.setStyleSheet("color: #ffd1dc; font-size: 18px;")
        dot2.setAlignment(Qt.AlignCenter)
        layout.addWidget(dot2)

        layout.addSpacing(12)

        # ============ 鼠标活动 ============
        mouse_section = QLabel("🖱 鼠标")
        mouse_section.setObjectName("section")
        layout.addWidget(mouse_section)

        mouse_row = QHBoxLayout()
        mouse_row.setSpacing(0)

        mouse_move_box = QVBoxLayout()
        mouse_move_box.setSpacing(2)
        mouse_move_box.addWidget(self._make_value_label("0", "move"))
        mouse_move_box.addWidget(self._make_label("移动"))
        mouse_move_box.setAlignment(Qt.AlignCenter)
        mouse_row.addLayout(mouse_move_box)

        sep2 = QLabel("|")
        sep2.setStyleSheet("color: #ffe0e8; font-size: 20px;")
        sep2.setAlignment(Qt.AlignCenter)
        mouse_row.addWidget(sep2)

        mouse_click_box = QVBoxLayout()
        mouse_click_box.setSpacing(2)
        mouse_click_box.addWidget(self._make_value_label("0", "click"))
        mouse_click_box.addWidget(self._make_label("点击"))
        mouse_click_box.setAlignment(Qt.AlignCenter)
        mouse_row.addLayout(mouse_click_box)

        sep3 = QLabel("|")
        sep3.setStyleSheet("color: #ffe0e8; font-size: 20px;")
        sep3.setAlignment(Qt.AlignCenter)
        mouse_row.addWidget(sep3)

        mouse_scroll_box = QVBoxLayout()
        mouse_scroll_box.setSpacing(2)
        mouse_scroll_box.addWidget(self._make_value_label("0", "scroll"))
        mouse_scroll_box.addWidget(self._make_label("滚轮"))
        mouse_scroll_box.setAlignment(Qt.AlignCenter)
        mouse_row.addLayout(mouse_scroll_box)

        layout.addLayout(mouse_row)

        layout.addSpacing(20)

        dot3 = QLabel("·")
        dot3.setStyleSheet("color: #ffd1dc; font-size: 18px;")
        dot3.setAlignment(Qt.AlignCenter)
        layout.addWidget(dot3)

        layout.addSpacing(12)

        # ============ 今日任务 ============
        task_section = QLabel("📋 今日任务")
        task_section.setObjectName("section")
        layout.addWidget(task_section)

        self.task_info = QLabel()
        self.task_info.setAlignment(Qt.AlignCenter)
        self.task_info.setStyleSheet(
            "color: #ff6b8a; font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(self.task_info)

        layout.addStretch()

        # 按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.update_data)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.update_data()

    def _make_label(self, text):
        label = QLabel(text)
        label.setObjectName("label")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _make_value_label(self, text, attr):
        label = QLabel(text)
        label.setObjectName("value")
        label.setAlignment(Qt.AlignCenter)
        self.setProperty(attr, label)
        return label

    def _make_rank_row(self, index):
        """创建颁奖榜单中的一行"""
        # 行容器
        frame = QFrame()
        frame.setObjectName("rankRow")
        if index == 0:
            frame.setObjectName("rankRow1")
        elif index == 1:
            frame.setObjectName("rankRow2")
        elif index == 2:
            frame.setObjectName("rankRow3")

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(10, 6, 10, 6)
        row_layout.setSpacing(10)

        # 奖牌/排名图标
        rank_label = QLabel(_MEDAL_ICONS[index])
        rank_label.setAlignment(Qt.AlignCenter)
        rank_label.setFixedWidth(36)
        rank_label.setStyleSheet(
            "font-size: 20px;"
        )
        row_layout.addWidget(rank_label)

        # 按键名称
        key_label = QLabel("—")
        key_label.setObjectName("rank_empty")
        key_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        key_label.setStyleSheet(
            "color: #ddd; font-size: 15px;"
        )
        row_layout.addWidget(key_label, 1)

        # 次数
        count_label = QLabel("")
        count_label.setObjectName("rank_count")
        count_label.setAlignment(Qt.AlignCenter)
        count_label.setFixedWidth(80)
        row_layout.addWidget(count_label)

        frame.setLayout(row_layout)

        return {
            "frame": frame,
            "rank": rank_label,
            "key": key_label,
            "count": count_label,
        }

    def update_data(self):
        """更新显示数据"""
        key_data = keyboard.get_data()
        mouse_data = mouse.get_data()
        done, total = task.progress()

        self.property("chars").setText(str(key_data['chars']))
        self.property("keys").setText(str(key_data['keys']))
        self.property("move").setText(str(mouse_data['move']))
        self.property("click").setText(str(mouse_data['click']))
        self.property("scroll").setText(str(mouse_data['scroll']))

        # 任务
        if total > 0:
            pct = int(done / total * 100)
            self.task_info.setText(f"{done}/{total}  ({pct}%)")
        else:
            self.task_info.setText("还没有任务～")

        # 今日键王 TOP3
        if key_data['top_key'] != "无":
            self._update_top3(key_data['top5'])
        else:
            self._update_top3([])

    def _update_top3(self, top5):
        """更新颁奖榜单 TOP3"""
        for i in range(3):
            row = self.rank_rows[i]
            if i < len(top5):
                key_name, count = top5[i]
                row["key"].setText(key_name)
                row["key"].setObjectName("rank_key")
                row["key"].setStyleSheet("color: #333; font-size: 16px; font-weight: bold;")
                row["count"].setText(f"{count} 次")
                row["count"].setObjectName("rank_count")
                row["count"].setStyleSheet(
                    "color: #ff99aa; font-size: 14px; font-weight: bold;"
                )
            else:
                row["key"].setText("—")
                row["key"].setObjectName("rank_empty")
                row["key"].setStyleSheet("color: #ddd; font-size: 15px;")
                row["count"].setText("")

    def closeEvent(self, event):
        """关闭时隐藏而不是退出"""
        event.ignore()
        self.hide()
