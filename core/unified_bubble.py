from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLineEdit, QScrollArea, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

from system import task


class UnifiedBubble(QWidget):
    """统一气泡 - 合并音乐显示和任务管理"""

    task_finished = pyqtSignal(int)
    task_deleted = pyqtSignal(int)
    task_edited = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()  # 初始隐藏，避免闪现

        self._task_widgets = []
        self._current_tasks = []
        self._music_text = None
        self._pet = None

        self.setStyleSheet("""
            QWidget#bubble {
                background: white;
                border-radius: 20px;
                border: 2px solid #ffb3c6;
            }
            QLabel#musicLabel {
                color: #ff6b8a;
                font-size: 18px;
                font-family: "Microsoft YaHei", "微软雅黑";
                font-weight: bold;
                padding: 10px 14px;
                background: linear-gradient(135deg, #fff5f7 0%, #ffe8ef 100%);
                border-radius: 12px;
            }
            QLabel#taskTitle {
                color: #333;
                font-size: 18px;
                font-family: "Microsoft YaHei", "微软雅黑";
                font-weight: 500;
                padding: 8px 12px;
            }
            QLabel#doneTitle {
                color: #bbb;
                font-size: 18px;
                font-family: "Microsoft YaHei", "微软雅黑";
                padding: 8px 12px;
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
                min-width: 36px;
                min-height: 36px;
            }
            QPushButton#checkBtn:hover {
                background: #ff85a1;
            }
            QPushButton#editBtn {
                background: transparent;
                color: #aaa;
                border: none;
                font-size: 16px;
                padding: 4px 6px;
                min-width: 28px;
                min-height: 28px;
                border-radius: 6px;
            }
            QPushButton#editBtn:hover {
                color: #ff9fb5;
                background: #fff0f3;
            }
            QPushButton#delBtn {
                background: transparent;
                color: #ccc;
                border: none;
                font-size: 18px;
                padding: 4px 8px;
                min-width: 28px;
                min-height: 28px;
                border-radius: 6px;
            }
            QPushButton#delBtn:hover {
                color: #ff6b6b;
                background: #ffe8e8;
            }
            QLabel#titleLabel {
                color: #ff6b8a;
                font-size: 17px;
                font-weight: bold;
                padding: 8px;
                background: #fff5f7;
                border-radius: 10px;
            }
            QLineEdit#addInput {
                background: #fff8fa;
                border: 2px solid #ffd1dc;
                border-radius: 12px;
                padding: 8px 14px;
                font-size: 16px;
                font-family: "Microsoft YaHei", "微软雅黑";
                color: #333;
                selection-background-color: #ffb3c6;
            }
            QLineEdit#addInput:focus {
                border-color: #ff9fb5;
            }
            QPushButton#addBtn {
                background: #ff9fb5;
                color: white;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                min-width: 44px;
            }
            QPushButton#addBtn:hover {
                background: #ff85a1;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QWidget#taskContainer {
                background: transparent;
            }
        """)

        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 6, 8, 6)

        self.container = QWidget()
        self.container.setObjectName("bubble")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(14, 10, 14, 10)
        container_layout.setSpacing(8)

        # 音乐显示区域
        self.music_label = QLabel()
        self.music_label.setObjectName("musicLabel")
        self.music_label.setAlignment(Qt.AlignCenter)
        self.music_label.setWordWrap(True)
        self.music_label.setMinimumWidth(200)
        self.music_label.hide()
        container_layout.addWidget(self.music_label)

        # 分割线（音乐和任务之间）
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setStyleSheet("color: #ffe0e8; max-height: 1px;")
        self.separator.hide()
        container_layout.addWidget(self.separator)

        # 任务区域容器（包含标题和滚动区）
        self.task_section = QWidget()
        task_section_layout = QVBoxLayout()
        task_section_layout.setContentsMargins(0, 0, 0, 0)
        task_section_layout.setSpacing(6)

        # 任务计数标题
        self.header = QLabel("📋 今日任务")
        self.header.setObjectName("titleLabel")
        self.header.setAlignment(Qt.AlignCenter)
        task_section_layout.addWidget(self.header)

        # 任务滚动区
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #ffd1dc;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ffb3c6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.task_container = QWidget()
        self.task_container.setObjectName("taskContainer")
        self.task_layout = QVBoxLayout()
        self.task_layout.setSpacing(3)
        self.task_layout.setContentsMargins(2, 4, 4, 4)
        self.task_container.setLayout(self.task_layout)
        self.scroll.setWidget(self.task_container)
        task_section_layout.addWidget(self.scroll, 0)

        self.task_section.setLayout(task_section_layout)
        container_layout.addWidget(self.task_section)

        # 添加任务输入区
        add_layout = QHBoxLayout()
        add_layout.setSpacing(8)

        self.add_input = QLineEdit()
        self.add_input.setObjectName("addInput")
        self.add_input.setPlaceholderText("添加新任务...")
        self.add_input.returnPressed.connect(self._on_add_task)
        add_layout.addWidget(self.add_input, 1)

        self.add_btn = QPushButton("+")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_btn.clicked.connect(self._on_add_task)
        add_layout.addWidget(self.add_btn)

        container_layout.addLayout(add_layout)

        self.container.setLayout(container_layout)
        main_layout.addWidget(self.container)

        self.setLayout(main_layout)

    # ======================
    # 音乐显示
    # ======================
    def show_music(self, text):
        """显示音乐信息"""
        self._music_text = text
        self.music_label.setText(text)
        self.music_label.show()
        self._update_separator()
        self._refresh_all()

    def hide_music(self):
        """隐藏音乐显示"""
        self._music_text = None
        self.music_label.hide()
        self._update_separator()
        self._refresh_all()

    def update_music(self, text):
        """更新音乐显示"""
        if self._music_text != text:
            self.show_music(text)

    def _update_separator(self):
        """更新分割线显示"""
        has_music = self._music_text is not None
        has_tasks_section = self.task_section.isVisible()
        if has_music and has_tasks_section:
            self.separator.show()
        else:
            self.separator.hide()

    # ======================
    # 任务管理
    # ======================
    def _get_visible_tasks(self):
        """获取可见的任务（排除全部完成的情况）"""
        tasks = task.get_tasks()
        active = [t for t in tasks if not t["done"]]
        if not active:
            return []
        return tasks

    def update_tasks(self):
        """更新任务显示"""
        self._refresh_all()

    def _refresh_all(self):
        """刷新所有内容"""
        # 清空旧任务
        for widget in self._task_widgets:
            widget.deleteLater()
        self._task_widgets = []

        tasks = task.get_tasks()
        active_count = sum(1 for t in tasks if not t["done"])

        # 没有任务且没有音乐时隐藏
        if not tasks and self._music_text is None:
            self.hide()
            return

        # 没有任务时隐藏任务区域
        if not tasks:
            self.task_section.hide()
        else:
            self.task_section.show()

        # 所有任务完成但有音乐时，仍显示
        if active_count == 0 and tasks:
            self.header.setText("🎉 全部完成啦！")
            for i, t in enumerate(tasks):
                self._add_task_row(i, t, show_edit=False)
        elif tasks:
            done_count = len(tasks) - active_count
            self.header.setText(f"📋 今日任务 ({done_count}/{len(tasks)})")
            for i, t in enumerate(tasks):
                self._add_task_row(i, t, show_edit=True)
        else:
            self.header.setText("📋 还没有任务呢")

        # 根据总任务数量动态调整滚动区高度
        total = len(tasks)
        spacing = self.task_layout.spacing()  # 3
        margins = self.task_layout.contentsMargins()  # 2,4,4,4
        row_h = 44
        if self._task_widgets:
            hint_h = self._task_widgets[0].sizeHint().height()
            row_h = max(44, hint_h)

        if total <= 3:
            # 总任务 <= 3 条，完全显示，关闭滚动条，精确计算高度
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            needed_h = row_h * max(total, 1) + spacing * max(total - 1, 0) + margins.top() + margins.bottom()
            sp = self.scroll.sizePolicy()
            sp.setVerticalPolicy(QSizePolicy.Fixed)
            self.scroll.setSizePolicy(sp)
            self.scroll.setFixedHeight(needed_h)
        else:
            # 总任务 > 3 条，固定显示3条的高度，开启滚动条
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            fixed_h = row_h * 3 + spacing * 2 + margins.top() + margins.bottom()
            sp = self.scroll.sizePolicy()
            sp.setVerticalPolicy(QSizePolicy.Fixed)
            self.scroll.setSizePolicy(sp)
            self.scroll.setFixedHeight(fixed_h)

        # 恢复音乐标签可见性（定时器刷新时可能会遮挡）
        if self._music_text is not None:
            self.music_label.show()

        self._update_separator()
        self.adjustSize()
        # 先定位再显示，避免闪现
        if self._pet:
            self.position_above(self._pet.x(), self._pet.y(), self._pet._size)
        self.show()

    def _add_task_row(self, idx, t, show_edit=True):
        """添加一行任务"""
        task_widget = QWidget()
        task_layout = QHBoxLayout()
        task_layout.setContentsMargins(0, 0, 0, 0)
        task_layout.setSpacing(6)

        # 完成按钮
        check_btn = QPushButton("✓" if t["done"] else "○")
        check_btn.setObjectName("checkBtn")
        check_btn.setCheckable(True)
        check_btn.setChecked(t["done"])
        check_btn.setCursor(QCursor(Qt.PointingHandCursor))
        check_btn.clicked.connect(lambda checked, i=idx: self._on_check(checked, i))
        task_layout.addWidget(check_btn)

        # 任务标题（双击编辑）
        title_label = QLabel(t["title"])
        title_label.setObjectName("doneTitle" if t["done"] else "taskTitle")
        title_label.setWordWrap(True)
        title_label.setCursor(QCursor(Qt.PointingHandCursor))
        title_label.mouseDoubleClickEvent = lambda e, i=idx, l=title_label: self._on_edit(i, l)
        task_layout.addWidget(title_label, 1)

        # 编辑按钮
        if show_edit and not t["done"]:
            edit_btn = QPushButton("✎")
            edit_btn.setObjectName("editBtn")
            edit_btn.setCursor(QCursor(Qt.PointingHandCursor))
            edit_btn.setToolTip("编辑任务")
            edit_btn.clicked.connect(lambda _, i=idx, l=title_label: self._on_edit(i, l))
            task_layout.addWidget(edit_btn)

        # 删除按钮
        del_btn = QPushButton("✕")
        del_btn.setObjectName("delBtn")
        del_btn.setCursor(QCursor(Qt.PointingHandCursor))
        del_btn.setToolTip("删除任务")
        del_btn.clicked.connect(lambda _, i=idx: self._on_delete(i))
        task_layout.addWidget(del_btn)

        task_widget.setLayout(task_layout)
        self.task_layout.addWidget(task_widget)
        self._task_widgets.append(task_widget)

    def _on_check(self, checked, idx):
        """点击完成按钮"""
        if checked:
            task.finish(idx)
            self.task_finished.emit(idx)
        else:
            tasks = task.get_tasks()
            if 0 <= idx < len(tasks):
                tasks[idx]["done"] = False
                from system import task as t
                t._save_tasks(tasks)
        self._refresh_all()

    def _on_delete(self, idx):
        """删除任务"""
        task.delete(idx)
        self.task_deleted.emit(idx)
        self._refresh_all()

    def _on_edit(self, idx, label):
        """编辑任务"""
        current_text = label.text().replace("✓ ", "").replace("○ ", "").strip()
        from PyQt5.QtWidgets import QInputDialog
        new_text, ok = QInputDialog.getText(
            self, "编辑任务", "修改任务内容：", text=current_text
        )
        if ok and new_text.strip():
            tasks = task.get_tasks()
            if 0 <= idx < len(tasks):
                tasks[idx]["title"] = new_text.strip()
                from system import task as t
                t._save_tasks(tasks)
                self.task_edited.emit(idx, new_text.strip())
        self._refresh_all()

    def _on_add_task(self):
        """添加新任务"""
        text = self.add_input.text().strip()
        if text:
            task.add_task(text)
            self.add_input.clear()
            self._refresh_all()

    # ======================
    # 定位
    # ======================
    def position_above(self, x, y, pet_width):
        """定位到桌宠上方"""
        self.adjustSize()
        bubble_width = self.width()
        new_x = x + (pet_width - bubble_width) // 2
        new_y = y - self.height() - 20
        self.move(new_x, new_y)
