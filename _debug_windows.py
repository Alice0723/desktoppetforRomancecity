import psutil
import win32gui
import win32process

# Find QQ音乐 PID
qq_pids = []
for proc in psutil.process_iter(['pid', 'name']):
    try:
        name = (proc.info['name'] or '').lower()
        if 'qqmusic' in name:
            qq_pids.append(proc.info['pid'])
            print(f'找到 QQ音乐进程: PID={proc.info["pid"]} Name={proc.info["name"]}')
    except Exception as e:
        pass

# Find windows for those PIDs
def cb(hwnd, _):
    if not win32gui.IsWindow(hwnd):
        return
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in qq_pids:
            title = win32gui.GetWindowText(hwnd)
            visible = win32gui.IsWindowVisible(hwnd)
            print(f'HWND={hwnd} PID={pid} Visible={visible} Title={repr(title)}')
    except Exception:
        pass

if qq_pids:
    win32gui.EnumWindows(cb, None)
else:
    print('未找到 QQ音乐进程')