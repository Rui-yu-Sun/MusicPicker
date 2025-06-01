# 歌曲筛选复制工具

一个基于 Python Tkinter 的图形界面工具，用于根据歌曲列表从本地音乐库中筛选并复制指定的音乐文件。

## 功能特点

- ? 图形界面操作，简单易用
- ? 支持多种音频格式（MP3, FLAC, WAV, M4A, AAC, OGG）
- ? 智能匹配歌曲名和艺术家
- ? 实时日志显示处理过程
- ?? 支持中途停止操作
- ? 进度显示

## 安装要求

- Python 3.6+
- tkinter（通常随 Python 自带）

## 使用方法

1. 运行程序：
   ```bash
   python ListPick_Copy.py
   ```

2. 选择歌曲列表文件（格式：`歌曲名 - 艺术家`，每行一首）
3. 选择本地音乐库文件夹
4. 选择输出文件夹
5. 点击"开始筛选复制"

## 歌曲列表格式

创建一个 `.txt` 文件，每行按以下格式书写：
```
歌曲名 - 艺术家
例如：
告白气球 - 周杰伦
演员 - 薛之谦
```

## 生成可执行文件

使用 PyInstaller 生成 exe 文件：
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="歌曲筛选复制工具" ListPick_Copy.py
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！