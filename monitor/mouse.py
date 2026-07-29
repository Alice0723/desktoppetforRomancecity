_mouse = None  # 延迟导入


# =====================
# 数据统计
# =====================
move_count = 0
click_count = 0
scroll_count = 0
_listener = None


# =====================
# 回调函数
# =====================
def on_move(x, y):
    """鼠标移动回调"""
    global move_count
    move_count += 1


def on_click(x, y, button, pressed):
    """鼠标点击回调"""
    global click_count
    if pressed:
        click_count += 1


def on_scroll(x, y, dx, dy):
    """鼠标滚轮回调"""
    global scroll_count
    scroll_count += 1


# =====================
# 控制函数
# =====================
def start():
    """启动鼠标监听"""
    global _listener, _mouse
    if _mouse is None:
        try:
            from pynput import mouse as _mouse
        except Exception as e:
            print(f"[鼠标监听] 启动失败: {e}")
            return
    try:
        _listener = _mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll
        )
        _listener.start()
    except Exception as e:
        print(f"[鼠标监听] 启动监听失败: {e}")


def stop():
    """停止鼠标监听"""
    global _listener
    if _listener:
        _listener.stop()
        _listener = None


def get_data():
    """获取鼠标统计数据"""
    return {
        "move": move_count,
        "click": click_count,
        "scroll": scroll_count
    }
