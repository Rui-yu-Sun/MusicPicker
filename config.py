"""
应用程序配置文件
"""
import tkinter as tk

# 应用程序信息
APP_NAME = "MusicPicker"
APP_VERSION = "1.0.0"
APP_TITLE = "Music Picker"

# 窗口配置
WINDOW_GEOMETRY = "800x600"
WINDOW_MIN_SIZE = (750, 550)

# 支持的音频格式
SUPPORTED_AUDIO_FORMATS = ('.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg')

# 日志配置
LOG_FILE = 'music_picker.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 界面配置
BUTTON_WIDTH = 10
BUTTON_HEIGHT = 2
ENTRY_PADDING = 8
MAIN_PADDING = 15

# 统一的字体配置 - 所有文字使用相同大小
def get_font_config():
    """获取字体配置，统一字体大小"""
    try:
        # 创建临时根窗口来检测DPI
        temp_root = tk.Tk()
        temp_root.withdraw()  # 隐藏窗口
        
        # 获取DPI缩放比例
        dpi = temp_root.winfo_fpixels('1i')
        scale_factor = max(1.0, dpi / 96.0)  # 最小缩放比例为1.0
        
        # 统一的字体大小 - 所有界面元素使用相同大小
        unified_size = max(11, int(12 * scale_factor))  # 统一使用12号字体
        button_size = max(12, int(13 * scale_factor))   # 按钮稍大一点
        
        temp_root.destroy()
        
        # 字体配置 - 统一字体大小
        fonts = {
            'main': ('Microsoft YaHei UI', unified_size),           # 主要文字
            'button': ('Microsoft YaHei UI', button_size, 'bold'),  # 按钮文字
            'log': ('Consolas', unified_size),                      # 日志文字
            'label': ('Microsoft YaHei UI', unified_size),          # 标签文字（与主要文字相同）
            'progress': ('Microsoft YaHei UI', unified_size),       # 进度文字（与主要文字相同）
        }
        
        return fonts
        
    except:
        # 降级方案 - 统一字体大小
        unified_size = 12
        return {
            'main': ('Microsoft YaHei', unified_size),
            'button': ('Microsoft YaHei', unified_size + 1, 'bold'),
            'log': ('Courier New', unified_size),
            'label': ('Microsoft YaHei', unified_size),      # 与main相同
            'progress': ('Microsoft YaHei', unified_size),   # 与main相同
        }

# 获取字体配置
FONTS = get_font_config()

# 简化的颜色配置
COLORS = {
    'bg_main': '#ffffff',           # 主背景色
    'bg_frame': '#f8f9fa',          # 框架背景色
    'text_normal': '#333333',       # 普通文字颜色
    'entry_bg': '#ffffff',          # 输入框背景
    'button_bg': '#f0f0f0',         # 按钮背景（系统默认）
}