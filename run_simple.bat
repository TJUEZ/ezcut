@echo off
chcp 65001 >nul 2>&1

echo ========================================
echo    EzCut - Smart Video Editing Software
echo ========================================
echo.

echo Starting EzCut...
echo Please wait for the GUI to appear...
echo.

REM Create directories if needed
if not exist "temp" mkdir temp
if not exist "output" mkdir output
if not exist "fonts" mkdir fonts

REM Start the program
conda run -n ezcut python main.py

echo.
echo Program finished. Press any key to exit...
pause