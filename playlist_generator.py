"""
歌单生成器模块
用于从音乐文件夹生成歌单列表
"""
import os
import logging
from typing import List, Optional, Tuple, Dict
from pathlib import Path
import re
from config import SUPPORTED_AUDIO_FORMATS


class PlaylistGenerator:
    """歌单生成器"""

    def __init__(
            self,
            metadata_processor=None,
            translator=None,
            log_callback=None):
        """
        初始化歌单生成器

        Args:
            metadata_processor: 元数据处理器实例（可选）
            translator: 翻译器实例
            log_callback: 日志回调函数
        """
        self.metadata_processor = metadata_processor
        self.translator = translator
        self.log_callback = log_callback or self._default_log
        self.logger = logging.getLogger(__name__)

    def _default_log(self, message: str):
        """默认日志输出"""
        self.logger.info(message)

    def scan_music_folder(self, folder_path: str) -> List[str]:
        """
        扫描文件夹中的音乐文件

        Args:
            folder_path: 音乐文件夹路径

        Returns:
            音乐文件路径列表
        """
        if not os.path.exists(folder_path):
            self.log_callback(f"错误: 文件夹不存在 {folder_path}")
            return []

        music_files = []
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext)
                           for ext in SUPPORTED_AUDIO_FORMATS):
                        file_path = os.path.join(root, file)
                        music_files.append(file_path)

            self.log_callback(f"扫描完成，找到 {len(music_files)} 个音乐文件")
            return music_files

        except Exception as e:
            self.log_callback(f"扫描文件夹时出错: {str(e)}")
            return []

    def parse_filename(self, filepath: str) -> Optional[Tuple[str, str]]:
        """
        从文件名解析歌曲信息
        支持格式：歌名-歌手.扩展名 或 歌手-歌名.扩展名

        Args:
            filepath: 音乐文件路径

        Returns:
            (歌名, 歌手) 元组，失败返回None
        """
        filename = os.path.splitext(os.path.basename(filepath))[0]

        # 尝试多种分隔符
        separators = [' - ', '-', ' _ ', '_', ' — ', '—']

        for sep in separators:
            if sep in filename:
                parts = filename.split(sep, 1)  # 只分割一次
                if len(parts) == 2:
                    part1, part2 = parts[0].strip(), parts[1].strip()
                    if part1 and part2:
                        # 尝试判断哪个是歌名，哪个是歌手
                        # 通常歌名在前，但也支持歌手在前的格式
                        return (part1, part2)

        # 如果没有分隔符，尝试从元数据获取
        return None

    def extract_song_info_from_metadata(
            self, filepath: str) -> Optional[Tuple[str, str]]:
        """
        从元数据提取歌曲信息

        Args:
            filepath: 音乐文件路径

        Returns:
            (歌名, 歌手) 元组，失败返回None
        """
        if not self.metadata_processor:
            return None

        try:
            metadata = self.metadata_processor.extract_metadata(filepath)
            if metadata and metadata.title and metadata.artist:
                return (metadata.title.strip(), metadata.artist.strip())
        except Exception as e:
            self.log_callback(
                f"提取元数据失败 {os.path.basename(filepath)}: {str(e)}")

        return None

    def generate_playlist_from_folder(self, folder_path: str, output_file: str,
                                      use_metadata: bool = False,
                                      include_subdirs: bool = True) -> bool:
        """
        从文件夹生成歌单

        Args:
            folder_path: 音乐文件夹路径
            output_file: 输出的歌单文件路径
            use_metadata: 是否优先使用元数据
            include_subdirs: 是否包含子目录

        Returns:
            是否成功生成
        """
        if not os.path.exists(folder_path):
            self.log_callback("错误: 指定的文件夹不存在")
            return False

        self.log_callback(f"开始扫描文件夹: {folder_path}")
        music_files = self.scan_music_folder(folder_path)

        if not music_files:
            self.log_callback("文件夹中没有找到音乐文件")
            return False

        playlist_entries = []
        success_count = 0
        failed_files = []

        for file_path in music_files:
            song_info = None
            filename = os.path.basename(file_path)

            # 根据用户选择决定提取方式
            if use_metadata and self.metadata_processor:
                # 优先使用元数据
                song_info = self.extract_song_info_from_metadata(file_path)
                if not song_info:
                    # 元数据失败时降级到文件名
                    song_info = self.parse_filename(file_path)
                    if song_info:
                        self.log_callback(f"元数据获取失败，使用文件名: {filename}")
            else:
                # 使用文件名解析
                song_info = self.parse_filename(file_path)

            if song_info:
                title, artist = song_info
                playlist_entry = f"{title} - {artist}"
                playlist_entries.append(playlist_entry)
                success_count += 1
                self.log_callback(f"✓ {playlist_entry}")
            else:
                failed_files.append(filename)
                self.log_callback(f"✗ 无法解析: {filename}")

        # 排序歌单条目
        playlist_entries.sort()

        # 写入文件
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# 歌单生成时间: {self._get_current_time()}\n")
                f.write(f"# 源文件夹: {folder_path}\n")
                f.write(f"# 总歌曲数: {len(playlist_entries)}\n")
                f.write(f"# 使用方法: {'元数据优先' if use_metadata else '文件名解析'}\n")
                f.write("\n")

                for entry in playlist_entries:
                    f.write(f"{entry}\n")

            self.log_callback(f"✅ 歌单生成完成!")
            self.log_callback(f"📁 保存位置: {output_file}")
            self.log_callback(
                f"📊 成功: {success_count} 首，失败: {len(failed_files)} 首")

            if failed_files:
                self.log_callback("⚠️  以下文件无法解析:")
                for file in failed_files[:10]:  # 只显示前10个
                    self.log_callback(f"   • {file}")
                if len(failed_files) > 10:
                    self.log_callback(
                        f"   ... 还有 {len(failed_files) - 10} 个文件")

            return True

        except Exception as e:
            self.log_callback(f"❌ 写入文件失败: {str(e)}")
            return False

    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def validate_filename_format(self, filename: str) -> bool:
        """
        验证文件名是否符合 "歌名-歌手" 格式

        Args:
            filename: 文件名（不含扩展名）

        Returns:
            是否符合格式
        """
        separators = [' - ', '-', ' _ ', '_', ' — ', '—']

        for sep in separators:
            if sep in filename:
                parts = filename.split(sep, 1)
                if len(parts) == 2:
                    part1, part2 = parts[0].strip(), parts[1].strip()
                    if part1 and part2:
                        return True
        return False

    def get_folder_analysis(self, folder_path: str) -> Dict:
        """
        分析文件夹内容，返回统计信息

        Args:
            folder_path: 文件夹路径

        Returns:
            分析结果字典
        """
        if not os.path.exists(folder_path):
            return {"error": "文件夹不存在"}

        music_files = self.scan_music_folder(folder_path)

        analysis = {
            "total_files": len(music_files),
            "parseable_files": 0,
            "metadata_available": 0,
            "format_distribution": {},
            "unparseable_files": []
        }

        for file_path in music_files:
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()

            # 统计格式分布
            analysis["format_distribution"][ext] = analysis["format_distribution"].get(
                ext, 0) + 1

            # 检查文件名是否可解析
            name_without_ext = os.path.splitext(filename)[0]
            if self.validate_filename_format(name_without_ext):
                analysis["parseable_files"] += 1
            else:
                analysis["unparseable_files"].append(filename)

            # 检查是否有元数据
            if self.metadata_processor:
                metadata = self.extract_song_info_from_metadata(file_path)
                if metadata:
                    analysis["metadata_available"] += 1

        return analysis

    def generate_playlist(self, folder_path: str, output_file: str,
                          use_metadata: bool = False,
                          include_subdirs: bool = True) -> bool:
        """
        生成播放列表的主接口方法（供GUI调用）

        Args:
            folder_path: 音乐文件夹路径
            output_file: 输出的歌单文件路径
            use_metadata: 是否优先使用元数据
            include_subdirs: 是否包含子目录

        Returns:
            是否成功生成
        """
        return self.generate_playlist_from_folder(
            folder_path, output_file, use_metadata, include_subdirs
        )
