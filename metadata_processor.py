"""
音乐文件元数据处理器模块
用于读取、比较和分析音乐文件的元数据
"""
import os
import logging
from typing import Dict, List, Optional, Tuple, Any
try:
    from mutagen import File
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
from dataclasses import dataclass, asdict
import json
from config import SUPPORTED_AUDIO_FORMATS

@dataclass
class MusicMetadata:
    """音乐元数据类"""
    filepath: str
    filename: str
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    albumartist: Optional[str] = None
    date: Optional[str] = None
    genre: Optional[str] = None
    track: Optional[str] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    format: Optional[str] = None
    size: Optional[int] = None

class MetadataProcessor:
    """元数据处理器"""
    
    def __init__(self, translator, log_callback=None):
        """
        初始化元数据处理器
        
        Args:
            translator: 翻译器实例
            log_callback: 日志回调函数
        """
        self.translator = translator
        self.log_callback = log_callback or self._default_log
        self.logger = logging.getLogger(__name__)
        
        # 检查mutagen库是否可用
        if not MUTAGEN_AVAILABLE:
            self.log_callback("警告: 未安装mutagen库，元数据功能将受限。请运行: pip install mutagen")
    
    def _default_log(self, message: str):
        """默认日志输出"""
        self.logger.info(message)
    
    def is_metadata_available(self) -> bool:
        """检查元数据功能是否可用"""
        return MUTAGEN_AVAILABLE
    
    def extract_metadata(self, filepath: str) -> Optional[MusicMetadata]:
        """
        提取单个文件的元数据
        
        Args:
            filepath: 音乐文件路径
            
        Returns:
            MusicMetadata对象或None
        """
        if not MUTAGEN_AVAILABLE:
            return None
            
        try:
            if not os.path.exists(filepath):
                return None
            
            # 检查文件格式
            ext = os.path.splitext(filepath)[1].lower()
            if ext not in SUPPORTED_AUDIO_FORMATS:
                return None
            
            # 使用mutagen读取元数据
            audio_file = File(filepath)
            if audio_file is None:
                return None
            
            # 获取基本文件信息
            file_stats = os.stat(filepath)
            filename = os.path.basename(filepath)
            
            # 创建元数据对象
            metadata = MusicMetadata(
                filepath=filepath,
                filename=filename,
                size=file_stats.st_size,
                format=ext[1:].upper()
            )
            
            # 提取音频信息
            if hasattr(audio_file, 'info'):
                info = audio_file.info
                metadata.duration = getattr(info, 'length', None)
                metadata.bitrate = getattr(info, 'bitrate', None)
            
            # 提取标签信息
            if audio_file.tags:
                tags = audio_file.tags
                metadata.title = self._get_tag_value(tags, ['TIT2', 'TITLE', '\xa9nam'])
                metadata.artist = self._get_tag_value(tags, ['TPE1', 'ARTIST', '\xa9ART'])
                metadata.album = self._get_tag_value(tags, ['TALB', 'ALBUM', '\xa9alb'])
                metadata.albumartist = self._get_tag_value(tags, ['TPE2', 'ALBUMARTIST', 'aART'])
                metadata.date = self._get_tag_value(tags, ['TDRC', 'DATE', '\xa9day'])
                metadata.genre = self._get_tag_value(tags, ['TCON', 'GENRE', '\xa9gen'])
                metadata.track = self._get_tag_value(tags, ['TRCK', 'TRACKNUMBER', 'trkn'])
            
            return metadata
            
        except Exception as e:
            self.log_callback(f"提取元数据失败 {filepath}: {str(e)}")
            return None
    
    def _get_tag_value(self, tags, tag_keys: List[str]) -> Optional[str]:
        """
        从标签中获取值，支持多种格式的标签键
        
        Args:
            tags: 音频文件标签
            tag_keys: 可能的标签键列表
            
        Returns:
            标签值或None
        """
        for key in tag_keys:
            if key in tags:
                value = tags[key]
                if isinstance(value, list) and value:
                    return str(value[0])
                elif value:
                    return str(value)
        return None
    
    def match_song_by_metadata(self, song_info: Dict, metadata: MusicMetadata, 
                              match_threshold: float = 0.8) -> bool:
        """
        基于元数据匹配歌曲
        
        Args:
            song_info: 歌曲信息字典，包含title和artist
            metadata: 音乐文件元数据
            match_threshold: 匹配阈值（0-1）
            
        Returns:
            是否匹配
        """
        if not metadata or not metadata.title or not metadata.artist:
            return False
        
        # 标准化比较
        song_title = self._normalize_text(song_info['title'])
        song_artist = self._normalize_text(song_info['artist'])
        meta_title = self._normalize_text(metadata.title)
        meta_artist = self._normalize_text(metadata.artist)
        
        # 计算相似度
        title_similarity = self._calculate_similarity(song_title, meta_title)
        artist_similarity = self._calculate_similarity(song_artist, meta_artist)
        
        # 综合相似度（标题权重更高）
        overall_similarity = (title_similarity * 0.7 + artist_similarity * 0.3)
        
        return overall_similarity >= match_threshold
    
    def _normalize_text(self, text: str) -> str:
        """
        标准化文本用于比较
        
        Args:
            text: 要标准化的文本
            
        Returns:
            标准化后的文本
        """
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
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            相似度分数（0-1）
        """
        if not text1 or not text2:
            return 0.0
        
        # 简单的包含关系检查
        if text1 in text2 or text2 in text1:
            return 1.0
        
        # 计算Jaccard相似度（基于单词）
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def compare_metadata(self, metadata1: MusicMetadata, metadata2: MusicMetadata, 
                        compare_fields: List[str] = None) -> Dict[str, Any]:
        """
        比较两个音乐文件的元数据
        
        Args:
            metadata1: 第一个文件的元数据
            metadata2: 第二个文件的元数据
            compare_fields: 要比较的字段列表，None表示比较所有字段
            
        Returns:
            比较结果字典
        """
        if compare_fields is None:
            compare_fields = ['title', 'artist', 'album', 'albumartist', 'date', 'genre', 'track']
        
        result = {
            'file1': metadata1.filename,
            'file2': metadata2.filename,
            'matches': {},
            'differences': {},
            'similarity_score': 0.0
        }
        
        matches = 0
        total_fields = len(compare_fields)
        
        for field in compare_fields:
            value1 = getattr(metadata1, field, None)
            value2 = getattr(metadata2, field, None)
            
            # 标准化值进行比较
            norm_value1 = self._normalize_text(str(value1)) if value1 else ""
            norm_value2 = self._normalize_text(str(value2)) if value2 else ""
            
            if norm_value1 == norm_value2:
                result['matches'][field] = {
                    'value': value1,
                    'match': True
                }
                matches += 1
            else:
                result['differences'][field] = {
                    'file1': value1,
                    'file2': value2,
                    'match': False
                }
        
        # 计算相似度分数
        result['similarity_score'] = (matches / total_fields) * 100 if total_fields > 0 else 0
        
        return result
    
    def find_duplicates(self, metadata_list: List[MusicMetadata], 
                       similarity_threshold: float = 90.0,
                       compare_fields: List[str] = None) -> List[List[MusicMetadata]]:
        """
        在元数据列表中查找重复文件
        
        Args:
            metadata_list: 元数据列表
            similarity_threshold: 相似度阈值（百分比）
            compare_fields: 要比较的字段列表
            
        Returns:
            重复文件组的列表
        """
        if compare_fields is None:
            compare_fields = ['title', 'artist', 'album']
        
        duplicate_groups = []
        processed = set()
        
        self.log_callback(f"开始查找重复文件，相似度阈值: {similarity_threshold}%")
        
        for i, metadata1 in enumerate(metadata_list):
            if i in processed:
                continue
            
            current_group = [metadata1]
            processed.add(i)
            
            for j, metadata2 in enumerate(metadata_list[i+1:], start=i+1):
                if j in processed:
                    continue
                
                comparison = self.compare_metadata(metadata1, metadata2, compare_fields)
                if comparison['similarity_score'] >= similarity_threshold:
                    current_group.append(metadata2)
                    processed.add(j)
            
            # 只保存包含多个文件的组（即实际的重复文件）
            if len(current_group) > 1:
                duplicate_groups.append(current_group)
        
        self.log_callback(f"找到 {len(duplicate_groups)} 组重复文件")
        return duplicate_groups
    
    def _format_duration(self, duration: Optional[float]) -> str:
        """格式化时长显示"""
        if duration is None:
            return "N/A"
        
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes}:{seconds:02d}"
    
    def _format_file_size(self, size: Optional[int]) -> str:
        """格式化文件大小显示"""
        if size is None:
            return "N/A"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
