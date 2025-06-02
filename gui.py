"""
图形界面模块 - 统一字体大小
"""
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import threading
import logging
from config import *


class MusicPickerGUI:
    def __init__(self, translator, music_processor):
        self.translator = translator
        self.music_processor = music_processor
        self.metadata_processor = None  # 将通过外部设置
        self.playlist_generator = None  # v1.2 播放列表生成器
        self.playlist_comparator = None  # v1.2 播放列表比较器
        self.root = None
        self.widgets = {}
        self.browse_buttons = []
        self.notebook = None  # 选项卡控件
        self.logger = logging.getLogger(__name__)

    def create_window(self):
        """创建主窗口"""
        self.root = tk.Tk()
        self.root.title(self.translator.t('window_title'))
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(*WINDOW_MIN_SIZE)

        # 配置窗口自适应
        self._configure_window_resize()

        # 创建主框架
        self.main_frame = tk.Frame(
            self.root,
            padx=MAIN_PADDING,
            pady=MAIN_PADDING,
            bg=COLORS['bg_main']
        )
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # 配置主框架权重
        self.main_frame.grid_rowconfigure(0, weight=0)  # 头部区域 - 固定高度
        self.main_frame.grid_rowconfigure(1, weight=4)  # 选项卡区域 - 更大权重
        self.main_frame.grid_rowconfigure(2, weight=0)  # 日志标题 - 固定高度
        self.main_frame.grid_rowconfigure(3, weight=1)  # 日志区域 - 较小权重
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 创建控件
        self._create_widgets()

        # 设置事件处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        return self.root

    def _configure_window_resize(self):
        """配置窗口自适应"""
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _create_widgets(self):
        """创建所有控件 - 使用选项卡界面"""
        # 顶部：语言切换按钮（右上角）
        self._create_header()

        # 创建选项卡界面
        self._create_notebook()

        # 创建各个选项卡
        self._create_main_tab()        # 原有的音乐筛选复制功能
        self._create_generator_tab()   # v1.2 播放列表生成器
        self._create_comparator_tab()  # v1.2 播放列表比较器

        # 共享日志区域（在选项卡下方）
        self._create_log_area()

    def _create_header(self):
        """创建顶部区域"""
        # 语言切换按钮放在右上角
        self.widgets['lang_button'] = tk.Button(
            self.main_frame,
            command=self._change_language,
            font=FONTS['button'],  # 使用按钮字体
            relief='raised',
            bd=1
        )
        self.widgets['lang_button'].grid(
            row=0, column=0, padx=ENTRY_PADDING, pady=(0, 10), sticky="e")

    def _create_main_file_selection(self, parent):
        """创建主选项卡的文件选择区域"""
        # 歌曲列表文件
        self.widgets['song_list_label'] = tk.Label(
            parent,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['song_list_label'].grid(
            row=0,
            column=0,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        self.widgets['list_file_entry'] = tk.Entry(
            parent, font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['list_file_entry'].grid(
            row=0,
            column=1,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        browse_btn1 = tk.Button(
            parent,
            command=lambda: self._select_file(
                self.widgets['list_file_entry'], 'select_song_list'),
            font=FONTS['button'],
            relief='raised',
            bd=2,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH
        )
        browse_btn1.grid(row=0, column=2, padx=ENTRY_PADDING,
                         pady=ENTRY_PADDING, sticky="ew")
        self.browse_buttons.append(browse_btn1)

        # 音乐库路径
        self.widgets['music_lib_label'] = tk.Label(
            parent,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['music_lib_label'].grid(
            row=1,
            column=0,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        self.widgets['music_lib_entry'] = tk.Entry(
            parent,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['music_lib_entry'].grid(
            row=1,
            column=1,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        browse_btn2 = tk.Button(
            parent,
            command=lambda: self._select_folder(
                self.widgets['music_lib_entry'], 'select_music_library'),
            font=FONTS['button'],
            relief='raised',
            bd=2,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH
        )
        browse_btn2.grid(row=1, column=2, padx=ENTRY_PADDING,
                         pady=ENTRY_PADDING, sticky="ew")
        self.browse_buttons.append(browse_btn2)

        # 输出文件夹路径
        self.widgets['output_dir_label'] = tk.Label(
            parent,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['output_dir_label'].grid(
            row=2,
            column=0,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        self.widgets['output_dir_entry'] = tk.Entry(
            parent,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['output_dir_entry'].grid(
            row=2,
            column=1,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        browse_btn3 = tk.Button(
            parent,
            command=lambda: self._select_folder(
                self.widgets['output_dir_entry'], 'select_output_folder'),
            font=FONTS['button'],
            relief='raised',
            bd=2,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH
        )
        browse_btn3.grid(row=2, column=2, padx=ENTRY_PADDING,
                         pady=ENTRY_PADDING, sticky="ew")
        self.browse_buttons.append(browse_btn3)

    def _create_main_metadata_options(self, parent):
        """创建主选项卡的元数据匹配选项"""
        # 创建元数据选项框架
        metadata_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        metadata_frame.grid(row=3, column=0, columnspan=3,
                            pady=(5, 0), sticky="ew")

        # 元数据匹配复选框 - 去掉说明文字
        self.use_metadata_var = tk.BooleanVar()
        self.widgets['metadata_checkbox'] = tk.Checkbutton(
            metadata_frame,
            variable=self.use_metadata_var,
            command=self._on_metadata_option_changed,
            font=FONTS['main'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_normal'],
            selectcolor=COLORS['bg_main'],
            activebackground=COLORS['bg_main'],
            activeforeground=COLORS['text_normal']
        )
        self.widgets['metadata_checkbox'].pack(
            side=tk.LEFT, padx=(ENTRY_PADDING, 5))

    def _on_metadata_option_changed(self):
        """元数据选项改变时的回调"""
        use_metadata = self.use_metadata_var.get()
        if hasattr(self, 'music_processor') and self.music_processor:
            self.music_processor.set_use_metadata_matching(use_metadata)

        # 显示提示信息
        if use_metadata:
            if hasattr(
                    self,
                    'metadata_processor') and self.metadata_processor and not self.metadata_processor.is_metadata_available():
                messagebox.showwarning(
                    "警告",
                    "元数据功能需要安装mutagen库。请运行: pip install mutagen"
                )
                self.use_metadata_var.set(False)
            else:
                self.log_message("已启用元数据匹配模式")
        else:
            self.log_message("已切换到文件名匹配模式")

    def _create_main_button_area(self, parent):
        """创建主选项卡的按钮区域 - 紧贴在浏览按钮下方"""
        # 开始按钮 - 放在第三列（浏览按钮下方）
        self.widgets['start_button'] = tk.Button(
            parent,
            command=self._start_processing,
            height=BUTTON_HEIGHT,
            font=FONTS['button'],
            relief='raised',
            bd=2,
            cursor='hand2',
            width=BUTTON_WIDTH
        )
        self.widgets['start_button'].grid(
            row=4,
            column=2,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")
        # 停止按钮 - 放在开始按钮下方
        self.widgets['stop_button'] = tk.Button(
            parent,
            command=self._stop_processing,
            state=tk.DISABLED,
            height=BUTTON_HEIGHT,
            font=FONTS['button'],
            relief='raised',
            bd=2,
            cursor='hand2',
            width=BUTTON_WIDTH
        )
        self.widgets['stop_button'].grid(
            row=5,
            column=2,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

    def _create_log_area(self):
        """创建共享日志区域"""
        # 日志标题和进度的容器
        log_header = tk.Frame(self.main_frame, bg=COLORS['bg_main'])
        log_header.grid(row=2, column=0, padx=ENTRY_PADDING,
                        pady=(15, 5), sticky="ew")
        log_header.grid_columnconfigure(0, weight=1)
        log_header.grid_columnconfigure(1, weight=1)

        # 日志标签（左边）
        self.widgets['log_label'] = tk.Label(
            log_header,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['log_label'].grid(row=0, column=0, sticky="w")

        # 进度标签（右边）
        self.widgets['progress_label'] = tk.Label(
            log_header,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='e'
        )
        self.widgets['progress_label'].grid(row=0, column=1, sticky="e")

        # 日志文本区域
        self.widgets['log_area'] = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            font=FONTS['log'],
            bg='white',
            fg=COLORS['text_normal'],
            relief='solid',
            bd=1,
            selectbackground='#3399ff',
            selectforeground='white'
        )
        self.widgets['log_area'].grid(
            row=3, column=0, padx=ENTRY_PADDING, pady=(
                0, ENTRY_PADDING), sticky="nsew")

    def _select_file(
            self,
            entry_widget,
            title_key='select_song_list',
            file_type='text_files'):
        """选择文件"""
        if file_type == 'playlist_files':
            filetypes = (("Playlist files", "*.txt"), ("All files", "*.*"))
        else:
            filetypes = (("Text files", "*.txt"), ("All files", "*.*"))

        filepath = filedialog.askopenfilename(
            title=self.translator.t(title_key),
            filetypes=filetypes
        )
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)

    def _select_folder(self, entry_widget, title_key):
        """选择文件夹"""
        folderpath = filedialog.askdirectory(
            title=self.translator.t(title_key))
        if folderpath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folderpath)

    def _select_save_file(
            self,
            entry_widget,
            title_key,
            file_type='text_files'):
        """选择保存文件"""
        if file_type == 'playlist_files':
            filetypes = (("Playlist files", "*.txt"), ("All files", "*.*"))
            defaultextension = ".txt"
        else:
            filetypes = (("Text files", "*.txt"), ("All files", "*.*"))
            defaultextension = ".txt"

        filepath = filedialog.asksaveasfilename(
            title=self.translator.t(title_key),
            filetypes=filetypes,
            defaultextension=defaultextension
        )
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)

    def _create_generator_options(self, parent):
        """创建播放列表生成器选项"""
        # 创建选项框架
        options_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        options_frame.grid(row=2, column=0, columnspan=3,
                           pady=(5, 0), sticky="ew")

        # 使用元数据复选框 - 去掉说明文字
        self.use_metadata_for_playlist_var = tk.BooleanVar(value=True)
        self.widgets['metadata_playlist_checkbox'] = tk.Checkbutton(
            options_frame,
            variable=self.use_metadata_for_playlist_var,
            font=FONTS['main'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_normal'],
            selectcolor=COLORS['bg_main'],
            activebackground=COLORS['bg_main'],
            activeforeground=COLORS['text_normal']
        )
        self.widgets['metadata_playlist_checkbox'].pack(
            side=tk.LEFT, padx=(ENTRY_PADDING, 20))

        # 包含子文件夹复选框 - 左移位置
        self.include_subfolders_var = tk.BooleanVar(value=True)
        self.widgets['subfolders_checkbox'] = tk.Checkbutton(
            options_frame,
            variable=self.include_subfolders_var,
            font=FONTS['main'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_normal'],
            selectcolor=COLORS['bg_main'],
            activebackground=COLORS['bg_main'],
            activeforeground=COLORS['text_normal']
        )
        self.widgets['subfolders_checkbox'].pack(
            side=tk.LEFT, padx=(0, ENTRY_PADDING))

    def _create_generator_button_area(self, parent):
        """创建播放列表生成器按钮区域"""
        # 生成播放列表按钮 - 放在第三列（浏览按钮下方）
        self.widgets['generate_playlist_button'] = tk.Button(
            parent,
            command=self._generate_playlist,
            height=BUTTON_HEIGHT,
            font=FONTS['button'],
            relief='raised',
            bd=2,
            cursor='hand2',
            width=BUTTON_WIDTH
        )
        self.widgets['generate_playlist_button'].grid(
            row=3, column=2, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")

    def _create_comparator_options(self, parent):
        """创建播放列表比较器选项"""
        # 创建选项框架
        options_frame = tk.Frame(parent, bg=COLORS['bg_main'])
        options_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

        # 相似度阈值
        threshold_label = tk.Label(
            options_frame,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        threshold_label.pack(side=tk.LEFT, padx=(ENTRY_PADDING, 5))

        self.similarity_threshold_var = tk.DoubleVar(value=0.8)
        threshold_scale = tk.Scale(
            options_frame,
            variable=self.similarity_threshold_var,
            from_=0.5, to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            length=200,
            font=FONTS['main'],
            bg=COLORS['bg_main'],
            fg=COLORS['text_normal'],
            highlightthickness=0
        )
        threshold_scale.pack(side=tk.LEFT, padx=(5, ENTRY_PADDING))

    def _create_comparator_button_area(self, parent):
        """创建播放列表比较器按钮区域"""        # 比较播放列表按钮 - 放在第三列（浏览按钮下方）
        self.widgets['compare_playlists_button'] = tk.Button(
            parent,
            command=self._compare_playlists,
            height=BUTTON_HEIGHT,
            font=FONTS['button'],
            relief='raised',
            bd=2,
            cursor='hand2',
            width=BUTTON_WIDTH
        )
        self.widgets['compare_playlists_button'].grid(
            row=4, column=2, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")

    def _create_notebook(self):
        """创建选项卡控件"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

    def _create_main_tab(self):
        """创建主要功能选项卡（原有的音乐筛选复制功能）"""
        # 创建选项卡框架 - 添加padding确保内容不会贴边
        main_tab = tk.Frame(self.notebook, bg=COLORS['bg_main'])
        main_tab.grid(sticky='nsew')  # 确保框架填充整个选项卡空间

        # 配置所有行的权重
        main_tab.grid_rowconfigure(0, weight=0)  # 歌曲列表行 - 固定高度
        main_tab.grid_rowconfigure(1, weight=0)  # 音乐库行 - 固定高度
        main_tab.grid_rowconfigure(2, weight=0)  # 输出目录行 - 固定高度
        main_tab.grid_rowconfigure(3, weight=0)  # 元数据选项行 - 固定高度
        main_tab.grid_rowconfigure(4, weight=0)  # 开始按钮行 - 固定高度
        main_tab.grid_rowconfigure(5, weight=0)  # 停止按钮行 - 固定高度
        main_tab.grid_rowconfigure(6, weight=1)  # 剩余空间，允许扩展
        main_tab.grid_columnconfigure(1, weight=3)  # 中间列权重更大
        main_tab.grid_columnconfigure(0, weight=1)  # 左列固定宽度
        main_tab.grid_columnconfigure(2, weight=1)  # 右列固定宽度

        # 文件选择区域
        self._create_main_file_selection(main_tab)

        # 元数据匹配选项
        self._create_main_metadata_options(main_tab)

        # 按钮区域
        self._create_main_button_area(main_tab)

        # 添加到选项卡
        self.notebook.add(
            main_tab, text=self.translator.t('main_features_tab'))

    def _create_generator_tab(self):
        """创建播放列表生成器选项卡"""
        # 创建选项卡框架 - 添加padding确保内容不会贴边
        gen_tab = tk.Frame(self.notebook, bg=COLORS['bg_main'])
        gen_tab.grid(sticky='nsew')  # 确保框架填充整个选项卡空间

        # 配置所有行的权重
        gen_tab.grid_rowconfigure(0, weight=0)  # 音乐文件夹行 - 固定高度
        gen_tab.grid_rowconfigure(1, weight=0)  # 播放列表输出行 - 固定高度
        gen_tab.grid_rowconfigure(2, weight=0)  # 选项行 - 固定高度
        gen_tab.grid_rowconfigure(3, weight=0)  # 按钮行 - 固定高度
        gen_tab.grid_rowconfigure(4, weight=1)  # 剩余空间，允许扩展
        gen_tab.grid_columnconfigure(1, weight=3)
        gen_tab.grid_columnconfigure(0, weight=1)
        gen_tab.grid_columnconfigure(2, weight=1)

        # 音乐文件夹选择
        self.widgets['music_folder_label'] = tk.Label(
            gen_tab,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['music_folder_label'].grid(
            row=0, column=0, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")

        self.widgets['music_folder_entry'] = tk.Entry(
            gen_tab,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['music_folder_entry'].grid(
            row=0, column=1, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")

        browse_music_btn = tk.Button(
            gen_tab,
            command=lambda: self._select_folder(
                self.widgets['music_folder_entry'], 'select_music_folder'),
            font=FONTS['button'],
            relief='raised',
            bd=2,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH
        )
        browse_music_btn.grid(
            row=0,
            column=2,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")
        self.browse_buttons.append(browse_music_btn)

        # 播放列表输出文件选择
        self.widgets['playlist_output_label'] = tk.Label(
            gen_tab,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['playlist_output_label'].grid(
            row=1, column=0, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")

        self.widgets['playlist_output_entry'] = tk.Entry(
            gen_tab,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['playlist_output_entry'].grid(
            row=1, column=1, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")

        browse_playlist_btn = tk.Button(
            gen_tab,
            command=lambda: self._select_save_file(
                self.widgets['playlist_output_entry'],
                'select_playlist_output',
                'playlist_files'),
            font=FONTS['button'],
            relief='raised',
            bd=2,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH)
        browse_playlist_btn.grid(
            row=1,
            column=2,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")
        self.browse_buttons.append(browse_playlist_btn)

        # 生成器选项
        self._create_generator_options(gen_tab)

        # 生成按钮
        self._create_generator_button_area(gen_tab)

        # 添加到选项卡
        self.notebook.add(gen_tab, text=self.translator.t(
            'playlist_generator_tab'))

    def _create_comparator_tab(self):
        """创建播放列表比较器选项卡"""
        # 创建选项卡框架 - 添加padding确保内容不会贴边
        comp_tab = tk.Frame(self.notebook, bg=COLORS['bg_main'])
        comp_tab.grid(sticky='nsew')  # 确保框架填充整个选项卡空间

        # 配置所有行的权重
        comp_tab.grid_rowconfigure(0, weight=0)  # 播放列表1行 - 固定高度
        comp_tab.grid_rowconfigure(1, weight=0)  # 播放列表2行 - 固定高度
        comp_tab.grid_rowconfigure(2, weight=0)  # 输出文件夹行 - 固定高度
        comp_tab.grid_rowconfigure(3, weight=0)  # 选项行 - 固定高度
        comp_tab.grid_rowconfigure(4, weight=0)  # 按钮行 - 固定高度
        comp_tab.grid_rowconfigure(5, weight=1)  # 剩余空间，允许扩展
        comp_tab.grid_columnconfigure(1, weight=3)
        comp_tab.grid_columnconfigure(0, weight=1)
        comp_tab.grid_columnconfigure(2, weight=1)

        # 播放列表 1 选择
        self.widgets['playlist1_label'] = tk.Label(
            comp_tab,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['playlist1_label'].grid(
            row=0,
            column=0,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        self.widgets['playlist1_entry'] = tk.Entry(
            comp_tab,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['playlist1_entry'].grid(
            row=0,
            column=1,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        browse_pl1_btn = tk.Button(
            comp_tab,
            command=lambda: self._select_file(
                self.widgets['playlist1_entry'],
                'select_playlist1',
                'playlist_files'),
            font=FONTS['button'],
            relief='raised',
            bd=2,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH)
        browse_pl1_btn.grid(row=0, column=2, padx=ENTRY_PADDING,
                            pady=ENTRY_PADDING, sticky="ew")
        self.browse_buttons.append(browse_pl1_btn)

        # 播放列表 2 选择
        self.widgets['playlist2_label'] = tk.Label(
            comp_tab,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['playlist2_label'].grid(
            row=1,
            column=0,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        self.widgets['playlist2_entry'] = tk.Entry(
            comp_tab,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['playlist2_entry'].grid(
            row=1,
            column=1,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")

        browse_pl2_btn = tk.Button(
            comp_tab,
            command=lambda: self._select_file(
                self.widgets['playlist2_entry'],
                'select_playlist2',
                'playlist_files'),
            font=FONTS['button'],
            relief='raised',
            bd=2,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH)
        browse_pl2_btn.grid(row=1, column=2, padx=ENTRY_PADDING,
                            pady=ENTRY_PADDING, sticky="ew")
        self.browse_buttons.append(browse_pl2_btn)

        # 比较结果输出文件夹选择
        self.widgets['comparison_output_label'] = tk.Label(
            comp_tab,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['comparison_output_label'].grid(
            row=2, column=0, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")

        self.widgets['comparison_output_entry'] = tk.Entry(
            comp_tab,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['comparison_output_entry'].grid(
            row=2, column=1, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")

        browse_comp_btn = tk.Button(
            comp_tab,
            command=lambda: self._select_folder(
                self.widgets['comparison_output_entry'],
                'select_comparison_output'),
            font=FONTS['button'],
            relief='raised',
            bd=2,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH)
        browse_comp_btn.grid(
            row=2,
            column=2,
            padx=ENTRY_PADDING,
            pady=ENTRY_PADDING,
            sticky="ew")
        self.browse_buttons.append(browse_comp_btn)

        # 比较器选项
        self._create_comparator_options(comp_tab)

        # 比较按钮
        self._create_comparator_button_area(comp_tab)

        # 添加到选项卡
        self.notebook.add(comp_tab, text=self.translator.t(
            'playlist_comparator_tab'))

    def _generate_playlist(self):
        """生成播放列表"""
        try:
            # 验证输入
            music_folder = self.widgets['music_folder_entry'].get().strip()
            output_file = self.widgets['playlist_output_entry'].get().strip()

            if not music_folder or not output_file:
                messagebox.showerror(
                    self.translator.t('error_title'),
                    self.translator.t('all_files_required')
                )
                return

            # 获取选项
            use_metadata = self.use_metadata_for_playlist_var.get()
            include_subfolders = self.include_subfolders_var.get()

            self.log_message(self.translator.t('generating_playlist'))

            def run_generation():
                try:
                    # 使用播放列表生成器
                    if self.playlist_generator:
                        result = self.playlist_generator.generate_playlist(
                            music_folder, output_file, use_metadata, include_subfolders)
                        if result:
                            self.log_message(self.translator.t(
                                'playlist_generated_successfully'))
                        else:
                            self.log_message(self.translator.t(
                                'playlist_generation_failed'))
                    else:
                        self.log_message("播放列表生成器未初始化")

                except Exception as e:
                    self.log_message(f"生成播放列表时出错: {str(e)}")

            # 在后台线程中运行
            thread = threading.Thread(target=run_generation)
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror(
                self.translator.t('error_title'),
                self.translator.t('playlist_generation_failed', str(e))
            )

    def _compare_playlists(self):
        """比较播放列表"""
        try:
            # 验证输入
            playlist1 = self.widgets['playlist1_entry'].get().strip()
            playlist2 = self.widgets['playlist2_entry'].get().strip()
            output_folder = self.widgets['comparison_output_entry'].get(
            ).strip()

            if not playlist1 or not playlist2 or not output_folder:
                messagebox.showerror(
                    self.translator.t('error_title'),
                    self.translator.t('all_files_required')
                )
                return

            # 获取相似度阈值
            similarity_threshold = self.similarity_threshold_var.get()

            self.log_message(self.translator.t('comparing_playlists'))

            def run_comparison():
                try:
                    # 使用播放列表比较器
                    if self.playlist_comparator:
                        result = self.playlist_comparator.compare_playlists(
                            playlist1, playlist2, output_folder, similarity_threshold
                        )
                        if result:
                            self.log_message(self.translator.t(
                                'playlists_compared_successfully'))
                        else:
                            self.log_message(self.translator.t(
                                'playlist_comparison_failed'))
                    else:
                        self.log_message("播放列表比较器未初始化")

                except Exception as e:
                    self.log_message(f"比较播放列表时出错: {str(e)}")

            # 在后台线程中运行
            thread = threading.Thread(target=run_comparison)
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror(
                self.translator.t('error_title'),
                self.translator.t('playlist_comparison_failed', str(e))
            )

    def _change_language(self):
        """切换语言"""
        if self.translator.get_language() == 'zh':
            self.translator.set_language('en')
        else:
            self.translator.set_language('zh')
        self.update_ui_language()

    def update_ui_language(self):
        """更新界面语言"""
        try:
            # 更新窗口标题
            if self.root:
                self.root.title(self.translator.t('window_title'))

            # 更新语言切换按钮
            self.widgets['lang_button'].config(
                text=self.translator.t('language_button'))

            # 更新主选项卡的标签
            self.widgets['song_list_label'].config(
                text=self.translator.t('song_list_file'))
            self.widgets['music_lib_label'].config(
                text=self.translator.t('music_library_path'))
            self.widgets['output_dir_label'].config(
                text=self.translator.t('output_folder_path'))
            self.widgets['metadata_checkbox'].config(
                text=self.translator.t('use_metadata_matching'))

            # 更新生成器选项卡的标签
            self.widgets['music_folder_label'].config(
                text=self.translator.t('music_folder'))
            self.widgets['playlist_output_label'].config(
                text=self.translator.t('playlist_output_file'))
            self.widgets['metadata_playlist_checkbox'].config(
                text=self.translator.t('use_metadata_for_playlist'))
            self.widgets['subfolders_checkbox'].config(
                text=self.translator.t('include_subfolders'))

            # 更新比较器选项卡的标签
            self.widgets['playlist1_label'].config(
                text=self.translator.t('playlist1'))
            self.widgets['playlist2_label'].config(
                text=self.translator.t('playlist2'))
            self.widgets['comparison_output_label'].config(
                text=self.translator.t('comparison_output_folder'))
            # 更新按钮文本
            self.widgets['start_button'].config(
                text=self.translator.t('start_button'))
            self.widgets['stop_button'].config(
                text=self.translator.t('stop_button'))
            self.widgets['generate_playlist_button'].config(
                text=self.translator.t('generate_playlist_button'))
            self.widgets['compare_playlists_button'].config(
                text=self.translator.t('compare_playlists_button'))

            # 更新浏览按钮文本
            for btn in self.browse_buttons:
                btn.config(text=self.translator.t('browse_button'))

            # 更新日志标签
            self.widgets['log_label'].config(
                text=self.translator.t('log_output'))

            # 更新进度标签 - 设置初始值为N/A
            self.widgets['progress_label'].config(
                text=self.translator.t('progress_na'))

            # 更新选项卡标题
            if hasattr(self, 'notebook') and self.notebook:
                # 获取当前选项卡的数量
                tab_count = self.notebook.index("end")
                if tab_count >= 1:
                    self.notebook.tab(
                        0, text=self.translator.t('main_features_tab'))
                if tab_count >= 2:
                    self.notebook.tab(1, text=self.translator.t(
                        'playlist_generator_tab'))
                if tab_count >= 3:
                    self.notebook.tab(2, text=self.translator.t(
                        'playlist_comparator_tab'))

        except Exception as e:
            self.logger.error(f"更新界面语言时出错: {e}")

    def log_message(self, message, level="INFO"):
        """在日志区域显示消息"""
        if 'log_area' in self.widgets:
            timestamp = threading.current_thread().ident
            log_line = f"[{level}] {message}\n"
            self.widgets['log_area'].insert(tk.END, log_line)
            self.widgets['log_area'].see(tk.END)

    def update_progress(self, current, total):
        """更新进度显示"""
        if 'progress_label' in self.widgets:
            progress_text = self.translator.t(
                'progress_format', current, total)
            self.widgets['progress_label'].config(text=progress_text)

    def set_metadata_processor(self, metadata_processor):
        """设置元数据处理器"""
        self.metadata_processor = metadata_processor

    def set_playlist_generator(self, playlist_generator):
        """设置播放列表生成器"""
        self.playlist_generator = playlist_generator

    def set_playlist_comparator(self, playlist_comparator):
        """设置播放列表比较器"""
        self.playlist_comparator = playlist_comparator

    def _start_processing(self):
        """开始处理"""
        try:
            # 验证输入
            list_file = self.widgets['list_file_entry'].get().strip()
            music_lib = self.widgets['music_lib_entry'].get().strip()
            output_dir = self.widgets['output_dir_entry'].get().strip()

            if not list_file or not music_lib or not output_dir:
                messagebox.showerror(
                    self.translator.t('error_title'),
                    self.translator.t('all_files_required')
                )
                return

            # 设置按钮状态
            self.widgets['start_button'].config(state=tk.DISABLED)
            self.widgets['stop_button'].config(state=tk.NORMAL)

            # 开始处理
            self.music_processor.start_processing(
                list_file, music_lib, output_dir)

        except Exception as e:
            messagebox.showerror(
                self.translator.t('error_title'),
                str(e)
            )
            # 重置按钮状态
            self.widgets['start_button'].config(state=tk.NORMAL)
            self.widgets['stop_button'].config(state=tk.DISABLED)

    def _stop_processing(self):
        """停止处理"""
        self.music_processor.stop_processing()
        # 重置按钮状态
        self.widgets['start_button'].config(state=tk.NORMAL)
        self.widgets['stop_button'].config(state=tk.DISABLED)

    def _on_closing(self):
        """窗口关闭事件"""
        if hasattr(self.music_processor, 'stop_processing'):
            self.music_processor.stop_processing()
        self.root.destroy()

    def show(self):
        """显示窗口"""
        if self.root:
            self.root.mainloop()
