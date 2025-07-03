@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo    EzCut Debug Startup Script
echo ========================================
echo.

echo Step 1: Checking Conda installation...
conda --version
if errorlevel 1 (
    echo ERROR: Conda not found
    pause
    exit /b 1
)

echo Step 2: Checking EzCut environment...
conda env list | findstr ezcut
if errorlevel 1 (
    echo ERROR: ezcut environment not found
    pause
    exit /b 1
)

echo Step 3: Testing Python in ezcut environment...
conda run -n ezcut python --version
if errorlevel 1 (
    echo ERROR: Python not working in ezcut environment
    pause
    exit /b 1
)

echo Step 4: Testing basic imports...
conda run -n ezcut python -c "import tkinter; print('Tkinter OK')"
if errorlevel 1 (
    echo ERROR: Tkinter import failed
    pause
    exit /b 1
)

echo Step 5: Testing EzCut imports...
conda run -n ezcut python -c "from src.gui.main_window import MainWindow; print('EzCut imports OK')"
if errorlevel 1 (
    echo ERROR: EzCut imports failed
    pause
    exit /b 1
)

echo Step 6: Starting EzCut with verbose output...
echo If GUI doesn't appear, check for error messages below:
echo.
conda run -n ezcut python main.py

echo.
echo Debug complete. Press any key to exit...
pause