# 🔥 火辣辣桌宠

> 一个可爱的桌面宠物，陪你学习、工作、音乐，记录你的每一天

<p align="center">
  <img src="assets/idle.png" width="120" alt="idle">
  <img src="assets/happy.png" width="120" alt="happy">
  <img src="assets/music.png" width="120" alt="music">
  <img src="assets/sleep.png" width="120" alt="sleep">
</p>

<p align="center">
  <em>键盘、鼠标、音乐、任务——它都能感知你的状态</em>
</p>

---

## ✨ 特色功能

- 🎭 **智能状态切换** - 空闲、打字、听音乐、睡觉，自动感知你的行为
- 📝 **任务管理** - 添加、完成、删除任务，全在桌宠头顶一键操作
- 🎵 **音乐识别** - 播放音乐时自动显示歌名和艺术家
- 📊 **今日报告** - 统计键盘、鼠标数据，找出你今日最常按的键
- 🌙 **深夜提醒** - 23点后自动进入睡眠状态提醒休息
- 🖱 **拖拽移动** - 鼠标拖动自由放置，滚轮缩放大小
- 🚀 **开机自启** - 设置中一键开启，电脑启动自动运行

---

## 🛠 安装与运行

### 环境要求

- Python 3.10+
- Windows 操作系统

### 安装依赖

```bash
pip install PyQt5 pynput
```

### 运行

```bash
python main.py
```

### 打包成 exe

双击运行 `build.bat`，或手动执行：

```bash
pyinstaller --noconsole --onefile --name "火辣辣桌宠" --add-data "assets;assets" --collect-all pynput main.py
```

---

## 🎮 使用指南

### 基本操作

| 操作 | 说明 |
|------|------|
| 左键点击 | 触发开心动画 |
| 拖拽 | 移动桌宠位置 |
| 滚轮 | 缩放桌宠大小 |
| 右键 | 打开菜单（设置、报告、退出） |

### 任务管理

- **添加任务**：在桌宠头顶的输入框输入任务内容，回车或点击 `+`
- **完成任务**：点击任务左侧的 `○` 变成 `✓`
- **编辑任务**：点击任务右侧的 `✎` 编辑按钮
- **删除任务**：点击任务右侧的 `✕` 删除按钮

### 设置面板

右键 → ⚙ 设置，可以：
- 调整桌宠大小（80-300 像素）
- 开启/关闭开机自启

---

## 📁 项目结构

```
桌宠/
├── main.py                 # 入口文件
├── build.bat               # 打包脚本
├── assets/                 # 图片资源
│   ├── idle.png           # 空闲状态
│   ├── happy.png          # 开心状态
│   ├── music.png          # 音乐状态
│   ├── keyboard.png       # 打字状态
│   ├── sleep.png          # 睡眠状态
│   ├── sit.png            # 坐姿
│   └── hello.png          # 打招呼
├── core/                   # 核心模块
│   ├── pet.py             # 宠物主体
│   ├── state.py           # 状态管理
│   ├── animation.py       # 动画控制
│   ├── bubble.py          # 对话气泡
│   └── unified_bubble.py  # 统一气泡（音乐+任务）
├── monitor/                # 监控模块
│   ├── keyboard.py        # 键盘监听
│   ├── mouse.py           # 鼠标监听
│   └── music.py           # 音乐检测
├── system/                 # 系统模块
│   ├── config.py          # 配置文件
│   ├── database.py        # 数据库
│   ├── task.py            # 任务管理
│   └── autorun.py         # 开机自启
└── ui/                     # 界面模块
    ├── panel.py           # 今日报告
    └── setting.py         # 设置面板
```

---

## 🖼 截图

<p align="center">
  <img src="assets/idle.png" width="200" alt="screenshot1">
  <img src="assets/music.png" width="200" alt="screenshot2">
</p>

---

## 🔧 技术栈

- **Python 3** - 编程语言
- **PyQt5** - GUI 框架
- **pynput** - 键盘鼠标监听
- **sqlite3** - 数据持久化

---

## 📄 许可证

本项目仅供个人娱乐学习交流使用，不得商用。
任何问题可联系🍠@明耀九粥

---

## 🙏 致谢

感谢使用火辣辣桌宠！希望它能陪你度过美好的每一天 💕
