#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EzCut Installation Test Script
测试EzCut安装是否成功的脚本
"""

import sys
import os
import subprocess

def test_python_version():
    """测试Python版本"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Version too old (requires 3.8+)")
        return False

def test_conda_environment():
    """测试Conda环境"""
    print("\nTesting Conda environment...")
    try:
        # 检查是否在conda环境中
        conda_env = os.environ.get('CONDA_DEFAULT_ENV')
        if conda_env:
            print(f"✓ Running in Conda environment: {conda_env}")
            return True
        else:
            print("✗ Not running in a Conda environment")
            return False
    except Exception as e:
        print(f"✗ Error checking Conda environment: {e}")
        return False

def test_core_dependencies():
    """测试核心依赖"""
    print("\nTesting core dependencies...")
    dependencies = {
        'tkinter': 'GUI framework',
        'cv2': 'OpenCV for video processing',
        'numpy': 'Numerical computing',
        'PIL': 'Image processing (Pillow)',
        'pysrt': 'Subtitle file handling'
    }
    
    all_ok = True
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {module} - {description}")
        except ImportError:
            print(f"✗ {module} - {description} (MISSING)")
            all_ok = False
    
    return all_ok

def test_optional_dependencies():
    """测试可选依赖"""
    print("\nTesting optional dependencies...")
    optional_deps = {
        'moviepy.editor': 'Video editing capabilities',
        'whisper': 'AI speech recognition',
        'faster_whisper': 'Faster speech recognition'
    }
    
    for module, description in optional_deps.items():
        try:
            __import__(module)
            print(f"✓ {module} - {description}")
        except ImportError:
            print(f"⚠ {module} - {description} (Optional, not installed)")

def test_project_structure():
    """测试项目结构"""
    print("\nTesting project structure...")
    required_files = [
        'main.py',
        'config.json',
        'environment.yml',
        'requirements.txt',
        'src/__init__.py',
        'src/gui/main_window.py',
        'src/utils/config.py'
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (MISSING)")
            all_ok = False
    
    return all_ok

def test_ffmpeg():
    """测试FFmpeg"""
    print("\nTesting FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg available: {version_line}")
            return True
        else:
            print("✗ FFmpeg not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ FFmpeg not found in PATH")
        return False
    except Exception as e:
        print(f"✗ Error testing FFmpeg: {e}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("  EzCut Installation Test")
    print("  EzCut 安装测试")
    print("="*60)
    
    tests = [
        test_python_version,
        test_conda_environment,
        test_core_dependencies,
        test_project_structure,
        test_ffmpeg
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # 测试可选依赖（不影响总体结果）
    test_optional_dependencies()
    
    print("\n" + "="*60)
    print("  Test Results / 测试结果")
    print("="*60)
    
    if all(results):
        print("✓ All tests passed! EzCut is ready to use.")
        print("✓ 所有测试通过！EzCut可以正常使用。")
        print("\nTo start EzCut, run: run_conda.bat")
        print("启动EzCut，请运行: run_conda.bat")
        return 0
    else:
        print("✗ Some tests failed. Please check the installation.")
        print("✗ 部分测试失败，请检查安装。")
        print("\nTry running: install.bat")
        print("尝试运行: install.bat")
        return 1

if __name__ == "__main__":
    sys.exit(main())