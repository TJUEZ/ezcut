#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EzCut 项目管理器

功能:
- 保存和加载编辑项目
- 管理项目设置
- 导入导出项目配置
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class ProjectManager:
    """项目管理器"""
    
    def __init__(self):
        self.current_project = None
        self.project_file = None
        self.default_settings = {
            'name': '新项目',
            'description': '',
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'settings': {
                'video': {
                    'width': 1920,
                    'height': 1080,
                    'fps': 30.0,
                    'format': 'mp4'
                },
                'audio': {
                    'sample_rate': 44100,
                    'channels': 2,
                    'format': 'aac'
                },
                'timeline': {
                    'duration': 300.0,  # 5分钟
                    'tracks': 5,
                    'pixels_per_second': 50
                }
            },
            'media_items': [],
            'timeline_clips': [],
            'effects': [],
            'transitions': []
        }
    
    def new_project(self, name: str = "新项目", description: str = "") -> Dict[str, Any]:
        """创建新项目"""
        self.current_project = self.default_settings.copy()
        self.current_project['name'] = name
        self.current_project['description'] = description
        self.current_project['created_at'] = datetime.now().isoformat()
        self.current_project['modified_at'] = datetime.now().isoformat()
        self.project_file = None
        return self.current_project
    
    def save_project(self, file_path: Optional[str] = None) -> bool:
        """保存项目"""
        if not self.current_project:
            return False
        
        if file_path:
            self.project_file = Path(file_path)
        elif not self.project_file:
            return False
        
        try:
            # 更新修改时间
            self.current_project['modified_at'] = datetime.now().isoformat()
            
            # 确保目录存在
            self.project_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存项目文件
            with open(self.project_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_project, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"保存项目失败: {e}")
            return False
    
    def load_project(self, file_path: str) -> bool:
        """加载项目"""
        try:
            project_file = Path(file_path)
            if not project_file.exists():
                print(f"项目文件不存在: {file_path}")
                return False
            
            with open(project_file, 'r', encoding='utf-8') as f:
                self.current_project = json.load(f)
            
            self.project_file = project_file
            
            # 验证项目格式
            if not self._validate_project():
                print("项目文件格式无效")
                return False
            
            return True
            
        except Exception as e:
            print(f"加载项目失败: {e}")
            return False
    
    def _validate_project(self) -> bool:
        """验证项目格式"""
        if not self.current_project:
            return False
        
        required_keys = ['name', 'settings', 'media_items', 'timeline_clips']
        for key in required_keys:
            if key not in self.current_project:
                return False
        
        return True
    
    def add_media_item(self, media_data: Dict[str, Any]):
        """添加媒体项目"""
        if not self.current_project:
            return
        
        self.current_project['media_items'].append(media_data)
        self.current_project['modified_at'] = datetime.now().isoformat()
    
    def add_timeline_clip(self, clip_data: Dict[str, Any]):
        """添加时间轴剪辑"""
        if not self.current_project:
            return
        
        self.current_project['timeline_clips'].append(clip_data)
        self.current_project['modified_at'] = datetime.now().isoformat()
    
    def remove_timeline_clip(self, clip_id: str):
        """移除时间轴剪辑"""
        if not self.current_project:
            return
        
        self.current_project['timeline_clips'] = [
            clip for clip in self.current_project['timeline_clips']
            if clip.get('id') != clip_id
        ]
        self.current_project['modified_at'] = datetime.now().isoformat()
    
    def update_project_settings(self, settings: Dict[str, Any]):
        """更新项目设置"""
        if not self.current_project:
            return
        
        self.current_project['settings'].update(settings)
        self.current_project['modified_at'] = datetime.now().isoformat()
    
    def get_project_info(self) -> Optional[Dict[str, Any]]:
        """获取项目信息"""
        if not self.current_project:
            return None
        
        return {
            'name': self.current_project.get('name', ''),
            'description': self.current_project.get('description', ''),
            'created_at': self.current_project.get('created_at', ''),
            'modified_at': self.current_project.get('modified_at', ''),
            'version': self.current_project.get('version', ''),
            'file_path': str(self.project_file) if self.project_file else None,
            'media_count': len(self.current_project.get('media_items', [])),
            'clip_count': len(self.current_project.get('timeline_clips', []))
        }
    
    def export_project_data(self) -> Optional[Dict[str, Any]]:
        """导出项目数据"""
        return self.current_project.copy() if self.current_project else None
    
    def import_project_data(self, project_data: Dict[str, Any]) -> bool:
        """导入项目数据"""
        try:
            # 验证数据格式
            temp_project = self.current_project
            self.current_project = project_data
            
            if not self._validate_project():
                self.current_project = temp_project
                return False
            
            self.project_file = None
            return True
            
        except Exception as e:
            print(f"导入项目数据失败: {e}")
            return False
    
    def get_recent_projects(self, max_count: int = 10) -> List[Dict[str, str]]:
        """获取最近项目列表"""
        # 这里可以实现最近项目的持久化存储
        # 暂时返回空列表
        return []
    
    def is_project_modified(self) -> bool:
        """检查项目是否已修改"""
        if not self.current_project or not self.project_file:
            return True
        
        try:
            # 比较文件修改时间
            file_mtime = self.project_file.stat().st_mtime
            project_mtime = datetime.fromisoformat(
                self.current_project['modified_at']
            ).timestamp()
            
            return project_mtime > file_mtime
            
        except Exception:
            return True

# 项目文件格式示例
PROJECT_TEMPLATE = {
    "name": "示例项目",
    "description": "这是一个示例视频编辑项目",
    "created_at": "2024-01-01T12:00:00",
    "modified_at": "2024-01-01T12:00:00",
    "version": "1.0.0",
    "settings": {
        "video": {
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "format": "mp4"
        },
        "audio": {
            "sample_rate": 44100,
            "channels": 2,
            "format": "aac"
        },
        "timeline": {
            "duration": 300.0,
            "tracks": 5,
            "pixels_per_second": 50
        }
    },
    "media_items": [
        {
            "id": "media_001",
            "name": "video1.mp4",
            "file_path": "/path/to/video1.mp4",
            "media_type": "video",
            "duration": 120.5,
            "fps": 30.0,
            "width": 1920,
            "height": 1080,
            "file_size": 52428800,
            "imported_at": "2024-01-01T12:05:00"
        }
    ],
    "timeline_clips": [
        {
            "id": "clip_001",
            "media_id": "media_001",
            "track": 0,
            "start_time": 0.0,
            "duration": 60.0,
            "in_point": 0.0,
            "out_point": 60.0,
            "effects": [],
            "properties": {
                "volume": 1.0,
                "brightness": 0.0,
                "contrast": 0.0,
                "saturation": 0.0
            }
        }
    ],
    "effects": [],
    "transitions": []
}

if __name__ == "__main__":
    # 测试项目管理器
    pm = ProjectManager()
    
    # 创建新项目
    project = pm.new_project("测试项目", "这是一个测试项目")
    print("创建项目:", project['name'])
    
    # 添加媒体项目
    pm.add_media_item({
        "id": "test_media",
        "name": "test.mp4",
        "file_path": "test.mp4",
        "media_type": "video"
    })
    
    # 保存项目
    if pm.save_project("test_project.ezcut"):
        print("项目保存成功")
    
    # 获取项目信息
    info = pm.get_project_info()
    print("项目信息:", info)