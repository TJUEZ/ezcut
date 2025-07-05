#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EzCut - 智能视频剪辑软件

主要功能：
- 自动字幕识别和生成
- 字幕样式编辑和自定义字体
- 视频剪切、拖拽、缩放、移动
- 视频片段重新排序

参考项目：
- AutoCut: https://github.com/mli/autocut (字幕生成和视频剪切)
- Tailor: https://github.com/FutureUniant/Tailor (视频处理和优化)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import os
import sys
from pathlib import Path

# 尝试导入拖拽支持
try:
    import tkinterdnd2 as tkdnd
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# 导入自定义模块
from src.video_processor import VideoProcessor
from src.subtitle_manager import SubtitleManager
from src.gui.main_window import MainWindow
from src.gui.theme_manager import ThemeManager
from src.utils.config import Config

class EzCutApp:
    """EzCut主应用程序类"""
    
    def __init__(self):
        # 根据是否有拖拽支持选择不同的根窗口
        if DND_AVAILABLE:
            self.root = tkdnd.TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        self.root.title("EzCut - 智能视频剪辑软件")
        
        # 初始化配置
        self.config = Config()
        
        # 初始化主题管理器
        self.theme_manager = ThemeManager(self.config.config_data)
        
        # 应用主题和DPI适配
        self.theme_manager.apply_theme(self.root)
        
        # 设置窗口大小（考虑DPI缩放）
        width = self.theme_manager.scale_size(self.config.get('app.window_width', 1200))
        height = self.theme_manager.scale_size(self.config.get('app.window_height', 800))
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(self.theme_manager.scale_size(800), self.theme_manager.scale_size(600))
        
        # 初始化核心组件
        self.video_processor = VideoProcessor()
        self.subtitle_manager = SubtitleManager()
        
        # 创建主界面
        self.main_window = MainWindow(self.root, self)
        
        # 绑定事件
        self.setup_events()
    
    def get_theme_manager(self):
        """获取主题管理器"""
        return self.theme_manager
        
    def setup_events(self):
        """设置事件绑定"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """应用关闭时的处理"""
        if messagebox.askokcancel("退出", "确定要退出EzCut吗？"):
            self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("错误", f"应用程序运行出错：{str(e)}")
            sys.exit(1)

def check_environment():
    """检查运行环境"""
    print("EzCut - 智能视频剪辑软件")
    print("=" * 40)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 错误：需要Python 3.8或更高版本")
        print(f"当前版本：{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        sys.exit(1)
    
    print(f"✓ Python版本：{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # 检查conda环境
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print(f"✓ Conda环境：{conda_env}")
    else:
        print("ℹ 未检测到Conda环境，建议使用conda环境以获得最佳兼容性")
    
    # 检查依赖包
    missing_packages = []
    
    try:
        import cv2
        print("✓ OpenCV已安装")
    except ImportError:
        missing_packages.append("opencv-python")
        print("❌ OpenCV未安装")
    
    try:
        import numpy
        print("✓ NumPy已安装")
    except ImportError:
        missing_packages.append("numpy")
        print("❌ NumPy未安装")
    
    try:
        import PIL
        print("✓ Pillow已安装")
    except ImportError:
        missing_packages.append("Pillow")
        print("❌ Pillow未安装")
    
    # 检查可选依赖
    optional_missing = []
    
    try:
        import moviepy
        print("✓ MoviePy已安装 - 视频处理功能可用")
    except ImportError:
        optional_missing.append("moviepy")
        print("⚠ MoviePy未安装 - 高级视频处理功能不可用")
    
    try:
        import whisper
        print("✓ Whisper已安装 - 字幕识别功能可用")
    except ImportError:
        optional_missing.append("openai-whisper")
        print("⚠ Whisper未安装 - 自动字幕识别功能不可用")
    
    try:
        import tkinterdnd2
        print("✓ TkinterDnD2已安装 - 拖拽功能可用")
    except ImportError:
        optional_missing.append("tkinterdnd2")
        print("⚠ TkinterDnD2未安装 - 拖拽功能不可用")
    
    if missing_packages:
        print("\n❌ 缺少必需依赖包，程序无法正常运行")
        print("请安装以下包：")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\n安装命令：")
        if conda_env:
            print(f"  conda activate {conda_env}")
            print("  pip install -r requirements.txt")
        else:
            print("  pip install -r requirements.txt")
        print("\n或使用conda环境（推荐）：")
        print("  install.bat (Windows) 或 ./install.sh (macOS/Linux)")
        sys.exit(1)
    
    if optional_missing:
        print("\n⚠ 部分功能不可用，建议安装完整依赖")
        print("运行环境检查脚本获取详细信息：")
        print("  python check_environment.py")
    
    print("\n✓ 基础环境检查通过，启动程序...")
    print("=" * 40)

def main():
    """主函数"""
    # 检查运行环境
    check_environment()
    
    # 创建必要的目录
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("fonts", exist_ok=True)
    
    # 启动应用
    try:
        app = EzCutApp()
        app.run()
    except Exception as e:
        print(f"\n❌ 程序启动失败：{str(e)}")
        print("\n请尝试以下解决方案：")
        print("1. 运行环境检查：python check_environment.py")
        print("2. 重新安装依赖：pip install -r requirements.txt")
        print("3. 使用conda环境：install.bat 或 ./install.sh")
        sys.exit(1)

if __name__ == "__main__":
    main()