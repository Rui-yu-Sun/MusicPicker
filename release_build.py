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
import glob


def get_version():
    """从config.py获取版本号"""
    try:
        with open('config.py', 'r', encoding='utf-8') as f:
            for line in f:
                if 'APP_VERSION' in line:
                    version = line.split('=')[1].strip().strip('"\'')
                    return version
    except BaseException:
        return "1.0.0"


def format_code():
    """格式化Python代码"""
    print("🎨 格式化Python代码...")

    try:
        # 检查是否安装了autopep8
        result = subprocess.run(['autopep8', '--version'],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print("   ⚠️  autopep8未安装，尝试安装...")
            install_result = subprocess.run(['pip', 'install', 'autopep8'],
                                            capture_output=True, text=True)
            if install_result.returncode != 0:
                print(f"   ❌ 安装autopep8失败: {install_result.stderr}")
                return False
            print("   ✓ autopep8安装成功")

        # 格式化所有Python文件
        python_files = glob.glob("*.py")
        formatted_count = 0

        for py_file in python_files:
            # 跳过一些不需要格式化的文件
            if py_file in ['release_build.py', 'release_build_fixed.py']:
                continue

            try:
                format_result = subprocess.run([
                    'autopep8',
                    '--in-place',
                    '--aggressive',
                    '--aggressive',
                    py_file
                ], capture_output=True, text=True)

                if format_result.returncode == 0:
                    print(f"   ✓ 已格式化 {py_file}")
                    formatted_count += 1
                else:
                    print(f"   ⚠️  格式化失败 {py_file}: {format_result.stderr}")
            except Exception as e:
                print(f"   ⚠️  格式化 {py_file} 时出错: {e}")

        print(f"   ✓ 完成格式化，共处理 {formatted_count} 个文件")
        return True

    except Exception as e:
        print(f"   ❌ 代码格式化失败: {e}")
        return False


def force_remove_dir(dir_path):
    """强制删除目录，处理权限和占用问题"""
    import stat
    import time

    def handle_remove_readonly(func, path, exc):
        """处理只读文件删除问题"""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    try:
        # 方法1: 使用 shutil.rmtree 带错误处理
        shutil.rmtree(dir_path, onerror=handle_remove_readonly)
        return True
    except Exception:
        pass

    try:
        # 方法2: 使用 Windows 命令行强制删除
        if os.name == 'nt':  # Windows
            result = subprocess.run([
                'cmd', '/c', 'rmdir', '/s', '/q', dir_path
            ], capture_output=True, text=True)
            if result.returncode == 0:
                return True
    except Exception:
        pass

    try:
        # 方法3: 使用 PowerShell 强制删除
        if os.name == 'nt':  # Windows
            result = subprocess.run([
                'powershell', '-Command',
                f'Remove-Item -Path "{dir_path}" -Recurse -Force -ErrorAction SilentlyContinue'
            ], capture_output=True, text=True)
            if result.returncode == 0 or not os.path.exists(dir_path):
                return True
    except Exception:
        pass

    try:
        # 方法4: 逐个文件删除
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.chmod(file_path, stat.S_IWRITE)
                    os.remove(file_path)
                except Exception:
                    pass
            for dir_name in dirs:
                dir_full_path = os.path.join(root, dir_name)
                try:
                    os.rmdir(dir_full_path)
                except Exception:
                    pass
        os.rmdir(dir_path)
        return True
    except Exception:
        pass

    # 如果所有方法都失败，检查目录是否仍然存在
    return not os.path.exists(dir_path)


def clean_build():
    """清理构建文件"""
    print("🧹 清理旧的构建文件...")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            if not force_remove_dir(dir_name):
                print(f"   ⚠️  无法完全清理 {dir_name}，尝试继续...")
            else:
                print(f"   ✓ 已清理 {dir_name}")


def clean_python_cache():
    """清理Python缓存文件"""
    print("🧹 清理Python缓存文件...")

    # 清理所有 .pyc 文件
    pyc_files = glob.glob("**/*.pyc", recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"   ✓ 已删除 {pyc_file}")
        except Exception as e:
            print(f"   ⚠️  无法删除 {pyc_file}: {e}")

    # 清理所有 __pycache__ 目录
    pycache_dirs = []
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_dirs.append(os.path.join(root, dir_name))

    for pycache_dir in pycache_dirs:
        if force_remove_dir(pycache_dir):
            print(f"   ✓ 已清理 {pycache_dir}")
        else:
            print(f"   ⚠️  无法清理 {pycache_dir}")


def prepare_build_environment():
    """准备构建环境"""
    print("🛠️  准备构建环境...")

    # 检查必需的工具
    tools_to_check = [
        ('pyinstaller', 'PyInstaller'),
        ('python', 'Python'),
    ]

    for tool, name in tools_to_check:
        try:
            result = subprocess.run([tool, '--version'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                version_info = result.stdout.strip().split('\n')[0]
                print(f"   ✓ {name}: {version_info}")
            else:
                print(f"   ❌ {name} 未找到")
                return False
        except FileNotFoundError:
            print(f"   ❌ {name} 未安装")
            return False
        except Exception as e:
            print(f"   ⚠️  检查 {name} 时出错: {e}")

    return True


def build_exe():
    """构建exe文件"""
    print("🔨 开始构建exe文件...")

    try:
        # 运行pyinstaller
        result = subprocess.run(['pyinstaller',
                                 '--clean',
                                 'MusicPicker.spec'],
                                capture_output=True,
                                text=True,
                                encoding='utf-8')

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

    print(f"📦 创建发布包: {package_name}")    # 创建发布文件夹
    release_dir = f"release/{package_name}"
    if os.path.exists(release_dir):
        if not force_remove_dir(release_dir):
            print(f"   ⚠️  无法删除旧的发布目录: {release_dir}")

    os.makedirs(release_dir, exist_ok=True)    # 复制文件
    files_to_copy = [
        ('dist/MusicPicker.exe', 'MusicPicker.exe'),
        ('示例list.txt', '示例list.txt'),
        ('README.md', 'README.md'),
        ('CHANGELOG.md', 'CHANGELOG.md'),
        ('使用说明.txt', '使用说明.txt'),
    ]

    for src, dst in files_to_copy:
        if os.path.exists(src):
            dst_path = os.path.join(release_dir, dst)
            shutil.copy2(src, dst_path)
            print(f"   ✓ 已复制 {dst}")
        else:
            print(f"   ⚠️  文件不存在: {src}")

    return release_dir


def create_zip_package(release_dir):
    """创建zip压缩包"""
    version = get_version()
    zip_name = f"MusicPicker-v{version}.zip"

    # 确保release目录存在
    os.makedirs('release', exist_ok=True)

    # 压缩包放在release文件夹下
    zip_path = os.path.join('release', zip_name)

    print(f"📮 创建zip压缩包: {zip_path}")

    # 如果zip文件已存在，先删除
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
            print(f"   ✓ 已删除旧的zip文件")
        except Exception as e:
            print(f"   ⚠️  无法删除旧zip文件: {e}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, 'release')
                zipf.write(file_path, arc_name)
                print(f"   ✓ 已添加 {arc_name}")

    zip_size = os.path.getsize(zip_path) / (1024 * 1024)  # MB
    print(f"   ✓ 压缩包创建完成，大小: {zip_size:.1f} MB")

    return zip_path


def print_release_info():
    """打印发布信息"""
    version = get_version()
    print(f"""
🎉 MusicPicker v{version} 发布包准备完成！

📁 发布文件:
   • release/MusicPicker-v{version}.zip (完整发布包)
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
   请使用 CHANGELOG.md 中的内容
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

    # 步骤0: 准备构建环境
    if not prepare_build_environment():
        print("❌ 构建环境检查失败")
        return False
    print()

    # 步骤1: 格式化代码
    if not format_code():
        print("⚠️  代码格式化失败，但继续构建过程...")
    print()

    # 步骤2: 清理Python缓存
    clean_python_cache()
    print()

    # 步骤3: 清理构建文件
    clean_build()
    print()

    # 步骤4: 构建exe
    if not build_exe():
        success = False
    print()

    # 步骤5: 测试exe
    if success and not test_exe():
        success = False
    print()

    if not success:
        print("❌ 发布准备失败，请检查错误信息")
        return False

    # 步骤6: 创建发布包
    release_dir = create_release_package()
    print()

    # 步骤7: 创建zip包
    zip_file = create_zip_package(release_dir)
    print()

    # 步骤8: 显示发布信息
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
