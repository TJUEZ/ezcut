@echo off
chcp 65001 >nul
echo ========================================
echo    EzCut - 智能视频剪辑软件
echo ========================================
echo.
echo 正在启动程序...
echo.

:: 使用系统Python避免conda环境冲突
set PYTHON_PATH=C:\Python312\python.exe

:: 检查系统Python是否安装
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到系统Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查依赖是否安装
echo 检查依赖包...
%PYTHON_PATH% -m pip show opencv-python >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    %PYTHON_PATH% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)

:: 创建必要目录
if not exist "temp" mkdir temp
if not exist "output" mkdir output
if not exist "fonts" mkdir fonts

:: 启动程序
echo 启动EzCut...
%PYTHON_PATH% main.py

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)