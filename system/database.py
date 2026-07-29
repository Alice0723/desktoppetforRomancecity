import sqlite3
import os
from datetime import datetime

from system.config import DATA_DIR

# 数据库路径：数据目录（打包后为 exe 同目录）
DB_PATH = os.path.join(DATA_DIR, "huolala.db")


def connect():
    """连接数据库"""
    return sqlite3.connect(DB_PATH)


def init():
    """初始化数据库表"""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily(
            date TEXT PRIMARY KEY,
            words INTEGER,
            mouse INTEGER,
            clicks INTEGER
        )
    """)
    conn.commit()
    conn.close()


def save(words, mouse, clicks):
    """保存每日数据"""
    conn = connect()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT OR REPLACE INTO daily
        VALUES(?,?,?,?)
    """, (today, words, mouse, clicks))
    conn.commit()
    conn.close()


def get_today():
    """获取今日数据"""
    conn = connect()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT * FROM daily WHERE date=?", (today,))
    result = cursor.fetchone()
    conn.close()
    return result
