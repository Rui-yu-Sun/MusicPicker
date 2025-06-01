"""
工具函数模块
"""
import logging
from config import LOG_FILE, LOG_FORMAT

def setup_logging():
    """设置日志配置"""
    # 清除现有的handlers，避免重复设置
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 重新配置日志
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a'),
            logging.StreamHandler()
        ],
        force=True  # 强制重新配置
    )

def is_supported_audio_file(filename, supported_formats):
    """检查文件是否为支持的音频格式"""
    return filename.lower().endswith(supported_formats)

def normalize_filename(filename):
    """标准化文件名（去除扩展名并转小写）"""
    import os
    return os.path.splitext(filename)[0].lower()