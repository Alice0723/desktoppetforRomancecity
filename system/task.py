import json
import os

from system.config import DATA_DIR

# 任务数据文件
TASK_FILE = os.path.join(DATA_DIR, "tasks.json")

def _load_tasks():
    """从文件加载任务"""
    if os.path.exists(TASK_FILE):
        try:
            with open(TASK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_tasks(tasks):
    """保存任务到文件"""
    try:
        with open(TASK_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# 全局任务列表
_tasks = _load_tasks()


def get_tasks():
    """获取任务列表"""
    return _tasks


def add_task(title):
    """添加新任务"""
    _tasks.append({"title": title, "done": False})
    _save_tasks(_tasks)


def finish(index):
    """标记任务为完成"""
    if 0 <= index < len(_tasks):
        _tasks[index]["done"] = True
        _save_tasks(_tasks)


def delete(index):
    """删除任务"""
    if 0 <= index < len(_tasks):
        del _tasks[index]
        _save_tasks(_tasks)


def reset():
    """重置所有任务"""
    global _tasks
    _tasks = []
    _save_tasks(_tasks)


def progress():
    """获取任务进度（已完成数，总数）"""
    total = len(_tasks)
    done = sum(1 for t in _tasks if t["done"])
    return done, total


def get_active_tasks():
    """获取未完成的任务"""
    return [(i, t) for i, t in enumerate(_tasks) if not t["done"]]
