@echo off
chcp 65001 >nul
echo 🚀 MusicPicker 快速发布脚本
echo ================================

echo.
echo 📋 发布准备检查...
if not exist "MusicPicker.py" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

echo ✅ 项目文件检查通过
echo.

echo 🔧 开始自动发布流程...
python release_build.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 发布包创建成功！
    echo.
    echo 📂 打开发布文件夹？
    choice /C YN /M "是否打开release文件夹查看发布包"
    if !ERRORLEVEL! EQU 1 (
        if exist "release" start "" "release"
    )
) else (
    echo.
    echo ❌ 发布失败，请检查错误信息
)

echo.
pause
