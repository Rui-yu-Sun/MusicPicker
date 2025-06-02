"""
音乐处理核心逻辑模块
"""
import os
import shutil
import logging
from config import SUPPORTED_AUDIO_FORMATS
from utils import is_supported_audio_file, normalize_filename


class MusicProcessor:
    def __init__(self, translator, log_callback):
        self.translator = translator
        self.log_callback = log_callback
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        self.metadata_processor = None  # 将通过外部设置
        self.use_metadata_matching = False  # 是否使用元数据匹配

    def set_metadata_processor(self, metadata_processor):
        """设置元数据处理器"""
        self.metadata_processor = metadata_processor

    def set_use_metadata_matching(self, use_metadata: bool):
        """设置是否使用元数据匹配"""
        self.use_metadata_matching = use_metadata
        if use_metadata and self.metadata_processor and not self.metadata_processor.is_metadata_available():
            self._log_message("警告: 元数据功能不可用，将使用文件名匹配", 'warning')
            self.use_metadata_matching = False

    def _log_message(self, message, level='info'):
        """同时记录到GUI和日志文件"""
        # 显示在GUI中
        self.log_callback(message)
        # 记录到日志文件
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)

    def parse_song_list(self, file_path):
        """解析歌曲列表文件"""
        songs_to_find = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释行
                    if not line or line.startswith('#'):
                        continue
                    parts = line.rsplit(' - ', 1)
                    if len(parts) == 2:
                        song_title = parts[0].strip().lower()
                        artist = parts[1].strip().lower()
                        songs_to_find.append({
                            'title': song_title,
                            'artist': artist,
                            'original_line': line
                        })
                    else:
                        self._log_message(self.translator.t(
                            'parse_warning', line), 'warning')
        except FileNotFoundError:
            self._log_message(self.translator.t(
                'file_not_found', file_path), 'error')
            return None
        except Exception as e:
            self._log_message(self.translator.t('parse_error', e), 'error')
            return None
        return songs_to_find

    def find_and_copy_songs(
            self,
            songs_to_find,
            library_path,
            output_path,
            progress_callback):
        """查找并复制歌曲"""
        if not songs_to_find:
            self._log_message(self.translator.t('song_list_empty'))
            return

        if not os.path.isdir(library_path):
            self._log_message(self.translator.t(
                'invalid_library_path', library_path), 'error')
            return

        # 创建输出目录
        if not self._create_output_directory(output_path):
            return

        found_count = 0
        total_songs_to_check = len(songs_to_find)

        self._log_message(self.translator.t('starting_search', library_path))

        # 创建歌曲状态字典
        song_status = {song_info['original_line']                       : False for song_info in songs_to_find}

        # 遍历音乐库
        for root, _, files in os.walk(library_path):
            if not self.is_running:
                self._log_message(self.translator.t('operation_aborted'))
                return

            for filename in files:
                if not self.is_running:
                    self._log_message(self.translator.t('operation_aborted'))
                    return

                if not is_supported_audio_file(
                        filename, SUPPORTED_AUDIO_FORMATS):
                    continue

                file_path = os.path.join(root, filename)
                filename_no_ext = normalize_filename(filename)

                # 检查是否匹配歌曲列表
                found_count += self._process_file_match(
                    file_path, filename, filename_no_ext,
                    songs_to_find, song_status, output_path
                )

                # 更新进度
                count_processed = sum(
                    1 for status in song_status.values() if status)
                progress_callback(count_processed, total_songs_to_check)

        # 处理完成
        self._finalize_processing(
            found_count, song_status, total_songs_to_check, progress_callback)

    def _create_output_directory(self, output_path):
        """创建输出目录"""
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
                self._log_message(self.translator.t(
                    'output_folder_created', output_path))
                return True
            except OSError as e:
                self._log_message(self.translator.t(
                    'create_output_folder_failed', output_path, e), 'error')
                return False
        return True

    def _normalize_artist_separators(self, text: str) -> str:
        """
        标准化艺术家分隔符，将 / 和 _ 统一处理

        Args:
            text: 待处理的文本

        Returns:
            标准化后的文本
        """
        import re
        # 将 / 和 _ 都替换为空格，便于匹配
        text = re.sub(r'[/_]', ' ', text)
        # 压缩多个空格为单个空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text.lower()

    def _enhanced_filename_match(
            self,
            song_title: str,
            song_artist: str,
            filename_no_ext: str) -> bool:
        """
        增强的文件名匹配算法，支持多作者分隔符兼容

        Args:
            song_title: 歌曲标题
            song_artist: 歌曲艺术家
            filename_no_ext: 文件名（无扩展名）

        Returns:
            是否匹配
        """
        # 基本匹配：直接包含检查
        if song_title in filename_no_ext and song_artist in filename_no_ext:
            return True

        # 增强匹配：处理分隔符差异
        normalized_filename = self._normalize_artist_separators(
            filename_no_ext)
        normalized_artist = self._normalize_artist_separators(song_artist)
        normalized_title = song_title.lower().strip()

        # 检查标准化后的匹配
        if normalized_title in normalized_filename and normalized_artist in normalized_filename:
            return True

        # 处理多个艺术家的情况：分解艺术家名称
        import re
        # 分解歌单中的艺术家（支持 / 和 _ 分隔符）
        artists_in_song = re.split(r'[/_]', song_artist.strip())
        artists_in_song = [artist.strip().lower()
                           for artist in artists_in_song if artist.strip()]

        # 检查是否所有艺术家都在文件名中
        if artists_in_song:
            all_artists_found = all(
                artist in normalized_filename for artist in artists_in_song)
            if normalized_title in normalized_filename and all_artists_found:
                return True

        return False

    def _process_file_match(
            self,
            file_path,
            filename,
            filename_no_ext,
            songs_to_find,
            song_status,
            output_path):
        """处理文件匹配"""
        found_count = 0

        for song_info in songs_to_find:
            if song_status[song_info['original_line']]:
                continue

            # 根据设置选择匹配方式
            is_match = False
            if self.use_metadata_matching and self.metadata_processor:
                # 使用元数据匹配
                metadata = self.metadata_processor.extract_metadata(file_path)
                if metadata:
                    is_match = self.metadata_processor.match_song_by_metadata(
                        song_info, metadata)
                    if is_match:
                        self._log_message(
                            f"元数据匹配: {
                                song_info['original_line']} -> {filename}")
              # 如果元数据匹配失败或未启用，则使用文件名匹配
            if not is_match:
                # 使用增强的文件名匹配算法
                is_match = self._enhanced_filename_match(
                    song_info['title'], song_info['artist'], filename_no_ext)
                if is_match:
                    if self.use_metadata_matching:
                        self._log_message(
                            f"文件名匹配: {
                                song_info['original_line']} -> {filename}")
                    else:
                        self._log_message(
                            f"文件名匹配: {
                                song_info['original_line']} -> {filename}")

            if is_match:
                destination_path = os.path.join(output_path, filename)
                try:
                    if os.path.exists(destination_path):
                        self._log_message(
                            self.translator.t(
                                'file_already_exists',
                                filename,
                                song_info['original_line']))
                    else:
                        shutil.copy2(file_path, destination_path)
                        self._log_message(
                            self.translator.t(
                                'found_and_copied',
                                song_info['original_line'],
                                filename))
                        found_count += 1

                    song_status[song_info['original_line']] = True
                    break
                except Exception as e:
                    self._log_message(
                        self.translator.t(
                            'copy_failed',
                            file_path,
                            destination_path,
                            e),
                        'error')

        return found_count

    def _finalize_processing(
            self,
            found_count,
            song_status,
            total_songs,
            progress_callback):
        """完成处理"""
        self._log_message(self.translator.t('search_complete', found_count))

        # 显示未找到的歌曲
        unfound_songs = [line for line,
                         found in song_status.items() if not found]
        if unfound_songs:
            self._log_message('\n' + self.translator.t('unfound_songs_header'))
            for original_line in unfound_songs:
                self._log_message(f"- {original_line}")

        progress_callback(total_songs, total_songs)

    def start_processing(self, list_file, music_lib, output_dir):
        """开始处理音乐文件"""
        self.is_running = True
        self._log_message("开始处理音乐文件...")

        # 设置元数据匹配选项
        use_metadata = getattr(self, 'use_metadata_matching', False)
        self.set_use_metadata_matching(use_metadata)

        # 解析歌曲列表
        songs_to_find = self.parse_song_list(list_file)
        if songs_to_find is None:
            self.is_running = False
            return

        # 开始查找和复制
        def dummy_progress_callback(current, total):
            """临时进度回调函数"""
            pass

        self.find_and_copy_songs(
            songs_to_find, music_lib, output_dir, dummy_progress_callback)
        self.is_running = False

    def stop_processing(self):
        """停止处理"""
        self.is_running = False
        self._log_message("处理已停止")
