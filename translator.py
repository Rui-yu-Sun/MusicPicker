"""
国际化翻译模块
"""
import locale


class Translator:
    def __init__(self):
        self.current_language = 'zh'  # 默认中文
        self.translations = self.load_translations()

    def load_translations(self):
        """加载翻译文件"""
        translations = {
            'zh': {                # 窗口标题
                'window_title': '歌曲筛选复制工具',

                # 语言按钮
                'language_button': '中/En',

                # 标签文本
                'song_list_file': '歌曲列表 (list.txt):',
                'music_library_path': '本地音乐库路径:',
                'output_folder_path': '输出文件夹路径:',
                'log_output': '日志:',
                'progress_na': '进度: N/A',
                # 按钮文本
                'browse_button': '浏览...',
                'start_button': '开始筛选复制',
                'stop_button': '停止',

                # 元数据匹配选项
                'use_metadata_matching': '使用元数据匹配',
                'metadata_help_text': '基于歌曲标签信息进行匹配，准确度更高',
                'warning': '警告',

                # 对话框标题
                'select_song_list': '选择歌曲列表文件',
                'select_music_library': '选择音乐库文件夹',
                'select_output_folder': '选择输出文件夹',
                'error_title': '错误',
                'exit_title': '退出',
                'severe_error_title': '严重错误',

                # 消息文本
                'all_paths_required': '请确保所有路径都已选择！',
                'confirm_exit': '确定要退出程序吗？',
                'starting_process': '开始处理...',
                'all_operations_complete': '所有操作完成。',
                'attempting_to_stop': '正在尝试停止操作...',
                'operation_aborted': '操作已中止。',
                'processing_failed': '处理失败: {}',

                # 日志消息
                'song_list_empty': '歌曲列表为空，无需操作。',
                'invalid_library_path': '错误: 音乐库路径 \'{}\' 不是一个有效的文件夹。',
                'output_folder_created': '已创建输出文件夹: \'{}\'',
                'create_output_folder_failed': '错误: 无法创建输出文件夹 \'{}\': {}',
                'starting_search': '开始在 \'{}\' 中搜索歌曲...',
                'file_already_exists': '提示: 文件 \'{}\' 已存在于目标文件夹，跳过复制 (来自: {})。',
                'found_and_copied': '找到并复制: \'{}\' -> \'{}\'',
                'copy_failed': '错误: 复制文件 \'{}\' 到 \'{}\' 失败: {}',
                'search_complete': '搜索完成。共找到并复制 {} 首不同的歌曲。',
                'unfound_songs_header': '以下歌曲可能未在音乐库中找到（或命名不匹配）：',
                'parse_warning': '警告: 无法解析行 \'{}\'，跳过。',
                'file_not_found': '错误: 歌曲列表文件 \'{}\' 未找到。',
                'parse_error': '错误: 解析歌曲列表时发生错误: {}',
                'load_song_list_failed': '未能加载歌曲列表，操作中止。',
                'uncaught_error': '处理过程中发生未捕获的错误: {}',
                # 进度文本
                'progress_format': '进度: {}/{} ({:.2f}%)',
                'progress_na': '进度: N/A',
                # v1.2 新功能 - 播放列表生成器
                'playlist_generator_tab': '播放列表生成器',
                'music_folder': '音乐文件夹:',
                'playlist_output_file': '播放列表输出文件:',
                'use_metadata_for_playlist': '使用元数据提取',
                'metadata_playlist_help': '从音乐文件元数据中提取歌曲信息',
                'include_subfolders': '包含子文件夹',
                'generate_playlist_button': '生成播放列表',
                'select_music_folder': '选择音乐文件夹',
                'select_playlist_output': '选择播放列表输出文件',
                'playlist_files': '播放列表文件',
                'generating_playlist': '正在生成播放列表...',
                'playlist_generated_successfully': '播放列表生成成功',
                'playlist_generation_failed': '播放列表生成失败: {}',
                'folder_analysis_title': '文件夹分析',

                # v1.2 新功能 - 播放列表比较器
                'playlist_comparator_tab': '播放列表比较器',
                'playlist1': '播放列表 1:',
                'playlist2': '播放列表 2:',
                'comparison_output_folder': '比较结果输出文件夹:',
                'similarity_threshold_label': '相似度阈值:',
                'compare_playlists_button': '比较播放列表',
                'select_playlist1': '选择播放列表 1',
                'select_playlist2': '选择播放列表 2',
                'select_comparison_output': '选择比较结果输出文件夹',
                'comparing_playlists': '正在比较播放列表...',
                'playlists_compared_successfully': '播放列表比较完成',
                'playlist_comparison_failed': '播放列表比较失败: {}',

                # 通用
                'main_features_tab': '音乐筛选复制',
                'all_files_required': '请确保所有必需的文件和文件夹都已选择！'
            }, 'en': {
                # Window title
                'window_title': 'Music Picker',

                # Language button
                'language_button': 'En/中',

                # Label texts
                'song_list_file': 'Song List (list.txt):',
                'music_library_path': 'Local Music Library Path:',
                'output_folder_path': 'Output Folder Path:',
                'log_output': 'Log:',
                'progress_na': 'Progress: N/A',
                # Button texts
                'browse_button': 'Browse...',
                'start_button': 'Start Processing',
                'stop_button': 'Stop',

                # Metadata matching options
                'use_metadata_matching': 'Use Metadata Matching',
                'metadata_help_text': 'Match based on song tag information for higher accuracy',
                'warning': 'Warning',

                # Dialog titles
                'select_song_list': 'Select Song List File',
                'select_music_library': 'Select Music Library Folder',
                'select_output_folder': 'Select Output Folder',
                'error_title': 'Error',
                'exit_title': 'Exit',
                'severe_error_title': 'Severe Error',

                # Message texts
                'all_paths_required': 'Please ensure all paths are selected!',
                'confirm_exit': 'Are you sure you want to exit?',
                'starting_process': 'Starting process...',
                'all_operations_complete': 'All operations completed.',
                'attempting_to_stop': 'Attempting to stop operation...',
                'operation_aborted': 'Operation aborted.',
                'processing_failed': 'Processing failed: {}',

                # Log messages
                'song_list_empty': 'Song list is empty, no operation needed.',
                'invalid_library_path': 'Error: Music library path \'{}\' is not a valid folder.',
                'output_folder_created': 'Output folder created: \'{}\'',
                'create_output_folder_failed': 'Error: Cannot create output folder \'{}\': {}',
                'starting_search': 'Starting search in \'{}\'...',
                'file_already_exists': 'Info: File \'{}\' already exists in target folder, skipping copy (from: {}).',
                'found_and_copied': 'Found and copied: \'{}\' -> \'{}\'',
                'copy_failed': 'Error: Failed to copy file \'{}\' to \'{}\': {}',
                'search_complete': 'Search completed. Found and copied {} unique songs.',
                'unfound_songs_header': 'The following songs may not be found in the music library (or naming mismatch):',
                'parse_warning': 'Warning: Cannot parse line \'{}\', skipping.',
                'file_not_found': 'Error: Song list file \'{}\' not found.',
                'parse_error': 'Error: Error occurred while parsing song list: {}',
                'load_song_list_failed': 'Failed to load song list, operation aborted.',
                'uncaught_error': 'Uncaught error occurred during processing: {}',
                # Progress text
                'progress_format': 'Progress: {}/{} ({:.2f}%)',
                'progress_na': 'Progress: N/A',
                # v1.2 New Features - Playlist Generator
                'playlist_generator_tab': 'Playlist Generator',
                'music_folder': 'Music Folder:',
                'playlist_output_file': 'Playlist Output File:',
                'use_metadata_for_playlist': 'Use Metadata Extraction',
                'metadata_playlist_help': 'Extract song information from music file metadata',
                'include_subfolders': 'Include Subfolders',
                'generate_playlist_button': 'Generate Playlist',
                'select_music_folder': 'Select Music Folder',
                'select_playlist_output': 'Select Playlist Output File',
                'playlist_files': 'Playlist Files',
                'generating_playlist': 'Generating playlist...',
                'playlist_generated_successfully': 'Playlist generated successfully',
                'playlist_generation_failed': 'Playlist generation failed: {}',
                'folder_analysis_title': 'Folder Analysis',

                # v1.2 New Features - Playlist Comparator
                'playlist_comparator_tab': 'Playlist Comparator',
                'playlist1': 'Playlist 1:',
                'playlist2': 'Playlist 2:',
                'comparison_output_folder': 'Comparison Output Folder:',
                'similarity_threshold_label': 'Similarity Threshold:',
                'compare_playlists_button': 'Compare Playlists',
                'select_playlist1': 'Select Playlist 1',
                'select_playlist2': 'Select Playlist 2',
                'select_comparison_output': 'Select Comparison Output Folder',
                'comparing_playlists': 'Comparing playlists...',
                'playlists_compared_successfully': 'Playlist comparison completed',
                'playlist_comparison_failed': 'Playlist comparison failed: {}',

                # Common
                'main_features_tab': 'Music Filter & Copy',
                'all_files_required': 'Please ensure all required files and folders are selected!'
            }
        }
        return translations

    def get_language(self):
        """获取当前语言"""
        return self.current_language

    def set_language(self, language):
        """设置语言"""
        if language in self.translations:
            self.current_language = language
            return True
        return False

    def t(self, key, *args):
        """翻译函数"""
        try:
            text = self.translations[self.current_language].get(key, key)
            if args:
                return text.format(*args)
            return text
        except BaseException:
            return key


def detect_system_language():
    """检测系统语言"""
    try:
        system_locale = locale.getdefaultlocale()[0]
        if system_locale and system_locale.startswith('zh'):
            return 'zh'
        else:
            return 'en'
    except BaseException:
        return 'zh'  # 默认中文
