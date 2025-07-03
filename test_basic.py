#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本功能测试脚本

用于验证EzCut的核心功能是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from src.video_processor import VideoProcessor, VideoSegment
        print("✓ 视频处理模块导入成功")
    except ImportError as e:
        print(f"✗ 视频处理模块导入失败: {e}")
        return False
    
    try:
        from src.subtitle_manager import SubtitleManager, SubtitleStyle, SubtitleItem
        print("✓ 字幕管理模块导入成功")
    except ImportError as e:
        print(f"✗ 字幕管理模块导入失败: {e}")
        return False
    
    try:
        from src.utils.config import Config
        print("✓ 配置管理模块导入成功")
    except ImportError as e:
        print(f"✗ 配置管理模块导入失败: {e}")
        return False
    
    try:
        from src.gui.main_window import MainWindow
        print("✓ GUI模块导入成功")
    except ImportError as e:
        print(f"✗ GUI模块导入失败: {e}")
        return False
    
    return True

def test_dependencies():
    """测试依赖包"""
    print("\n测试依赖包...")
    
    dependencies = [
        ('cv2', 'opencv-python'),
        ('moviepy', 'moviepy'),
        ('PIL', 'Pillow'),
        ('pysrt', 'pysrt'),
        ('numpy', 'numpy'),
        ('tkinter', 'tkinter (内置)')
    ]
    
    all_ok = True
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {package_name} 可用")
        except ImportError:
            print(f"✗ {package_name} 不可用")
            all_ok = False
    
    # 测试可选依赖
    optional_deps = [
        ('whisper', 'openai-whisper'),
        ('faster_whisper', 'faster-whisper')
    ]
    
    print("\n可选依赖:")
    for module_name, package_name in optional_deps:
        try:
            __import__(module_name)
            print(f"✓ {package_name} 可用")
        except ImportError:
            print(f"- {package_name} 不可用 (可选)")
    
    return all_ok

def test_config():
    """测试配置管理"""
    print("\n测试配置管理...")
    
    try:
        from src.utils.config import Config
        
        # 创建配置实例
        config = Config("test_config.json")
        
        # 测试获取配置
        window_width = config.get('app.window_width', 1200)
        print(f"✓ 获取配置成功: window_width = {window_width}")
        
        # 测试设置配置
        config.set('test.value', 'hello')
        value = config.get('test.value')
        if value == 'hello':
            print("✓ 设置配置成功")
        else:
            print("✗ 设置配置失败")
            return False
        
        # 测试配置验证
        if config.validate_config():
            print("✓ 配置验证通过")
        else:
            print("✗ 配置验证失败")
            return False
        
        # 清理测试文件
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置管理测试失败: {e}")
        return False

def test_video_processor():
    """测试视频处理器"""
    print("\n测试视频处理器...")
    
    try:
        from src.video_processor import VideoProcessor, VideoSegment
        
        # 创建视频处理器实例
        processor = VideoProcessor()
        print("✓ 视频处理器创建成功")
        
        # 测试视频片段
        segment = VideoSegment(0.0, 10.0)
        if segment.duration == 10.0:
            print("✓ 视频片段创建成功")
        else:
            print("✗ 视频片段创建失败")
            return False
        
        # 测试添加片段
        processor.segments.append(segment)
        if len(processor.segments) == 1:
            print("✓ 添加视频片段成功")
        else:
            print("✗ 添加视频片段失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 视频处理器测试失败: {e}")
        return False

def test_subtitle_manager():
    """测试字幕管理器"""
    print("\n测试字幕管理器...")
    
    try:
        from src.subtitle_manager import SubtitleManager, SubtitleStyle, SubtitleItem
        
        # 创建字幕管理器实例
        manager = SubtitleManager()
        print("✓ 字幕管理器创建成功")
        
        # 测试字幕样式
        style = SubtitleStyle(font_size=20, font_color="#FF0000")
        if style.font_size == 20 and style.font_color == "#FF0000":
            print("✓ 字幕样式创建成功")
        else:
            print("✗ 字幕样式创建失败")
            return False
        
        # 测试添加字幕
        subtitle = manager.add_subtitle(0.0, 5.0, "测试字幕")
        if len(manager.subtitles) == 1 and subtitle.text == "测试字幕":
            print("✓ 添加字幕成功")
        else:
            print("✗ 添加字幕失败")
            return False
        
        # 测试获取字幕信息
        info = manager.get_subtitles_info()
        if len(info) == 1 and info[0]['text'] == "测试字幕":
            print("✓ 获取字幕信息成功")
        else:
            print("✗ 获取字幕信息失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 字幕管理器测试失败: {e}")
        return False

def test_directories():
    """测试目录创建"""
    print("\n测试目录创建...")
    
    directories = ['temp', 'output', 'fonts']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            if os.path.exists(directory):
                print(f"✓ 目录 {directory} 创建成功")
            else:
                print(f"✗ 目录 {directory} 创建失败")
                return False
        except Exception as e:
            print(f"✗ 目录 {directory} 创建失败: {e}")
            return False
    
    return True

def main():
    """主测试函数"""
    print("EzCut 基本功能测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_dependencies,
        test_directories,
        test_config,
        test_video_processor,
        test_subtitle_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ 测试 {test_func.__name__} 出现异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！EzCut 基本功能正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)