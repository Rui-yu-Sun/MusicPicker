# MusicPicker - 歌曲筛选复制工具

## 💡 项目初衷

### 🎧 音乐平台迁移的现实挑战

在数字音乐时代，我们经常面临这样的困扰：当需要更换音乐平台时（比如从网易云音乐切换到 Spotify，或从 QQ 音乐转向 Apple Music），如何将珍藏多年的歌单完整地迁移过去？

**传统迁移方案的局限性：**

🔒 **在线迁移工具的瓶颈**  
虽然市面上有一些优秀的歌单迁移服务（如 [TunemyMusic](https://www.tunemymusic.com)、[Spotlistr](https://spotlistr.com/)），但在实际使用中往往受限于：
- **版权壁垒** - 不同平台间的版权差异导致部分歌曲无法匹配
- **曲库差异** - 独立音乐人、小众歌曲在某些平台缺失
- **识别错误** - 自动匹配算法可能出现同名不同曲、版本混淆等问题

💔 **手动重建的痛苦**  
对于拥有**数千首收藏歌曲**的资深乐迷来说，逐一搜索添加缺失歌曲几乎是不可能完成的任务。更糟糕的是，一些珍贵的现场版本、混音版本、或者已经下架的歌曲可能永远找不回来。

### 🚀 MusicPicker 的解决方案

如果你是一个习惯收集本地音乐文件的用户，那么你已经拥有了最完整、最高质量的音乐库。**MusicPicker** 提供了一个更优雅的迁移思路：

> **🎯 核心理念：** 
> 1. **获取歌单列表** - 通过 [GoMusic](https://github.com/Bistutu/GoMusic) 等工具从任意平台导出歌单
> 2. **智能文件匹配** - 从本地音乐库中精准定位对应的音频文件  
> 3. **批量导入同步** - 利用音乐平台的本地导入和云同步功能，实现完美迁移

### 🌟 实际应用价值

**MusicPicker** 特别适合以下场景：

🏠 **本地音乐库管理者**  
如果你拥有精心整理的本地音乐收藏（无损格式、珍稀版本、自制精选集），这个工具能帮你快速构建新平台的歌单基础。

🔄 **多平台用户**  
在 Apple Music、Spotify、网易云等多个平台间切换时，无需重复搜索添加，一键复制即可。

📱 **设备同步需求**  
通过各平台的云同步机制（如 iTunes Match、Spotify Connect），实现从电脑到手机、平板等所有设备的无缝音乐体验。

💎 **音质追求者**  
保持原有的高品质音频文件，而不是依赖平台的在线音质（可能被压缩）。

**MusicPicker** 让音乐平台迁移变得简单高效：
- 📋 **批量处理** - 一次性处理数千首歌曲的匹配和复制
- 🎯 **智能匹配** - 模糊算法应对各种文件命名差异和格式变化  
- 📁 **即插即用** - 匹配结果直接复制到目标文件夹，便于批量导入
- 🚀 **效率提升** - 将数小时的手动工作缩短为几分钟的自动化处理

## 🎵 功能特点

- 🖥️ **图形界面操作** - 简单直观的GUI界面，无需命令行操作
- 🎯 **智能模糊匹配** - 包含式匹配算法，应对各种文件命名差异和格式变化
- 🎧 **多格式支持** - 支持 MP3、FLAC、WAV、M4A、AAC、OGG 等主流音频格式
- 📋 **歌单快速导入** - 完美兼容 [GoMusic](https://music.unmeta.cn) 等工具生成的歌单格式
- 📝 **实时处理日志** - 详细显示匹配过程，便于跟踪和问题排查
- 📊 **进度可视化** - 实时显示处理进度和完成百分比
- ⏹️ **随时中断** - 支持处理过程中随时停止操作
- 🌐 **多语言界面** - 中英文界面切换，自动检测系统语言
- 🔄 **批量高效处理** - 一次性处理整个歌曲列表，支持数千首歌曲

## 📋 安装要求

- Python 3.6+ (推荐 Python 3.8+)
- tkinter (通常随 Python 自带)
- 其他依赖均为 Python 标准库

## 🚀 快速开始

### 方法一：直接运行
1. 克隆或下载项目到本地
2. 运行程序：
   ```bash
   python MusicPicker.py
   ```

### 方法二：使用虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 运行程序
python MusicPicker.py
```

## 📖 使用方法

### 基本流程
1. **启动程序** - 运行 `python MusicPicker.py`
2. **选择歌曲列表** - 选择 `.txt` 歌曲列表文件
3. **选择音乐库** - 选择本地音乐文件夹（递归搜索子文件夹）
4. **选择输出位置** - 选择复制目标文件夹
5. **开始处理** - 点击"开始筛选复制"
6. **查看结果** - 通过日志查看处理过程

### 快速获取歌单（list.txt) 🌟
**方法一：GoMusic在线工具（推荐）**
1. 访问 https://music.unmeta.cn
2. 输入任意歌单链接（网易云/QQ音乐/汽水音乐）
3. 复制生成的歌曲列表
4. 保存为 `.txt` 文件直接使用

**方法二：手动创建**
1. 新建 `.txt` 文件
2. 按 `歌曲名 - 艺术家` 格式逐行添加
3. 使用 UTF-8 编码保存

## 📝 歌曲列表格式

### 手动创建格式
创建 `.txt` 文件，每行格式：`歌曲名 - 艺术家`

#### 示例：
```
# 🎤 华语流行
告白气球 - 周杰伦
七里香 - 周杰伦
演员 - 薛之谦

# 🌟 经典老歌
月亮代表我的心 - 邓丽君
甜蜜蜜 - 邓丽君
```

#### 格式要求：
- 📄 **编码**：UTF-8
- 🔤 **分隔符**：` - ` (空格-空格)
- 📝 **注释**：支持 `#` 开头的注释行
- ⚠️ **容错**：自动忽略空行和注释

## 🎯 智能匹配算法

### 包含式模糊匹配
程序采用**智能包含式匹配**，能处理各种文件命名差异：

#### ✅ 支持的命名格式（以"告白气球 - 周杰伦"为例）：
```
✅ "告白气球 - 周杰伦.mp3"              (标准格式)
✅ "周杰伦 - 告白气球.flac"             (艺术家在前)
✅ "告白气球_周杰伦.wav"                (下划线分隔)
✅ "[十二新作] 周杰伦 - 告白气球.mp3"    (包含专辑)
✅ "告白气球 - 周杰伦 [320K].flac"      (包含音质)
✅ "Jay Chou 周杰伦 - 告白气球.wav"     (中英混合)
```

#### 🔍 匹配原理：
- **双重验证** - 文件名必须同时包含歌曲名和艺术家
- **容错处理** - 自动忽略专辑、音质、版本等额外信息
- **大小写不敏感** - 自动处理大小写差异
- **格式兼容** - 支持各种分隔符和命名风格

#### 🎵 支持格式：MP3、FLAC、WAV、M4A、AAC、OGG

## 🏗️ 项目架构

```
MusicPicker/
├── MusicPicker.py       # 程序入口
├── gui.py               # 图形界面
├── music_processor.py   # 核心匹配逻辑
├── translator.py        # 多语言支持
├── config.py           # 配置文件
├── requirements.txt    # 依赖列表
└── 示例文件.txt         # 示例歌曲列表
```

## 📦 打包可执行文件

```bash
# 安装打包工具
pip install pyinstaller

# 生成exe文件
pyinstaller --onefile --windowed --name="MusicPicker" MusicPicker.py
```

生成的文件位于 `dist/MusicPicker.exe`

## 💡 使用技巧

### 快速上手：
1. **获取歌单** - 推荐使用 [GoMusic](https://music.unmeta.cn) 从现有歌单快速生成列表
2. **文件命名** - 确保音乐文件包含歌曲名和艺术家信息
3. **批量处理** - 一次性添加大量歌曲到列表文件

### 常见问题：
- **歌曲未找到** → 检查文件名是否包含完整的歌曲名和艺术家
- **中文乱码** → 确保歌曲列表文件使用 UTF-8 编码
- **程序卡顿** → 大型音乐库搜索需要时间，请耐心等待
- **权限问题** → 确保对输出文件夹有写入权限

## 🎮 应用场景

- **🔄 音乐平台迁移** - 更换音乐平台时，从本地库重建歌单避免版权缺失问题
- **📋 歌单本地化** - 将在线歌单转换为本地文件版本，便于离线使用和跨平台同步
- **🎵 音乐收藏整理** - 从庞大的本地音乐库中快速筛选和整理特定歌曲集合
- **☁️ 云同步准备** - 为 iTunes、Spotify 等平台的云同步功能准备标准化文件
- **💿 音乐库管理** - 批量复制、组织和备份音乐文件
- **📤 精选集制作** - 快速打包特定主题或风格的歌曲合集

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🙏 致谢

- 感谢 [GoMusic](https://github.com/Bistutu/GoMusic) 项目提供便捷的歌单获取方案
- 感谢所有贡献者和用户的支持

---

**享受音乐，享受编程！** 🎵✨