"""
MusicPicker - 歌曲筛选复制工具
主程序入口
"""
from translator import Translator, detect_system_language
from music_processor import MusicProcessor
from gui import MusicPickerGUI
from utils import setup_logging

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 初始化翻译器
    translator = Translator()
    translator.set_language(detect_system_language())
    
    # 创建GUI应用
    app = MusicPickerGUI(translator, None)
    
    # 创建音乐处理器
    music_processor = MusicProcessor(translator, app.log_message)
    app.music_processor = music_processor
    
    # 创建并运行窗口
    app.create_window()
    app.update_ui_language()
    app.run()

if __name__ == "__main__":
    main()