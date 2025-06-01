"""
MusicPicker - 歌曲筛选复制工具
主程序入口
"""
from translator import Translator, detect_system_language
from music_processor import MusicProcessor
from metadata_processor import MetadataProcessor
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
    
    # 创建元数据处理器
    metadata_processor = MetadataProcessor(translator, app.log_message)
      # 将处理器绑定到应用
    app.music_processor = music_processor
    app.metadata_processor = metadata_processor
    
    # 将元数据处理器绑定到音乐处理器
    music_processor.set_metadata_processor(metadata_processor)
    
    # 创建并运行窗口
    app.create_window()
    app.update_ui_language()
    app.run()

if __name__ == "__main__":
    main()