#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EzCut 视频编辑器启动脚本

使用方法:
1. 双击运行此脚本
2. 或在命令行运行: python start.py
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """检查核心依赖包"""
    required_packages = {
        'PyQt6': 'PyQt6',
        'cv2': 'opencv-python', 
        'numpy': 'numpy',
        'PIL': 'pillow'
    }
    
    # 可选依赖包
    optional_packages = {
        'moviepy': 'moviepy'
    }
    
    missing_packages = []
    
    # 检查核心依赖
    for import_name, package_name in required_packages.items():
        try:
            if import_name == 'cv2':
                import cv2
            elif import_name == 'PIL':
                import PIL
            else:
                __import__(import_name)
            print(f"✅ {package_name} 已安装")
        except ImportError:
            print(f"❌ {package_name} 未安装")
            missing_packages.append(package_name)
    
    # 检查可选依赖
    for import_name, package_name in optional_packages.items():
        try:
            if import_name == 'moviepy':
                import moviepy
                # 尝试导入editor模块
                try:
                    import moviepy.editor
                    print(f"✅ {package_name} 已安装 (完整版本)")
                except ImportError:
                    print(f"⚠️  {package_name} 已安装但editor模块缺失，建议重新安装: pip install --upgrade moviepy")
            else:
                __import__(import_name)
                print(f"✅ {package_name} 已安装")
        except ImportError:
            print(f"⚠️  {package_name} 未安装 (可选，用于高级视频编辑功能)")
            print(f"   安装命令: pip install {package_name}")
    
    return missing_packages

def install_dependencies(packages):
    """安装缺失的依赖包"""
    print(f"📦 正在安装: {' '.join(packages)}")
    try:
        cmd = [sys.executable, "-m", "pip", "install"] + packages
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def run_editor():
    """启动视频编辑器"""
    editor_file = Path(__file__).parent / "video_editor_qt.py"
    
    if not editor_file.exists():
        print("❌ 找不到 video_editor_qt.py 文件")
        return False
    
    print("🚀 启动 EzCut 视频编辑器...")
    try:
        # 使用subprocess启动，避免导入问题
        result = subprocess.run([sys.executable, str(editor_file)], 
                              cwd=str(editor_file.parent))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🎬 EzCut 专业视频编辑器")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        input("\n按回车键退出...")
        return
    
    # 检查依赖
    print("\n📋 检查依赖包...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        response = input("是否自动安装? (y/n): ").lower().strip()
        
        if response in ['y', 'yes', '是', '']:
            if install_dependencies(missing_packages):
                # 重新检查
                missing_packages = check_dependencies()
                if missing_packages:
                    print(f"❌ 仍有依赖包未安装: {', '.join(missing_packages)}")
                    input("\n按回车键退出...")
                    return
            else:
                input("\n按回车键退出...")
                return
        else:
            print("\n💡 请手动安装依赖包:")
            print(f"pip install {' '.join(missing_packages)}")
            input("\n按回车键退出...")
            return
    
    print("\n✅ 所有依赖检查通过")
    print("-" * 30)
    
    # 启动编辑器
    if not run_editor():
        input("\n按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 意外错误: {e}")
        input("\n按回车键退出...")