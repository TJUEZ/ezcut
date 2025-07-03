@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    EzCut Installation Script (Windows)
echo ========================================
echo.

REM Check if conda is installed
conda --version >nul 2>&1
if errorlevel 1 (
    echo Error: conda not found, please install Anaconda or Miniconda first
    echo Download: https://www.anaconda.com/products/distribution
    pause
    exit /b 1
)

echo Conda environment manager detected
echo.

REM Check if ezcut environment already exists
conda env list | findstr ezcut >nul 2>&1
if not errorlevel 1 (
    echo Existing ezcut environment detected
    set /p choice="Remove and recreate? (y/N): "
    if /i "!choice!"=="y" (
        echo Removing existing environment...
        conda env remove -n ezcut -y
    ) else (
        echo Using existing environment
        goto activate_env
    )
)

REM Create conda environment
echo Creating conda virtual environment...
conda env create -f environment.yml
if errorlevel 1 (
    echo Environment creation failed, trying manual creation...
    conda create -n ezcut python=3.9 -y
    call conda activate ezcut
    conda install -c conda-forge opencv numpy pillow tqdm requests -y
    pip install moviepy pysrt whisper faster-whisper
)

:activate_env
echo.
echo Activating conda environment...
call conda activate ezcut

REM Verify installation
echo Verifying installation...
python -c "import cv2, numpy, PIL, moviepy; print('All dependencies installed successfully!')" 2>nul
if errorlevel 1 (
    echo Warning: Some dependencies may not be installed correctly
)

REM Create necessary directories
if not exist "temp" mkdir temp
if not exist "output" mkdir output
if not exist "fonts" mkdir fonts

echo.
echo ========================================
echo Installation completed!
echo.
echo Usage:
echo 1. Run 'conda activate ezcut' to activate environment
echo 2. Run 'python main.py' to start the program
echo Or directly run 'run_conda.bat'
echo ========================================
pause