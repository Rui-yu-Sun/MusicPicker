"""
歌单比较器模块
用于比较两个歌单文件的差异
"""
import os
import logging
from typing import List, Set, Dict, Tuple
import re


class PlaylistComparator:
    """歌单比较器"""

    def __init__(self, translator=None, log_callback=None):
        """
        初始化歌单比较器

        Args:
            translator: 翻译器实例
            log_callback: 日志回调函数
        """
        self.translator = translator
        self.log_callback = log_callback or self._default_log
        self.logger = logging.getLogger(__name__)

    def _default_log(self, message: str):
        """默认日志输出"""
        self.logger.info(message)

    def parse_playlist_file(self, file_path: str) -> Set[str]:
        """
        解析歌单文件，返回歌曲集合

        Args:
            file_path: 歌单文件路径

        Returns:
            歌曲集合（格式：歌名 - 歌手）
        """
        if not os.path.exists(file_path):
            self.log_callback(f"错误: 文件不存在 {file_path}")
            return set()

        songs = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # 跳过空行和注释行
                    if not line or line.startswith('#'):
                        continue

                    # 验证歌曲格式（歌名 - 歌手）
                    if ' - ' in line:
                        # 标准化格式
                        normalized_song = self._normalize_song_entry(line)
                        if normalized_song:
                            songs.add(normalized_song)
                    else:
                        self.log_callback(f"⚠️  第{line_num}行格式不正确: {line}")

            self.log_callback(
                f"✓ 解析完成: {os.path.basename(file_path)} ({len(songs)} 首歌曲)")
            return songs

        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and ' - ' in line:
                            normalized_song = self._normalize_song_entry(line)
                            if normalized_song:
                                songs.add(normalized_song)
                self.log_callback(
                    f"✓ 解析完成(GBK编码): {
                        os.path.basename(file_path)} ({
                        len(songs)} 首歌曲)")
                return songs
            except Exception as e:
                self.log_callback(f"❌ 编码错误: {str(e)}")
                return set()
        except Exception as e:
            self.log_callback(f"❌ 解析文件失败 {file_path}: {str(e)}")
            return set()

    def _normalize_song_entry(self, song_line: str) -> str:
        """
        标准化歌曲条目格式

        Args:
            song_line: 歌曲行文本

        Returns:
            标准化后的歌曲条目
        """
        # 移除首尾空白
        song_line = song_line.strip()
        # 查找 " - " 分隔符
        if ' - ' in song_line:
            parts = song_line.split(' - ', 1)  # 只分割一次
            if len(parts) == 2:
                title, artist = parts[0].strip(), parts[1].strip()
                if title and artist:
                    return f"{title} - {artist}"

        return ""

    def compare_playlists(
            self,
            playlist1_path: str,
            playlist2_path: str,
            output_folder: str = None,
            similarity_threshold: float = None) -> Dict:
        """
        比较两个歌单文件

        Args:
            playlist1_path: 第一个歌单文件路径
            playlist2_path: 第二个歌单文件路径
            output_folder: 输出文件夹路径（可选）
            similarity_threshold: 相似度阈值（可选）

        Returns:
            比较结果字典
        """
        self.log_callback("🔍 开始比较歌单...")

        # 解析两个歌单
        playlist1_name = os.path.basename(playlist1_path)
        playlist2_name = os.path.basename(playlist2_path)

        songs1 = self.parse_playlist_file(playlist1_path)
        songs2 = self.parse_playlist_file(playlist2_path)

        if not songs1 and not songs2:
            self.log_callback("❌ 两个歌单都为空或解析失败")
            return {}

        # 计算差异
        only_in_1 = songs1 - songs2  # 只在歌单1中存在
        only_in_2 = songs2 - songs1  # 只在歌单2中存在
        common = songs1 & songs2     # 两个歌单都有

        # 生成比较结果
        result = {
            "playlist1": {
                "name": playlist1_name,
                "path": playlist1_path,
                "total": len(songs1)
            },
            "playlist2": {
                "name": playlist2_name,
                "path": playlist2_path,
                "total": len(songs2)
            },
            "common_songs": sorted(list(common)),
            "only_in_playlist1": sorted(list(only_in_1)),
            "only_in_playlist2": sorted(list(only_in_2)),
            "stats": {
                "common_count": len(common),
                "only_in_1_count": len(only_in_1),
                "only_in_2_count": len(only_in_2),
                "total_unique": len(songs1 | songs2)
            }}

        # 输出统计信息
        self.log_callback("📊 比较结果统计:")
        self.log_callback(f"   📋 {playlist1_name}: {len(songs1)} 首歌曲")
        self.log_callback(f"   📋 {playlist2_name}: {len(songs2)} 首歌曲")
        self.log_callback(f"   🤝 共同歌曲: {len(common)} 首")
        self.log_callback(f"   🆔 仅在 {playlist1_name}: {len(only_in_1)} 首")
        self.log_callback(f"   🆔 仅在 {playlist2_name}: {len(only_in_2)} 首")
        self.log_callback(f"   🎵 总计不重复: {len(songs1 | songs2)} 首")

        # 如果提供了输出文件夹，生成详细报告
        if output_folder:
            if self.generate_difference_reports(result, output_folder):
                self.log_callback(f"✅ 详细报告已生成到: {output_folder}")
            else:
                self.log_callback("❌ 生成详细报告失败")

        return result

    def generate_difference_reports(
            self,
            comparison_result: Dict,
            output_dir: str) -> bool:
        """
        生成差异报告文件

        Args:
            comparison_result: 比较结果
            output_dir: 输出目录

        Returns:
            是否成功生成
        """
        if not comparison_result:
            self.log_callback("❌ 没有比较结果可生成报告")
            return False

        try:
            os.makedirs(output_dir, exist_ok=True)

            playlist1_name = comparison_result["playlist1"]["name"]
            playlist2_name = comparison_result["playlist2"]["name"]
            timestamp = self._get_current_time()

            # 生成仅在歌单1中的歌曲列表
            if comparison_result["only_in_playlist1"]:
                only_in_1_file = os.path.join(
                    output_dir, f"仅在_{
                        self._safe_filename(playlist1_name)}.txt")
                with open(only_in_1_file, 'w', encoding='utf-8') as f:
                    f.write(f"# 仅在 {playlist1_name} 中存在的歌曲\n")
                    f.write(f"# 生成时间: {timestamp}\n")
                    f.write(
                        f"# 总计: {len(comparison_result['only_in_playlist1'])} 首\n\n")

                    for song in comparison_result["only_in_playlist1"]:
                        f.write(f"{song}\n")

                self.log_callback(f"✓ 已生成: {only_in_1_file}")

            # 生成仅在歌单2中的歌曲列表
            if comparison_result["only_in_playlist2"]:
                only_in_2_file = os.path.join(
                    output_dir, f"仅在_{
                        self._safe_filename(playlist2_name)}.txt")
                with open(only_in_2_file, 'w', encoding='utf-8') as f:
                    f.write(f"# 仅在 {playlist2_name} 中存在的歌曲\n")
                    f.write(f"# 生成时间: {timestamp}\n")
                    f.write(
                        f"# 总计: {len(comparison_result['only_in_playlist2'])} 首\n\n")

                    for song in comparison_result["only_in_playlist2"]:
                        f.write(f"{song}\n")

                self.log_callback(f"✓ 已生成: {only_in_2_file}")

            # 生成共同歌曲列表
            if comparison_result["common_songs"]:
                common_file = os.path.join(output_dir, "共同歌曲.txt")
                with open(common_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {playlist1_name} 和 {playlist2_name} 的共同歌曲\n")
                    f.write(f"# 生成时间: {timestamp}\n")
                    f.write(
                        f"# 总计: {len(comparison_result['common_songs'])} 首\n\n")

                    for song in comparison_result["common_songs"]:
                        f.write(f"{song}\n")

                self.log_callback(f"✓ 已生成: {common_file}")

            # 生成完整比较报告
            report_file = os.path.join(output_dir, "比较报告.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"# 歌单比较报告\n")
                f.write(f"# 生成时间: {timestamp}\n\n")

                f.write(f"## 歌单信息\n")
                f.write(
                    f"歌单A: {playlist1_name} ({
                        comparison_result['playlist1']['total']} 首)\n")
                f.write(
                    f"歌单B: {playlist2_name} ({
                        comparison_result['playlist2']['total']} 首)\n\n")

                f.write(f"## 统计摘要\n")
                f.write(
                    f"共同歌曲: {comparison_result['stats']['common_count']} 首\n")
                f.write(
                    f"仅在歌单A: {
                        comparison_result['stats']['only_in_1_count']} 首\n")
                f.write(
                    f"仅在歌单B: {
                        comparison_result['stats']['only_in_2_count']} 首\n")
                f.write(
                    f"总计不重复: {
                        comparison_result['stats']['total_unique']} 首\n\n")

                # 计算相似度
                if comparison_result['stats']['total_unique'] > 0:
                    similarity = (comparison_result['stats']['common_count'] /
                                  comparison_result['stats']['total_unique']) * 100
                    f.write(f"相似度: {similarity:.1f}%\n\n")

                f.write(f"## 详细文件\n")
                f.write(f"- 仅在_{self._safe_filename(playlist1_name)}.txt\n")
                f.write(f"- 仅在_{self._safe_filename(playlist2_name)}.txt\n")
                f.write(f"- 共同歌曲.txt\n")

            self.log_callback(f"✓ 已生成: {report_file}")
            self.log_callback(f"✅ 所有差异报告已生成到: {output_dir}")

            return True

        except Exception as e:
            self.log_callback(f"❌ 生成报告失败: {str(e)}")
            return False

    def _safe_filename(self, filename: str) -> str:
        """
        生成安全的文件名（移除非法字符）

        Args:
            filename: 原始文件名

        Returns:
            安全的文件名
        """
        # 移除文件扩展名
        name = os.path.splitext(filename)[0]

        # 替换非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        safe_name = re.sub(illegal_chars, '_', name)

        # 限制长度
        if len(safe_name) > 50:
            safe_name = safe_name[:50]

        return safe_name

    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def find_similar_songs(self,
                           songs1: Set[str],
                           songs2: Set[str],
                           similarity_threshold: float = 0.8) -> List[Tuple[str,
                                                                            str,
                                                                            float]]:
        """
        查找相似但不完全相同的歌曲

        Args:
            songs1: 第一个歌曲集合
            songs2: 第二个歌曲集合
            similarity_threshold: 相似度阈值

        Returns:
            相似歌曲对列表 [(歌曲1, 歌曲2, 相似度)]
        """
        similar_pairs = []

        # 获取不在交集中的歌曲
        only_in_1 = songs1 - songs2
        only_in_2 = songs2 - songs1

        for song1 in only_in_1:
            for song2 in only_in_2:
                similarity = self._calculate_song_similarity(song1, song2)
                if similarity >= similarity_threshold:
                    similar_pairs.append((song1, song2, similarity))

        # 按相似度排序
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        return similar_pairs

    def _calculate_song_similarity(self, song1: str, song2: str) -> float:
        """
        计算两首歌的相似度

        Args:
            song1: 第一首歌
            song2: 第二首歌

        Returns:
            相似度分数（0-1）
        """
        # 简单的Jaccard相似度计算
        words1 = set(song1.lower().split())
        words2 = set(song2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0
