"""
图形界面模块 - 统一字体大小
"""
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import logging
from config import *

class MusicPickerGUI:
    def __init__(self, translator, music_processor):
        self.translator = translator
        self.music_processor = music_processor
        self.metadata_processor = None  # 将通过外部设置
        self.root = None
        self.widgets = {}
        self.browse_buttons = []
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
        
        # 配置主框架权重 - 对称布局
        self.main_frame.grid_rowconfigure(7, weight=1)  # 日志区域可扩展
        self.main_frame.grid_columnconfigure(1, weight=3)  # 中间列权重更大
        self.main_frame.grid_columnconfigure(0, weight=1)  # 左列固定宽度
        self.main_frame.grid_columnconfigure(2, weight=1)  # 右列固定宽度
        
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
        """创建所有控件 - 统一字体"""
        # 顶部：语言切换按钮（右上角）
        self._create_header()
        
        # 中部：文件选择区域
        self._create_file_selection_area()
        
        # 元数据匹配选项
        self._create_metadata_options()
        
        # 按钮区域
        self._create_button_area()
        
        # 日志区域（包含进度显示）
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
        self.widgets['lang_button'].grid(row=0, column=2, padx=ENTRY_PADDING, pady=(0, 10), sticky="e")
    
    def _create_file_selection_area(self):
        """创建文件选择区域 - 统一字体大小"""
        # 歌曲列表文件
        self.widgets['song_list_label'] = tk.Label(
            self.main_frame,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['song_list_label'].grid(row=1, column=0, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")
        
        self.widgets['list_file_entry'] = tk.Entry(
            self.main_frame,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['list_file_entry'].grid(row=1, column=1, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")
        
        browse_btn1 = tk.Button(
            self.main_frame, 
            command=lambda: self._select_file(self.widgets['list_file_entry']),
            font=FONTS['button'],
            relief='raised',
            bd=1
        )
        browse_btn1.grid(row=1, column=2, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")
        self.browse_buttons.append(browse_btn1)
        
        # 音乐库路径
        self.widgets['music_lib_label'] = tk.Label(
            self.main_frame,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['music_lib_label'].grid(row=2, column=0, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")
        
        self.widgets['music_lib_entry'] = tk.Entry(
            self.main_frame,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['music_lib_entry'].grid(row=2, column=1, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")
        
        browse_btn2 = tk.Button(
            self.main_frame, 
            command=lambda: self._select_folder(self.widgets['music_lib_entry'], 'select_music_library'),
            font=FONTS['button'],
            relief='raised',
            bd=1
        )
        browse_btn2.grid(row=2, column=2, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")
        self.browse_buttons.append(browse_btn2)
        
        # 输出文件夹路径
        self.widgets['output_dir_label'] = tk.Label(
            self.main_frame,
            font=FONTS['main'],
            fg=COLORS['text_normal'],
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['output_dir_label'].grid(row=3, column=0, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")
        
        self.widgets['output_dir_entry'] = tk.Entry(
            self.main_frame,
            font=FONTS['main'],
            bg=COLORS['entry_bg'],
            relief='solid',
            bd=1
        )
        self.widgets['output_dir_entry'].grid(row=3, column=1, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")
        
        browse_btn3 = tk.Button(
            self.main_frame, 
            command=lambda: self._select_folder(self.widgets['output_dir_entry'], 'select_output_folder'),
            font=FONTS['button'],
            relief='raised',
            bd=1
        )
        browse_btn3.grid(row=3, column=2, padx=ENTRY_PADDING, pady=ENTRY_PADDING, sticky="ew")
        self.browse_buttons.append(browse_btn3)
    
    def _create_metadata_options(self):
        """创建元数据匹配选项"""
        # 创建元数据选项框架
        metadata_frame = tk.Frame(self.main_frame, bg=COLORS['bg_main'])
        metadata_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")
        
        # 元数据匹配复选框
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
        self.widgets['metadata_checkbox'].pack(side=tk.LEFT, padx=(ENTRY_PADDING, 5))
        
        # 说明文字
        self.widgets['metadata_help_label'] = tk.Label(
            metadata_frame,
            font=FONTS['main'],
            fg='gray',
            bg=COLORS['bg_main'],
            anchor='w'
        )
        self.widgets['metadata_help_label'].pack(side=tk.LEFT, padx=(0, ENTRY_PADDING))
    
    def _on_metadata_option_changed(self):
        """元数据选项改变时的回调"""
        use_metadata = self.use_metadata_var.get()
        if hasattr(self, 'music_processor') and self.music_processor:
            self.music_processor.set_use_metadata_matching(use_metadata)
            
        # 显示提示信息
        if use_metadata:
            if hasattr(self, 'metadata_processor') and self.metadata_processor and not self.metadata_processor.is_metadata_available():
                messagebox.showwarning(
                    "警告",
                    "元数据功能需要安装mutagen库。请运行: pip install mutagen"
                )
                self.use_metadata_var.set(False)
            else:
                self.log_message("已启用元数据匹配模式")
        else:
            self.log_message("已切换到文件名匹配模式")
    
    def _create_button_area(self):
        """创建按钮区域 - 居中对称"""
        # 创建按钮容器框架
        button_container = tk.Frame(self.main_frame, bg=COLORS['bg_main'])
        button_container.grid(row=5, column=0, columnspan=3, pady=20, sticky="ew")
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(1, weight=0)
        button_container.grid_columnconfigure(2, weight=0)
        button_container.grid_columnconfigure(3, weight=1)
        
        # 开始按钮
        self.widgets['start_button'] = tk.Button(
            button_container, 
            command=self._start_processing, 
            height=BUTTON_HEIGHT, 
            font=FONTS['button'],
            relief='raised',
            bd=2,
            cursor='hand2',
            width=15
        )
        self.widgets['start_button'].grid(row=0, column=1, padx=10, pady=5)
        
        # 停止按钮
        self.widgets['stop_button'] = tk.Button(
            button_container, 
            command=self._stop_processing, 
            state=tk.DISABLED, 
            height=BUTTON_HEIGHT,
            font=FONTS['button'],
            relief='raised',
            bd=2,
            cursor='hand2',
            width=10
        )
        self.widgets['stop_button'].grid(row=0, column=2, padx=10, pady=5)
    
    def _create_log_area(self):
        """创建日志区域 - 统一字体"""
        # 日志标题和进度的容器
        log_header = tk.Frame(self.main_frame, bg=COLORS['bg_main'])
        log_header.grid(row=6, column=0, columnspan=3, padx=ENTRY_PADDING, pady=(15, 5), sticky="ew")
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
        self.widgets['log_area'].grid(row=7, column=0, columnspan=3, padx=ENTRY_PADDING, pady=(0, ENTRY_PADDING), sticky="nsew")
    
    def _select_file(self, entry_widget):
        """选择文件"""
        filepath = filedialog.askopenfilename(
            title=self.translator.t('select_song_list'),
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)
    
    def _select_folder(self, entry_widget, title_key):
        """选择文件夹"""
        folderpath = filedialog.askdirectory(title=self.translator.t(title_key))
        if folderpath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folderpath)
    
    def log_message(self, message):
        """显示日志消息并记录到文件"""
        # 显示在GUI中
        self.widgets['log_area'].insert(tk.END, message + "\n")
        self.widgets['log_area'].see(tk.END)
        self.root.update_idletasks()
        
        # 同时记录到日志文件
        self.logger.info(message)
    
    def update_progress(self, current, total):
        """更新进度显示"""
        if total > 0:
            percentage = (current / total) * 100
            text = self.translator.t('progress_format', current, total, percentage)
        else:
            text = self.translator.t('progress_na')
        
        self.widgets['progress_label'].config(text=text)
        self.root.update_idletasks()
    
    def _start_processing(self):
        """开始处理"""
        self.widgets['start_button'].config(state=tk.DISABLED)
        self.widgets['stop_button'].config(state=tk.NORMAL)
        
        # 获取路径
        list_file = self.widgets['list_file_entry'].get()
        music_lib = self.widgets['music_lib_entry'].get()
        output_dir = self.widgets['output_dir_entry'].get()
        
        if not all([list_file, music_lib, output_dir]):
            messagebox.showerror(
                self.translator.t('error_title'), 
                self.translator.t('all_paths_required')
            )
            self._reset_buttons()
            return
        
        # 在新线程中处理
        thread = threading.Thread(
            target=self._process_files_thread, 
            args=(list_file, music_lib, output_dir),
            daemon=True
        )
        thread.start()
    
    def _process_files_thread(self, list_file, music_lib, output_dir):
        """处理文件的线程函数"""
        try:
            self.music_processor.start()
            self.log_message(self.translator.t('starting_process'))
            
            # 解析歌曲列表
            songs = self.music_processor.parse_song_list(list_file)
            if songs:
                # 开始处理
                self.music_processor.find_and_copy_songs(
                    songs, music_lib, output_dir, self.update_progress
                )
            else:
                self.log_message(self.translator.t('load_song_list_failed'))
                
        except Exception as e:
            self.log_message(self.translator.t('uncaught_error', e))
            messagebox.showerror(
                self.translator.t('severe_error_title'), 
                self.translator.t('processing_failed', e)
            )
        finally:
            self._reset_buttons()
            if self.music_processor.is_running:
                self.log_message(self.translator.t('all_operations_complete'))
    
    def _stop_processing(self):
        """停止处理"""
        self.log_message(self.translator.t('attempting_to_stop'))
        self.music_processor.stop()
        self._reset_buttons()
    
    def _reset_buttons(self):
        """重置按钮状态"""
        self.widgets['start_button'].config(state=tk.NORMAL)
        self.widgets['stop_button'].config(state=tk.DISABLED)
    
    def _change_language(self):
        """切换语言"""
        current = self.translator.get_language()
        new_language = 'en' if current == 'zh' else 'zh'
        self.translator.set_language(new_language)
        self.update_ui_language()
    
    def update_ui_language(self):
        """更新UI语言"""
        self.root.title(self.translator.t('window_title'))
        
        # 更新标签
        self.widgets['song_list_label'].config(text=self.translator.t('song_list_label'))
        self.widgets['music_lib_label'].config(text=self.translator.t('music_library_label'))
        self.widgets['output_dir_label'].config(text=self.translator.t('output_folder_label'))
        self.widgets['log_label'].config(text=self.translator.t('log_label'))
        
        # 更新元数据选项
        self.widgets['metadata_checkbox'].config(text=self.translator.t('use_metadata_matching'))
        self.widgets['metadata_help_label'].config(text=self.translator.t('metadata_help_text'))
        
        # 更新按钮
        for browse_btn in self.browse_buttons:
            browse_btn.config(text=self.translator.t('browse_button'))
        
        self.widgets['start_button'].config(text=self.translator.t('start_button'))
        self.widgets['stop_button'].config(text=self.translator.t('stop_button'))
        
        # 更新语言按钮
        current_lang = self.translator.get_language()
        self.widgets['lang_button'].config(text='中文' if current_lang == 'en' else 'English')
        
        # 更新进度标签
        self.widgets['progress_label'].config(text=self.translator.t('progress_na'))
    
    def _on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel(
            self.translator.t('exit_title'), 
            self.translator.t('confirm_exit')
        ):
            self.music_processor.stop()
            self.root.destroy()
    
    def run(self):
        """运行GUI"""
        if self.root:
            self.root.mainloop()
