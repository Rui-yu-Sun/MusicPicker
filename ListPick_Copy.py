import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading # 用于在后台运行耗时操作
import os
import shutil

# --- 核心逻辑函数 ---
def parse_song_list(file_path):
    songs_to_find = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.rsplit(' - ', 1)
                if len(parts) == 2:
                    song_title = parts[0].strip().lower()
                    artist = parts[1].strip().lower()
                    songs_to_find.append({'title': song_title, 'artist': artist, 'original_line': line})
                else:
                    log_message(f"警告: 无法解析行 '{line}'，跳过。") # 使用GUI的日志函数
    except FileNotFoundError:
        log_message(f"错误: 歌曲列表文件 '{file_path}' 未找到。")
        return None
    except Exception as e:
        log_message(f"错误: 解析歌曲列表时发生错误: {e}")
        return None
    return songs_to_find

def find_and_copy_songs_gui(songs_to_find, library_path, output_path, progress_callback):
    if not songs_to_find:
        log_message("歌曲列表为空，无需操作。")
        return

    if not os.path.isdir(library_path):
        log_message(f"错误: 音乐库路径 '{library_path}' 不是一个有效的文件夹。")
        return

    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path)
            log_message(f"已创建输出文件夹: '{output_path}'")
        except OSError as e:
            log_message(f"错误: 无法创建输出文件夹 '{output_path}': {e}")
            return
    
    found_count = 0
    copied_files_log = []
    total_songs_to_check = len(songs_to_find)
    processed_songs = 0

    log_message(f"\n开始在 '{library_path}' 中搜索歌曲...")

    # 优化：先创建一个基于 list.txt 条目的查找状态字典
    song_status = {song_info['original_line']: False for song_info in songs_to_find}


    for root, _, files in os.walk(library_path):
        if not app_running: # 允许中途停止
            log_message("操作已中止。")
            return

        for filename in files:
            if not app_running:
                log_message("操作已中止。")
                return

            if not filename.lower().endswith(('.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg')):
                continue

            file_path = os.path.join(root, filename)
            filename_no_ext = os.path.splitext(filename)[0].lower()

            # 遍历待查找列表，而不是反过来，这样可以更快地标记已找到的条目
            for song_info in songs_to_find:
                if song_status[song_info['original_line']]: # 如果这个条目已经找到匹配并处理过了
                    continue

                if song_info['title'] in filename_no_ext and song_info['artist'] in filename_no_ext:
                    destination_path = os.path.join(output_path, filename)
                    try:
                        if os.path.exists(destination_path):
                            log_message(f"提示: 文件 '{filename}' 已存在于目标文件夹，跳过复制 (来自: {song_info['original_line']})。")
                        else:
                            shutil.copy2(file_path, destination_path)
                            log_message(f"找到并复制: '{song_info['original_line']}' -> '{filename}'")
                            found_count += 1
                        
                        song_status[song_info['original_line']] = True # 标记此 list.txt 条目已处理
                        # processed_songs +=1 # 这个计数应该在外部循环song_to_find时更新，或者用len(song_status)中为True的数量
                        
                        # 更新进度 (简单地基于已处理的 list.txt 条目)
                        # count_processed_in_list = sum(1 for status in song_status.values() if status)
                        # progress_callback(count_processed_in_list, total_songs_to_check)

                        break # 处理下一个库文件
                    except Exception as e:
                        log_message(f"错误: 复制文件 '{file_path}' 到 '{destination_path}' 失败: {e}")
        
        # 稍微精确一点的进度更新方式（基于遍历完一个文件夹）
        # 这里的进度更新比较粗略，可以考虑更细致的进度条
        # processed_songs +=1 # 这种方式不太对
        # progress_callback(processed_songs, total_songs_to_check) # 这个逻辑可能需要调整

    log_message(f"\n搜索完成。共找到并复制 {found_count} 首不同的歌曲。")
    
    unfound_songs = [line for line, found in song_status.items() if not found]
    if unfound_songs:
        log_message("\n以下歌曲可能未在音乐库中找到（或命名不匹配）：")
        for original_line in unfound_songs:
            log_message(f"- {original_line}")
    
    progress_callback(total_songs_to_check, total_songs_to_check) # 确保最后进度条满

# --- GUI部分 ---
app_running = True # 用于控制后台线程停止

def select_file(entry_widget):
    filepath = filedialog.askopenfilename(
        title="选择歌曲列表文件",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    if filepath:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filepath)

def select_folder(entry_widget, title="选择文件夹"):
    folderpath = filedialog.askdirectory(title=title)
    if folderpath:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folderpath)

def log_message(message):
    log_area.insert(tk.END, message + "\n")
    log_area.see(tk.END) # 自动滚动到底部
    root.update_idletasks() # 强制更新UI，确保日志实时显示

def update_progress(current, total):
    # 简单文本进度，可以替换为tk.ttk.Progressbar
    if total > 0:
        percentage = (current / total) * 100
        progress_label.config(text=f"进度: {current}/{total} ({percentage:.2f}%)")
    else:
        progress_label.config(text="进度: N/A")
    root.update_idletasks()


def process_files_thread():
    global app_running
    app_running = True
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    log_message("开始处理...")

    list_file = list_file_entry.get()
    music_lib = music_lib_entry.get()
    output_dir = output_dir_entry.get()

    if not all([list_file, music_lib, output_dir]):
        messagebox.showerror("错误", "请确保所有路径都已选择！")
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        return

    songs = parse_song_list(list_file)
    if songs:
        try:
            find_and_copy_songs_gui(songs, music_lib, output_dir, update_progress)
        except Exception as e:
            log_message(f"处理过程中发生未捕获的错误: {e}")
            messagebox.showerror("严重错误", f"处理失败: {e}")
        finally: # 无论成功失败都重置按钮状态
            start_button.config(state=tk.NORMAL)
            stop_button.config(state=tk.DISABLED)
            if app_running: # 如果不是被中止的
                 log_message("所有操作完成。")
    else:
        log_message("未能加载歌曲列表，操作中止。")
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)


def start_processing():
    # 创建并启动一个新线程来运行耗时任务
    thread = threading.Thread(target=process_files_thread, daemon=True) # daemon=True 确保主窗口关闭时线程也关闭
    thread.start()

def stop_processing():
    global app_running
    log_message("正在尝试停止操作...")
    app_running = False # 设置标志，让后台线程检测并退出
    # 注意：这种停止方式不是立即的，取决于后台线程检查 app_running 的频率
    # 对于文件复制这种IO密集型操作，可能不会很快响应停止
    start_button.config(state=tk.NORMAL) # 允许用户重新开始
    stop_button.config(state=tk.DISABLED)


# --- 创建主窗口 ---
root = tk.Tk()
root.title("歌曲筛选复制工具")

# --- 控件 ---
# 歌曲列表文件
tk.Label(root, text="歌曲列表 (list.txt):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
list_file_entry = tk.Entry(root, width=50)
list_file_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="浏览...", command=lambda: select_file(list_file_entry)).grid(row=0, column=2, padx=5, pady=5)

# 音乐库路径
tk.Label(root, text="本地音乐库路径:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
music_lib_entry = tk.Entry(root, width=50)
music_lib_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="浏览...", command=lambda: select_folder(music_lib_entry, "选择音乐库文件夹")).grid(row=1, column=2, padx=5, pady=5)

# 输出文件夹路径
tk.Label(root, text="输出文件夹路径:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="浏览...", command=lambda: select_folder(output_dir_entry, "选择输出文件夹")).grid(row=2, column=2, padx=5, pady=5)

# 开始按钮
start_button = tk.Button(root, text="开始筛选复制", command=start_processing, width=15, height=2)
start_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10) # (row=3, column=1, padx=5, pady=10)

# 停止按钮 (可选)
stop_button = tk.Button(root, text="停止", command=stop_processing, width=10, state=tk.DISABLED)
stop_button.grid(row=3, column=2, padx=5, pady=10, sticky="w")


# 进度标签
progress_label = tk.Label(root, text="进度: N/A")
progress_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="w")

# 日志区域
tk.Label(root, text="日志:").grid(row=5, column=0, padx=5, pady=5, sticky="nw")
log_area = scrolledtext.ScrolledText(root, width=70, height=15, wrap=tk.WORD)
log_area.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

# --- 运行主循环 ---
def on_closing():
    global app_running
    if messagebox.askokcancel("退出", "确定要退出程序吗？"):
        app_running = False # 尝试停止任何正在运行的线程
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

# 目录结构示例：
# ListPick_Copy/
# ├── README.md
# ├── ListPick_Copy.py
# ├── requirements.txt
# ├── .gitignore
# ├── example/
# │   └── sample_list.txt
# └── docs/
#     └── screenshots/
