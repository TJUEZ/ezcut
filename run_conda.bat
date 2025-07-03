@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo    EzCut - Smart Video Editing Software
echo    (Conda Environment Version)
echo ========================================
echo.

REM Check if conda is installed
echo Checking Conda installation...
conda --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda not found, please run install.bat first
    pause
    exit /b 1
)

REM Check if ezcut environment exists
echo Checking EzCut environment...
conda info --envs | findstr /i ezcut >nul 2>&1
if errorlevel 1 (
    echo ERROR: ezcut environment not found, please run install.bat first
    echo Available environments:
    conda info --envs
    pause
    exit /b 1
)
echo EzCut environment found.

REM Use conda run instead of activate for better compatibility
echo Starting EzCut with conda run...

REM Create necessary directories
echo Creating necessary directories...
if not exist "temp" mkdir temp
if not exist "output" mkdir output
if not exist "fonts" mkdir fonts

REM Start the program using conda run
echo Starting EzCut...
echo If the program window doesn't appear, check taskbar or minimized windows
echo.
echo Running: conda run -n ezcut python main.py
echo Please wait for the GUI to load...
echo.

REM Run with error output capture
conda run -n ezcut python main.py 2>&1
set EXIT_CODE=%errorlevel%

REM Check program exit status
echo.
echo Program finished with exit code: %EXIT_CODE%
if %EXIT_CODE% neq 0 (
    echo.
    echo ERROR: Program encountered an error (exit code: %EXIT_CODE%)
    echo Possible solutions:
    echo 1. Check if all dependencies are installed: python check_environment.py
    echo 2. Re-run install.bat to reinstall dependencies
    echo 3. Try running directly: conda activate ezcut ^&^& python main.py
    echo 4. Check if display/GUI is working properly
    pause
) else (
    echo.
    echo Program exited normally
    echo If GUI didn't appear, it might have started in background
    echo Check taskbar or try Alt+Tab to find the window
)

echo.
echo To restart EzCut, run this batch file again
echo To install dependencies, run install.bat
pause