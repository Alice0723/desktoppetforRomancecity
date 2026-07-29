from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QScrollArea
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

from system import task


class TaskBubble(QWidget):
    """头顶任务气泡 - 显示在桌宠上方"""

    task_finished = pyqtSignal(int)
    task_deleted = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WA_TranslucentBackground)

        self._task_widgets = []
        self._current_tasks = []

        self.setStyleSheet("""
            QWidget#bubble {
                background: white;
                border-radius: 18px;
                border: 2px solid #ffb3c6;
            }
            QLabel#taskTitle {
                color: #333;
                font-size: 17px;
                font-family: "Microsoft YaHei", "微软雅黑";
                font-weight: 500;
                padding: 8px 10px;
            }
            QLabel#doneTitle {
                color: #aaa;
                font-size: 17px;
                font-family: "Microsoft YaHei", "微软雅黑";
                padding: 8px 10px;
                text-decoration: line-through;
            }
            QPushButton#checkBtn {
                background: #ff9fb5;
                color: white;
                border-radius: 12px;
                padding: 6px 10px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                min-width: 32px;
                min-height: 32px;
            }
            QPushButton#checkBtn:hover {
                background: #ff85a1;
            }
            QPushButton#checkBtn:checked {
                background: #7cd996;
            }
            QPushButton#delBtn {
                background: transparent;
                color: #ccc;
                border: none;
                font-size: 18px;
                padding: 4px 8px;
                min-width: 24px;
                min-height: 24px;
            }
            QPushButton#delBtn:hover {
                color: #ff6b6b;
                background: #ffe8e8;
                border-radius: 8px;
            }
            QLabel#titleLabel {
                color: #ff6b8a;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                background: #fff5f7;
                border-radius: 10px;
            }
        """)

        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 10, 12, 10)

        self.container = QWidget()
        self.container.setObjectName("bubble")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(12, 8, 12, 8)
        container_layout.setSpacing(6)

        # 任务计数标题
        self.header = QLabel("📋 今日任务")
        self.header.setObjectName("titleLabel")
        self.header.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.header)

        self.task_layout = QVBoxLayout()
        self.task_layout.setSpacing(4)
        container_layout.addLayout(self.task_layout)

        self.container.setLayout(container_layout)
        main_layout.addWidget(self.container)

        self.setLayout(main_layout)

    def update_tasks(self):
        """更新任务显示"""
        # 清空旧任务
        for widget in self._task_widgets:
            widget.deleteLater()
        self._task_widgets = []

        tasks = task.get_tasks()
        if not tasks:
            self.hide()
            return

        # 检查是否所有任务都完成了
        all_done = all(t["done"] for t in tasks)
        if all_done:
            # 所有任务完成，隐藏任务框
            self.hide()
            return

        # 更新标题
        done_count = sum(1 for t in tasks if t["done"])
        self.header.setText(f"📋 今日任务 ({done_count}/{len(tasks)})")

        for i, t in enumerate(tasks):
            task_widget = QWidget()
            task_layout = QHBoxLayout()
            task_layout.setContentsMargins(0, 0, 0, 0)
            task_layout.setSpacing(8)

            # 完成按钮
            check_btn = QPushButton("✓" if t["done"] else "○")
            check_btn.setObjectName("checkBtn")
            check_btn.setCheckable(True)
            check_btn.setChecked(t["done"])
            check_btn.setCursor(QCursor(Qt.PointingHandCursor))
            check_btn.clicked.connect(lambda checked, idx=i: self._on_check(checked, idx))
            task_layout.addWidget(check_btn)

            # 任务标题
            title_label = QLabel(t["title"])
            title_label.setObjectName("doneTitle" if t["done"] else "taskTitle")
            title_label.setWordWrap(True)
            task_layout.addWidget(title_label, 1)

            # 删除按钮
            del_btn = QPushButton("✕")
            del_btn.setObjectName("delBtn")
            del_btn.setCursor(QCursor(Qt.PointingHandCursor))
            del_btn.setToolTip("删除任务")
            del_btn.clicked.connect(lambda _, idx=i: self._on_delete(idx))
            task_layout.addWidget(del_btn)

            task_widget.setLayout(task_layout)
            self.task_layout.addWidget(task_widget)
            self._task_widgets.append(task_widget)

        self._current_tasks = tasks

        # 调整大小
        self.adjustSize()
        self.show()

    def _on_check(self, checked, idx):
        """点击完成按钮"""
        if checked:
            task.finish(idx)
            self.task_finished.emit(idx)
        else:
            # 取消完成
            tasks = task.get_tasks()
            if 0 <= idx < len(tasks):
                tasks[idx]["done"] = False
                from system import task as t
                t._save_tasks(tasks)
        self.update_tasks()

    def _on_delete(self, idx):
        """删除任务"""
        task.delete(idx)
        self.task_deleted.emit(idx)
        self.update_tasks()

    def position_above(self, x, y, pet_width):
        """定位到桌宠上方"""
        self.adjustSize()
        bubble_width = self.width()
        # 居中对齐桌宠
        new_x = x + (pet_width - bubble_width) // 2
        new_y = y - self.height() - 15
        self.move(new_x, new_y)
