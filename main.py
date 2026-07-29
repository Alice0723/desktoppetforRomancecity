import sys
import random
import time

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QFontMetrics

from core.pet import Pet
from monitor import keyboard, mouse, music
from system import database
from system import config
from system import task


# ==========================
# 初始化
# ==========================
app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

# 初始化数据库
database.init()

# 开启监听
keyboard.start()
mouse.start()
music.start()


# ==========================
# 火辣辣
# ==========================
pet = Pet()

screen = app.desktop().availableGeometry()
pet.move(screen.width() - 250, screen.height() - 250)
pet.show()


# ==========================
# 系统托盘
# ==========================
def create_tray_icon():
    """创建托盘图标"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # 画一个圆形图标
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#ff9fb5"))
    painter.drawEllipse(4, 4, 56, 56)

    # 画表情
    painter.setPen(QColor("#ff6b8a"))
    painter.setFont(QFont("Segoe UI Emoji", 28))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "🐾")
    painter.end()
    return QIcon(pixmap)


tray_icon = QSystemTrayIcon(create_tray_icon())
tray_icon.setToolTip("火辣辣桌宠")

# 托盘菜单
tray_menu = QMenu()

show_action = QAction("🐾 显示桌宠", tray_icon)
show_action.triggered.connect(lambda: show_pet_from_tray())

tray_report_action = QAction("📊 今日报告", tray_icon)
tray_report_action.triggered.connect(lambda: open_report_panel())

tray_quit_action = QAction("❌ 退出", tray_icon)
tray_quit_action.triggered.connect(lambda: quit_app())

tray_menu.addAction(show_action)
tray_menu.addSeparator()
tray_menu.addAction(tray_report_action)
tray_menu.addSeparator()
tray_menu.addAction(tray_quit_action)

tray_icon.setContextMenu(tray_menu)


def show_pet_from_tray():
    """从托盘显示桌宠"""
    pet.show()
    pet.raise_()
    pet.activateWindow()
    tray_icon.hide()
    pet._app_hide_requested = False
    # 恢复定时器
    pet.bubble_timer.start(2000)
    pet.timer.start(30000)
    # 恢复面板和设置窗口的任务栏显示
    if pet._panel:
        pet._panel.setWindowFlags(Qt.Window)
        pet._panel.show()
        pet._panel.hide()
    if pet._setting:
        pet._setting.setWindowFlags(Qt.Window)
        pet._setting.show()
        pet._setting.hide()
    # 立即更新气泡
    pet._update_bubble()


def open_report_panel():
    """打开今日报告"""
    from ui.panel import Panel
    if pet._panel is None:
        pet._panel = Panel()
    pet._panel.setWindowFlags(Qt.Window)
    pet._panel.update_data()
    pet._panel.show()
    pet._panel.raise_()
    pet._panel.activateWindow()


def quit_app():
    """安全退出"""
    keyboard.stop()
    mouse.stop()
    music.stop()
    tray_icon.hide()
    QApplication.quit()


# 左键点击托盘图标显示/隐藏
tray_icon.activated.connect(
    lambda reason: show_pet_from_tray()
    if reason == QSystemTrayIcon.Trigger
    else None
)


# ==========================
# 状态联动逻辑
# ==========================
def update_pet_state():
    """根据用户活动更新宠物状态"""
    # 检查是否需要隐藏到托盘
    if getattr(pet, '_app_hide_requested', False):
        pet._app_hide_requested = False
        tray_icon.show()
        tray_icon.showMessage(
            "火辣辣桌宠",
            "已隐藏到系统托盘，点击图标可重新显示",
            QSystemTrayIcon.Information,
            2000
        )
        return

    # 如果桌宠已隐藏，跳过状态更新
    if not pet.isVisible():
        return

    current_state = pet.state.get_state()
    hour = time.localtime().tm_hour
    is_night = hour >= 23 or hour < 6

    # 优先检测：音乐播放（即使深夜也优先处理音乐）
    if music.is_playing():
        music_info = music.get_music()
        if current_state != "music":
            pet.change_action("music")
        
        # 持续显示音乐信息
        if music_info["title"] != "暂无播放":
            artist = music_info.get("artist", "")
            if artist and artist not in ("", "未知", "音乐播放中"):
                music_text = f"♪ {music_info['title']}\n{artist}"
            else:
                music_text = f"♪ {music_info['title']}"
            
            # 首次显示或更新内容
            if not pet.music_showing:
                pet.show_music(music_text)
            elif pet._last_music_text != music_text:
                pet.update_music(music_text)
        else:
            if not pet.music_showing:
                pet.show_music(random_choice("music"))
        return

    # 没有播放音乐，关闭音乐显示
    if pet.music_showing:
        pet.hide_music()

    # 深夜模式（不播放音乐时才生效）
    if is_night:
        if current_state not in ("sleep", "idle", "sit"):
            pet.change_action("sleep")
        return

    # 键盘输入中
    if keyboard.is_typing():
        if current_state != "keyboard":
            pet.change_action("keyboard")
            pet.say(random_choice("keyboard"))
        return

    # 如果没有活动，恢复 idle
    if current_state not in ("idle", "sit", "hello"):
        pet.change_action("idle")


def random_choice(category):
    """从语言库中随机选择一句话"""
    words = config.WORDS.get(category, config.WORDS.get("idle", ["..."]))
    return random.choice(words)


# 状态检查定时器（每3秒检查一次）
state_timer = QTimer()
state_timer.timeout.connect(update_pet_state)
state_timer.start(3000)


# ==========================
# 定时保存（每分钟）
# ==========================
def save_data():
    key_data = keyboard.get_data()
    mouse_data = mouse.get_data()
    database.save(key_data["chars"], mouse_data["move"], mouse_data["click"])


save_timer = QTimer()
save_timer.timeout.connect(save_data)
save_timer.start(60000)


# ==========================
# 运行
# ==========================
sys.exit(app.exec_())