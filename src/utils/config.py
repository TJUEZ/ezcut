#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块

功能：
- 应用程序配置管理
- 用户设置保存和加载
- 默认参数设置
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config_data = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            # 应用程序设置
            "app": {
                "window_width": 1200,
                "window_height": 800,
                "theme": "clam",
                "language": "zh_CN"
            },
            
            # 视频处理设置
            "video": {
                "default_bitrate": "10M",
                "output_format": "mp4",
                "preview_quality": "medium",
                "temp_dir": "temp",
                "output_dir": "output"
            },
            
            # 字幕设置
            "subtitle": {
                "whisper_model": "base",
                "use_faster_whisper": True,
                "default_language": "auto",
                "font_family": "Microsoft YaHei",
                "font_size": 24,
                "font_color": "#FFFFFF",
                "background_color": "#000000",
                "background_opacity": 0.7,
                "position": "bottom",
                "alignment": "center"
            },
            
            # 界面设置
            "ui": {
                "show_toolbar": True,
                "show_statusbar": True,
                "auto_save": True,
                "auto_save_interval": 300,  # 秒
                "recent_files_count": 10
            },
            
            # 性能设置
            "performance": {
                "max_threads": 4,
                "memory_limit": "2GB",
                "gpu_acceleration": False,
                "cache_size": "1GB"
            }
        }
    
    def load_config(self) -> bool:
        """从文件加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # 合并配置，保留默认值
                self._merge_config(self.config_data, loaded_config)
                print(f"配置文件加载成功: {self.config_file}")
                return True
            else:
                print("配置文件不存在，使用默认配置")
                return False
                
        except Exception as e:
            print(f"配置文件加载失败: {str(e)}，使用默认配置")
            return False
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            print(f"配置文件保存成功: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"配置文件保存失败: {str(e)}")
            return False
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]):
        """合并配置，保留默认值"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
    
    def get(self, key_path: str, default_value: Any = None) -> Any:
        """获取配置值
        
        Args:
            key_path: 配置键路径，如 'video.bitrate' 或 'subtitle.font_size'
            default_value: 默认值
        
        Returns:
            配置值
        """
        keys = key_path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default_value
    
    def set(self, key_path: str, value: Any) -> bool:
        """设置配置值
        
        Args:
            key_path: 配置键路径
            value: 配置值
        
        Returns:
            是否设置成功
        """
        keys = key_path.split('.')
        current = self.config_data
        
        try:
            # 导航到父级
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # 设置值
            current[keys[-1]] = value
            return True
            
        except Exception as e:
            print(f"设置配置失败: {str(e)}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置段
        
        Args:
            section: 配置段名称，如 'video', 'subtitle'
        
        Returns:
            配置段字典
        """
        return self.config_data.get(section, {})
    
    def set_section(self, section: str, config: Dict[str, Any]) -> bool:
        """设置配置段
        
        Args:
            section: 配置段名称
            config: 配置字典
        
        Returns:
            是否设置成功
        """
        try:
            self.config_data[section] = config
            return True
        except Exception as e:
            print(f"设置配置段失败: {str(e)}")
            return False
    
    def reset_to_default(self, section: Optional[str] = None) -> bool:
        """重置为默认配置
        
        Args:
            section: 要重置的配置段，None表示重置全部
        
        Returns:
            是否重置成功
        """
        try:
            default_config = self._load_default_config()
            
            if section:
                if section in default_config:
                    self.config_data[section] = default_config[section]
                else:
                    return False
            else:
                self.config_data = default_config
            
            return True
            
        except Exception as e:
            print(f"重置配置失败: {str(e)}")
            return False
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        try:
            # 检查必要的配置项
            required_sections = ['app', 'video', 'subtitle', 'ui', 'performance']
            
            for section in required_sections:
                if section not in self.config_data:
                    print(f"缺少必要的配置段: {section}")
                    return False
            
            # 检查数值范围
            if not (800 <= self.get('app.window_width', 1200) <= 3840):
                print("窗口宽度超出有效范围")
                return False
            
            if not (600 <= self.get('app.window_height', 800) <= 2160):
                print("窗口高度超出有效范围")
                return False
            
            if not (12 <= self.get('subtitle.font_size', 24) <= 72):
                print("字体大小超出有效范围")
                return False
            
            if not (0.0 <= self.get('subtitle.background_opacity', 0.7) <= 1.0):
                print("背景透明度超出有效范围")
                return False
            
            return True
            
        except Exception as e:
            print(f"配置验证失败: {str(e)}")
            return False
    
    def get_recent_files(self) -> list:
        """获取最近打开的文件列表"""
        return self.get('ui.recent_files', [])
    
    def add_recent_file(self, file_path: str):
        """添加最近打开的文件"""
        recent_files = self.get_recent_files()
        
        # 移除已存在的项目
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # 添加到开头
        recent_files.insert(0, file_path)
        
        # 限制数量
        max_count = self.get('ui.recent_files_count', 10)
        recent_files = recent_files[:max_count]
        
        self.set('ui.recent_files', recent_files)
    
    def clear_recent_files(self):
        """清空最近打开的文件列表"""
        self.set('ui.recent_files', [])
    
    def export_config(self, export_path: str) -> bool:
        """导出配置到指定文件"""
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            print(f"配置导出成功: {export_file}")
            return True
            
        except Exception as e:
            print(f"配置导出失败: {str(e)}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """从指定文件导入配置"""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                raise FileNotFoundError(f"配置文件不存在: {import_path}")
            
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 验证导入的配置
            temp_config = self.config_data.copy()
            self.config_data = imported_config
            
            if self.validate_config():
                print(f"配置导入成功: {import_file}")
                return True
            else:
                # 恢复原配置
                self.config_data = temp_config
                print("导入的配置无效，已恢复原配置")
                return False
                
        except Exception as e:
            print(f"配置导入失败: {str(e)}")
            return False
    
    def __str__(self) -> str:
        """字符串表示"""
        return json.dumps(self.config_data, indent=2, ensure_ascii=False)