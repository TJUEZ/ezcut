#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检查脚本
用于验证EzCut运行环境的兼容性
"""

import sys
import os
import platform
import subprocess
import importlib
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

def print_status(item, status, details=""):
    """打印状态信息"""
    status_symbol = "✓" if status else "✗"
    print(f"{status_symbol} {item:<30} {details}")

def check_python_version():
    """检查Python版本"""
    print_header("Python环境检查")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    is_valid = version >= (3, 8)
    
    print_status("Python版本", is_valid, f"v{version_str}")
    print_status("Python路径", True, sys.executable)
    
    return is_valid

def check_system_info():
    """检查系统信息"""
    print_header("系统信息")
    
    system = platform.system()
    release = platform.release()
    machine = platform.machine()
    
    print_status("操作系统", True, f"{system} {release}")
    print_status("架构", True, machine)
    print_status("工作目录", True, os.getcwd())
    
    return True

def check_conda_environment():
    """检查Conda环境"""
    print_header("Conda环境检查")
    
    # 检查conda是否可用
    try:
        result = subprocess.run(['conda', '--version'], 
                              capture_output=True, text=True, timeout=10)
        conda_available = result.returncode == 0
        conda_version = result.stdout.strip() if conda_available else "未安装"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        conda_available = False
        conda_version = "未安装"
    
    print_status("Conda可用性", conda_available, conda_version)
    
    # 检查当前环境
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', '未激活')
    in_conda_env = conda_env != '未激活'
    print_status("当前Conda环境", in_conda_env, conda_env)
    
    # 检查ezcut环境是否存在
    ezcut_env_exists = False
    if conda_available:
        try:
            result = subprocess.run(['conda', 'env', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            ezcut_env_exists = 'ezcut' in result.stdout
        except subprocess.TimeoutExpired:
            pass
    
    print_status("EzCut环境存在", ezcut_env_exists)
    
    return conda_available, in_conda_env, ezcut_env_exists

def check_required_packages():
    """检查必需的Python包"""
    print_header("Python包检查")
    
    required_packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'tkinter': 'tkinter (内置)',
        'tqdm': 'tqdm',
        'requests': 'requests'
    }
    
    optional_packages = {
        'moviepy': 'moviepy',
        'pysrt': 'pysrt',
        'whisper': 'openai-whisper',
        'faster_whisper': 'faster-whisper'
    }
    
    all_available = True
    
    # 检查必需包
    for module, package in required_packages.items():
        try:
            importlib.import_module(module)
            print_status(f"必需: {package}", True, "已安装")
        except ImportError:
            print_status(f"必需: {package}", False, "未安装")
            all_available = False
    
    # 检查可选包
    for module, package in optional_packages.items():
        try:
            importlib.import_module(module)
            print_status(f"可选: {package}", True, "已安装")
        except ImportError:
            print_status(f"可选: {package}", False, "未安装")
    
    return all_available

def check_ffmpeg():
    """检查FFmpeg"""
    print_header("FFmpeg检查")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        ffmpeg_available = result.returncode == 0
        if ffmpeg_available:
            version_line = result.stdout.split('\n')[0]
            version = version_line.split(' ')[2] if len(version_line.split(' ')) > 2 else "未知版本"
        else:
            version = "未安装"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        ffmpeg_available = False
        version = "未安装"
    
    print_status("FFmpeg可用性", ffmpeg_available, version)
    
    return ffmpeg_available

def check_project_structure():
    """检查项目结构"""
    print_header("项目结构检查")
    
    required_files = [
        'main.py',
        'environment.yml',
        'requirements.txt',
        'config.json'
    ]
    
    required_dirs = [
        'src',
        'src/gui',
        'src/utils'
    ]
    
    optional_dirs = [
        'temp',
        'output',
        'fonts'
    ]
    
    all_files_exist = True
    
    # 检查必需文件
    for file in required_files:
        exists = Path(file).exists()
        print_status(f"文件: {file}", exists)
        if not exists:
            all_files_exist = False
    
    # 检查必需目录
    for dir in required_dirs:
        exists = Path(dir).exists()
        print_status(f"目录: {dir}", exists)
        if not exists:
            all_files_exist = False
    
    # 检查可选目录
    for dir in optional_dirs:
        exists = Path(dir).exists()
        print_status(f"可选目录: {dir}", exists)
    
    return all_files_exist

def provide_recommendations(results):
    """提供修复建议"""
    print_header("修复建议")
    
    python_ok, conda_available, in_conda_env, ezcut_env_exists, packages_ok, ffmpeg_ok, structure_ok = results
    
    if not python_ok:
        print("❌ Python版本过低，请升级到3.8或更高版本")
    
    if not conda_available:
        print("❌ 未安装Conda，建议安装Anaconda或Miniconda")
        print("   下载地址: https://www.anaconda.com/products/distribution")
    
    if conda_available and not ezcut_env_exists:
        print("❌ 未找到ezcut环境，请运行安装脚本:")
        if platform.system() == "Windows":
            print("   install.bat")
        else:
            print("   ./install.sh")
    
    if not packages_ok:
        print("❌ 缺少必需的Python包，请安装依赖:")
        if conda_available and ezcut_env_exists:
            print("   conda activate ezcut")
            print("   pip install -r requirements.txt")
        else:
            print("   pip install -r requirements.txt")
    
    if not ffmpeg_ok:
        print("❌ 未安装FFmpeg，视频处理功能将不可用")
        if conda_available:
            print("   conda install -c conda-forge ffmpeg")
        else:
            print("   请从 https://ffmpeg.org/download.html 下载并安装")
    
    if not structure_ok:
        print("❌ 项目文件不完整，请重新下载项目")
    
    if all(results):
        print("✅ 环境检查通过！可以正常运行EzCut")
        print("\n启动命令:")
        if conda_available and ezcut_env_exists:
            if platform.system() == "Windows":
                print("   run_conda.bat")
            else:
                print("   ./run_conda.sh")
        else:
            print("   python main.py")

def main():
    """主函数"""
    print("EzCut 环境兼容性检查工具")
    print(f"检查时间: {platform.node()} - {sys.version}")
    
    # 执行各项检查
    python_ok = check_python_version()
    check_system_info()
    conda_available, in_conda_env, ezcut_env_exists = check_conda_environment()
    packages_ok = check_required_packages()
    ffmpeg_ok = check_ffmpeg()
    structure_ok = check_project_structure()
    
    # 提供建议
    results = (python_ok, conda_available, in_conda_env, ezcut_env_exists, 
              packages_ok, ffmpeg_ok, structure_ok)
    provide_recommendations(results)

if __name__ == "__main__":
    main()