import random

from PyQt5.QtWidgets import QLabel, QApplication, QMenu, QAction, QInputDialog
from PyQt5.QtCore import Qt, QTimer

from core.animation import Animation
from core.state import StateManager, PetState
from core.unified_bubble import UnifiedBubble
from system import config, task


class Pet(QLabel):
    """桌面宠物类"""

    def __init__(self):
        super().__init__()

        # 当前大小
        self._size = config.NORMAL_SIZE

        # 拖拽位置
        self.drag_position = None

        # 子窗口引用
        self._panel = None
        self._setting = None

        # 隐藏到托盘标志
        self._app_hide_requested = False

        # 窗口设置：无边框、置顶、工具窗口
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        # 透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 动画
        self.animation = Animation(self)

        # 状态管理
        self.state = StateManager()

        # 统一气泡（合并音乐+任务+对话）
        self.bubble = UnifiedBubble()
        self.bubble._pet = self

        # 音乐显示状态
        self.music_showing = False
        self._last_music_text = None

        # 调整窗口大小
        self._resize(self._size)

        # 初始动作
        self.animation.play("idle")

        # 自动状态计时器（每30秒随机切换）
        self.timer = QTimer()
        self.timer.timeout.connect(self.random_idle)
        self.timer.start(30000)

        # 气泡更新定时器（每2秒）
        self.bubble_timer = QTimer()
        self.bubble_timer.timeout.connect(self._update_bubble)
        self.bubble_timer.start(2000)

        # 任务完成时庆祝
        self.bubble.task_finished.connect(self._on_task_finished)
        self.bubble.task_edited.connect(self._on_task_edited)

    # ======================
    # 尺寸管理
    # ======================
    def _resize(self, size):
        """调整宠物大小"""
        self._size = size
        self.resize(size, size)
        self.animation.set_size(size)
        # 重新播放当前状态
        self.animation.play(self.state.get_state())
        # 更新气泡位置
        self._update_bubble()

    def set_size(self, size):
        """外部设置大小"""
        self._resize(size)
        config.NORMAL_SIZE = size

    def get_size(self):
        """获取当前大小"""
        return self._size

    # ======================
    # 自动动作
    # ======================
    def random_idle(self):
        action = random.choice(["idle", "sit"])
        self.change_action(action)

    # ======================
    # 切换动作
    # ======================
    def change_action(self, action):
        self.state.set_state(action)
        self.animation.play(action)

    # ======================
    # 点击事件
    # ======================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录拖拽起始位置
            self.drag_position = event.globalPos() - self.pos()

            # 播放打招呼动画
            self.change_action("hello")

            # 随机对话
            self.say(random.choice([
                "诶？找我吗？",
                "你回来啦～",
                "今天也一起努力吧！",
                "我在这里陪你哦。"
            ]))

    # ======================
    # 拖动事件
    # ======================
    def mouseMoveEvent(self, event):
        if self.drag_position is not None:
            # 计算目标位置
            new_pos = event.globalPos() - self.drag_position
            
            # 获取屏幕可用区域（排除任务栏）
            screen = QApplication.primaryScreen().availableGeometry()
            
            # 限制在屏幕范围内
            x = max(screen.left(), min(new_pos.x(), screen.right() - self._size))
            y = max(screen.top(), min(new_pos.y(), screen.bottom() - self._size))
            
            self.move(x, y)
            # 实时更新气泡位置
            self._update_bubble()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        # 3秒后恢复到空闲状态
        QTimer.singleShot(3000, self._restore_idle)

    def _restore_idle(self):
        self.change_action("idle")

    # ======================
    # 对话/气泡
    # ======================
    def say(self, text):
        """显示临时对话气泡"""
        self.bubble.show_music(text)
        QTimer.singleShot(4000, self._restore_bubble)

    def _restore_bubble(self):
        """恢复气泡到音乐/任务状态"""
        if self.music_showing and self._last_music_text:
            self.bubble.show_music(self._last_music_text)
        else:
            self.bubble._refresh_all()

    def show_music(self, text):
        """显示音乐信息（持续显示直到调用 hide_music）"""
        self.music_showing = True
        self._last_music_text = text
        self.bubble.show_music(text)

    def hide_music(self):
        """隐藏音乐显示"""
        self.music_showing = False
        self._last_music_text = None
        self.bubble.hide_music()

    def update_music(self, text):
        """更新音乐显示内容"""
        if self.music_showing:
            self._last_music_text = text
            self.bubble.update_music(text)

    def _update_bubble(self):
        """更新气泡位置和内容"""
        if not self.isVisible():
            return
        self.bubble.update_tasks()
        if self.bubble.isVisible():
            self.bubble.position_above(self.x(), self.y(), self._size)

    # ======================
    # 任务事件
    # ======================
    def _on_task_finished(self, idx):
        """任务完成时庆祝"""
        self.change_action("happy")
        
        # 检查是否所有任务都完成了
        tasks = task.get_tasks()
        all_done = all(t["done"] for t in tasks)
        
        if all_done:
            # 全部完成 - 特别庆祝
            self.say(random.choice([
                "🎉 太棒了！所有任务都完成啦！",
                "🎊 你真是太棒了！全部完成！",
                "✨ 完美！今天的任务都搞定了！",
                "🏆 恭喜你！完成所有任务！"
            ]))
        else:
            # 完成单个任务
            remaining = len([t for t in tasks if not t["done"]])
            self.say(random.choice([
                "太棒了！完成一个任务！",
                "你做得真好！",
                "为你感到开心～",
                "继续加油！",
                f"好耶！还剩 {remaining} 个任务～",
                "厉害厉害！",
                "一小步一小步地在进步呢～"
            ]))

    def _on_task_edited(self, idx, new_text):
        """任务编辑时"""
        self.say(f"已修改任务：{new_text}")

    # ======================
    # 右键菜单
    # ======================
    def contextMenuEvent(self, event):
        menu = QMenu(self)

        task_menu = menu.addMenu("📋 任务")

        # 添加任务
        add_action = QAction("➕ 添加任务", self)
        add_action.triggered.connect(self._add_task)
        task_menu.addAction(add_action)

        # 查看所有任务
        view_action = QAction("📝 查看所有任务", self)
        view_action.triggered.connect(self._show_all_tasks)
        task_menu.addAction(view_action)

        menu.addSeparator()

        report_action = QAction("📊 今日报告", self)
        setting_action = QAction("⚙ 设置", self)
        hide_action = QAction("📥 隐藏到托盘", self)
        quit_action = QAction("❌ 退出火辣辣", self)

        def open_panel():
            from ui.panel import Panel
            if self._panel is None:
                self._panel = Panel()
            # 恢复任务栏显示并刷新数据
            self._panel.setWindowFlags(Qt.Window)
            self._panel.update_data()
            self._panel.show()
            self._panel.raise_()

        def open_setting():
            from ui.setting import Setting
            if self._setting is None:
                self._setting = Setting(self._size)
                self._setting.size_changed.connect(self.set_size)
            self._setting.setWindowFlags(Qt.Window)
            self._setting.slider.setValue(self._size)
            self._setting.show()
            self._setting.raise_()

        def hide_to_tray():
            """隐藏到系统托盘"""
            # 停止定时器防止隐藏后仍更新导致崩溃
            self.bubble_timer.stop()
            self.timer.stop()
            self.hide()
            self.bubble.hide()
            if self._panel:
                self._panel.hide()
                # 移除任务栏条目
                self._panel.setWindowFlags(Qt.Tool)
                self._panel.show()
                self._panel.hide()
            if self._setting:
                self._setting.hide()
                self._setting.setWindowFlags(Qt.Tool)
                self._setting.show()
                self._setting.hide()
            self._app_hide_requested = True

        def quit_app():
            """安全退出"""
            from monitor import keyboard, mouse, music
            keyboard.stop()
            mouse.stop()
            music.stop()
            QApplication.quit()

        report_action.triggered.connect(open_panel)
        setting_action.triggered.connect(open_setting)
        hide_action.triggered.connect(hide_to_tray)
        quit_action.triggered.connect(quit_app)

        menu.addAction(report_action)
        menu.addAction(setting_action)
        menu.addAction(hide_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        menu.exec_(event.globalPos())

    def _add_task(self):
        """添加新任务对话框"""
        title, ok = QInputDialog.getText(
            self, "添加任务", "请输入任务内容："
        )
        if ok and title.strip():
            task.add_task(title.strip())
            self._update_bubble()
            self.say("好的，我记住了这个任务！")

    def _show_all_tasks(self):
        """显示所有任务"""
        tasks = task.get_tasks()
        if not tasks:
            self.say("暂时没有任务哦～")
            return

        text = "📋 今日任务：\n"
        for t in tasks:
            status = "✅" if t["done"] else "⬜"
            text += f"  {status} {t['title']}"

        self.bubble.show_music(text)
        QTimer.singleShot(5000, self._restore_bubble)
