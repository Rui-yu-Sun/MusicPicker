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
                        self._log_message(self.translator.t('parse_warning', line), 'warning')
        except FileNotFoundError:
            self._log_message(self.translator.t('file_not_found', file_path), 'error')
            return None
        except Exception as e:
            self._log_message(self.translator.t('parse_error', e), 'error')
            return None
        return songs_to_find
    
    def find_and_copy_songs(self, songs_to_find, library_path, output_path, progress_callback):
        """查找并复制歌曲"""
        if not songs_to_find:
            self._log_message(self.translator.t('song_list_empty'))
            return

        if not os.path.isdir(library_path):
            self._log_message(self.translator.t('invalid_library_path', library_path), 'error')
            return

        # 创建输出目录
        if not self._create_output_directory(output_path):
            return
        
        found_count = 0
        total_songs_to_check = len(songs_to_find)
        
        self._log_message(self.translator.t('starting_search', library_path))

        # 创建歌曲状态字典
        song_status = {song_info['original_line']: False for song_info in songs_to_find}

        # 遍历音乐库
        for root, _, files in os.walk(library_path):
            if not self.is_running:
                self._log_message(self.translator.t('operation_aborted'))
                return

            for filename in files:
                if not self.is_running:
                    self._log_message(self.translator.t('operation_aborted'))
                    return

                if not is_supported_audio_file(filename, SUPPORTED_AUDIO_FORMATS):
                    continue

                file_path = os.path.join(root, filename)
                filename_no_ext = normalize_filename(filename)

                # 检查是否匹配歌曲列表
                found_count += self._process_file_match(
                    file_path, filename, filename_no_ext, 
                    songs_to_find, song_status, output_path
                )
                
                # 更新进度
                count_processed = sum(1 for status in song_status.values() if status)
                progress_callback(count_processed, total_songs_to_check)

        # 处理完成
        self._finalize_processing(found_count, song_status, total_songs_to_check, progress_callback)
    
    def _create_output_directory(self, output_path):
        """创建输出目录"""
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
                self._log_message(self.translator.t('output_folder_created', output_path))
                return True
            except OSError as e:
                self._log_message(self.translator.t('create_output_folder_failed', output_path, e), 'error')
                return False
        return True
    
    def _process_file_match(self, file_path, filename, filename_no_ext, songs_to_find, song_status, output_path):
        """处理文件匹配"""
        found_count = 0
        
        for song_info in songs_to_find:
            if song_status[song_info['original_line']]:
                continue

            if song_info['title'] in filename_no_ext and song_info['artist'] in filename_no_ext:
                destination_path = os.path.join(output_path, filename)
                try:
                    if os.path.exists(destination_path):
                        self._log_message(self.translator.t('file_already_exists', filename, song_info['original_line']))
                    else:
                        shutil.copy2(file_path, destination_path)
                        self._log_message(self.translator.t('found_and_copied', song_info['original_line'], filename))
                        found_count += 1
                    
                    song_status[song_info['original_line']] = True
                    break
                except Exception as e:
                    self._log_message(self.translator.t('copy_failed', file_path, destination_path, e), 'error')
        
        return found_count
    
    def _finalize_processing(self, found_count, song_status, total_songs, progress_callback):
        """完成处理"""
        self._log_message(self.translator.t('search_complete', found_count))
        
        # 显示未找到的歌曲
        unfound_songs = [line for line, found in song_status.items() if not found]
        if unfound_songs:
            self._log_message('\n' + self.translator.t('unfound_songs_header'))
            for original_line in unfound_songs:
                self._log_message(f"- {original_line}")
        
        progress_callback(total_songs, total_songs)
    
    def start(self):
        """开始处理"""
        self.is_running = True
        self._log_message("开始处理音乐文件...")
    
    def stop(self):
        """停止处理"""
        self.is_running = False
        self._log_message("处理已停止")