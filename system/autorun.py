import os
import sys
import winreg


# 注册表路径
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "HuolalaPet"


def is_auto_start_enabled():
    """检查是否已开启开机自启动"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False


def enable_auto_start():
    """开启开机自启动"""
    try:
        # 获取当前 Python 解释器和脚本路径
        python_exe = sys.executable
        script_path = os.path.abspath(sys.argv[0])
        
        # 如果是打包后的 exe，直接使用 exe 路径
        if script_path.endswith('.exe'):
            command = f'"{script_path}"'
        else:
            command = f'"{python_exe}" "{script_path}"'
        
        # 写入注册表
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"开启开机自启动失败: {e}")
        return False


def disable_auto_start():
    """关闭开机自启动"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"关闭开机自启动失败: {e}")
        return False


def set_auto_start(enabled):
    """设置开机自启动"""
    if enabled:
        return enable_auto_start()
    else:
        return disable_auto_start()
