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

def normalize_for_comparison(text):
    """标准化文本用于比较"""
    if not text:
        return ""
    
    import re
    # 转换为小写
    text = text.lower().strip()
    
    # 移除常见的括号内容（如feat.等）
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    
    # 移除特殊字符，只保留字母数字和空格
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 压缩多个空格为单个空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def check_mutagen_availability():
    """检查mutagen库是否可用"""
    try:
        import mutagen
        return True
    except ImportError:
        return False