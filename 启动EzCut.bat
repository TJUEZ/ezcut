@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo    🎬 EzCut - 专业视频编辑器
echo ========================================
echo.

echo 正在启动 EzCut PyQt6 视频编辑器...
echo.

:: 直接运行PyQt6版本的视频编辑器
python video_editor_qt.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 启动失败，错误代码: %ERRORLEVEL%
    echo.
    echo 💡 解决方案:
    echo 1. 确保已安装 Python 3.8+
    echo 2. 安装依赖: pip install PyQt6 opencv-python numpy pillow
    echo 3. 或运行: pip install -r requirements_qt.txt
    echo.
    echo 📋 如需完整安装指南，请查看 README.md
    echo.
)

echo.
echo 按任意键退出...
pause >nul