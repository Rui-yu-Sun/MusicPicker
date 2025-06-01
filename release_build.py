#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MusicPicker 自动发布脚本
用于准备和创建发布包
"""

import os
import shutil
import zipfile
from datetime import datetime
import subprocess
import sys

def get_version():
    """从config.py获取版本号"""
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            for line in f:
                if 'APP_VERSION' in line:
                    version = line.split('=')[1].strip().strip('"\'')
                    return version
    except:
        return "1.0.0"

def clean_build():
    """清理构建文件"""
    print("🧹 清理旧的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✓ 已清理 {dir_name}")

def build_exe():
    """构建exe文件"""
    print("🔨 开始构建exe文件...")
    
    try:
        # 运行pyinstaller
        result = subprocess.run(['pyinstaller', '--clean', 'MusicPicker.spec'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("   ✓ exe文件构建成功")
            return True
        else:
            print(f"   ❌ 构建失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ 构建失败: {e}")
        return False

def test_exe():
    """测试exe文件"""
    print("🧪 测试exe文件...")
    
    exe_path = os.path.join('dist', 'MusicPicker.exe')
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"   ✓ exe文件存在，大小: {file_size:.1f} MB")
        return True
    else:
        print("   ❌ exe文件不存在")
        return False

def create_release_package():
    """创建发布包"""
    version = get_version()
    package_name = f"MusicPicker-v{version}"
    
    print(f"📦 创建发布包: {package_name}")
    
    # 创建发布文件夹
    release_dir = f"release/{package_name}"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir, exist_ok=True)
    
    # 复制文件
    files_to_copy = [
        ('dist/MusicPicker.exe', 'MusicPicker.exe'),
        ('示例list.txt', '示例list.txt'),
        ('README.md', 'README.md'),
        ('RELEASE_NOTES.md', '发布说明.md'),
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            dst_path = os.path.join(release_dir, dst)
            shutil.copy2(src, dst_path)
            print(f"   ✓ 已复制 {dst}")
        else:
            print(f"   ⚠️  文件不存在: {src}")
    
    # 创建快速启动说明
    quick_start = """# MusicPicker 快速启动指南

## 🚀 立即开始

1. **双击 MusicPicker.exe 启动程序**

2. **准备歌曲列表**
   - 参考 "示例list.txt" 创建你的歌曲列表
   - 或者使用 GoMusic (https://music.unmeta.cn) 快速生成

3. **选择路径**
   - 歌曲列表: 你的 .txt 文件
   - 音乐库: 包含音乐文件的文件夹
   - 输出文件夹: 复制文件的目标位置

4. **开始处理**
   - 点击"开始筛选复制"
   - 查看实时进度和日志

## 📖 详细说明

请查看 "发布说明.md" 获取完整的使用指南。

## 🐛 问题反馈

- GitHub: https://github.com/username/MusicPicker/issues
- 邮箱: your-email@example.com

---
MusicPicker v""" + version + f" | {datetime.now().strftime('%Y年%m月%d日')}"
    
    with open(os.path.join(release_dir, '使用说明.txt'), 'w', encoding='utf-8') as f:
        f.write(quick_start)
    print("   ✓ 已创建 使用说明.txt")
    
    return release_dir

def create_zip_package(release_dir):
    """创建zip压缩包"""
    version = get_version()
    zip_name = f"MusicPicker-v{version}.zip"
    
    print(f"📮 创建zip压缩包: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, 'release')
                zipf.write(file_path, arc_name)
                print(f"   ✓ 已添加 {arc_name}")
    
    zip_size = os.path.getsize(zip_name) / (1024 * 1024)  # MB
    print(f"   ✓ 压缩包创建完成，大小: {zip_size:.1f} MB")
    
    return zip_name

def print_release_info():
    """打印发布信息"""
    version = get_version()
    print(f"""
🎉 MusicPicker v{version} 发布包准备完成！

📁 发布文件:
   • MusicPicker-v{version}.zip (完整发布包)
   • release/MusicPicker-v{version}/ (解压目录)

🚀 下一步:
   1. 测试发布包中的exe文件
   2. 上传到GitHub Releases
   3. 发布公告和说明

📋 GitHub Release 建议标题:
   MusicPicker v{version} - 智能音乐文件筛选复制工具

🏷️  建议标签:
   v{version}

📝 发布说明:
   请使用 RELEASE_NOTES.md 中的内容
""")

def main():
    """主函数"""
    print("🚀 MusicPicker 自动发布脚本")
    print("=" * 50)
    
    # 检查是否在正确的目录
    if not os.path.exists('MusicPicker.py'):
        print("❌ 请在项目根目录运行此脚本")
        return False
    
    success = True
    
    # 步骤1: 清理构建文件
    clean_build()
    print()
    
    # 步骤2: 构建exe
    if not build_exe():
        success = False
    print()
    
    # 步骤3: 测试exe
    if success and not test_exe():
        success = False
    print()
    
    if not success:
        print("❌ 发布准备失败，请检查错误信息")
        return False
    
    # 步骤4: 创建发布包
    release_dir = create_release_package()
    print()
    
    # 步骤5: 创建zip包
    zip_file = create_zip_package(release_dir)
    print()
    
    # 步骤6: 显示发布信息
    print_release_info()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  发布过程被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发布过程中出现错误: {e}")
        sys.exit(1)
