class PetState:
    """宠物状态常量"""
    IDLE = "idle"
    SIT = "sit"
    HELLO = "hello"
    HAPPY = "happy"
    SLEEP = "sleep"
    MUSIC = "music"
    KEYBOARD = "keyboard"


class StateManager:
    """状态管理器"""

    def __init__(self):
        self.current = PetState.IDLE

    def set_state(self, state):
        """设置当前状态"""
        self.current = state

    def get_state(self):
        """获取当前状态"""
        return self.current
