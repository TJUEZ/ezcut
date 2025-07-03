@echo off
chcp 65001 >nul 2>&1

echo Testing conda run command...
conda run -n ezcut python -c "print('Python works in ezcut environment')"
echo Exit code: %errorlevel%

echo.
echo Testing main.py directly...
conda run -n ezcut python main.py
echo Exit code: %errorlevel%

echo.
echo Test complete.
pause