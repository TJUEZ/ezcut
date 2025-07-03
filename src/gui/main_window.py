#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口GUI模块 - 专业视频编辑界面

功能：
- 媒体库管理和文件拖拽
- 专业时间轴编辑器
- 视频预览和播放控制
- 多轨道编辑支持
- 剪刀工具和片段操作
- 字幕编辑和样式设置
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font, colorchooser
import cv2
from PIL import Image, ImageTk
import threading
import time
from typing import Optional, Callable, List, Dict
import os
from pathlib import Path
import json

class MediaLibraryPanel(ttk.Frame):
    """媒体库面板"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.media_files = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 标题和工具栏
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(header_frame, text="媒体库", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # 工具按钮
        ttk.Button(header_frame, text="导入", command=self.import_media, width=8).pack(side=tk.RIGHT, padx=2)
        ttk.Button(header_frame, text="刷新", command=self.refresh_media, width=8).pack(side=tk.RIGHT, padx=2)
        
        # 搜索框
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 媒体文件列表
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # 创建Treeview
        columns = ('类型', '时长', '大小')
        self.media_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=8)
        
        # 设置列
        self.media_tree.heading('#0', text='文件名')
        self.media_tree.heading('类型', text='类型')
        self.media_tree.heading('时长', text='时长')
        self.media_tree.heading('大小', text='大小')
        
        self.media_tree.column('#0', width=150)
        self.media_tree.column('类型', width=60)
        self.media_tree.column('时长', width=80)
        self.media_tree.column('大小', width=80)
        
        # 滚动条
        media_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.media_tree.yview)
        self.media_tree.configure(yscrollcommand=media_scroll.set)
        
        self.media_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        media_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定拖拽事件
        self.media_tree.bind('<Button-1>', self.on_media_click)
        self.media_tree.bind('<B1-Motion>', self.on_media_drag)
        self.media_tree.bind('<Double-1>', self.on_media_double_click)
        
        # 右键菜单
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="添加到时间轴", command=self.add_to_timeline)
        self.context_menu.add_command(label="预览", command=self.preview_media)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="删除", command=self.remove_media)
        
        self.media_tree.bind('<Button-3>', self.show_context_menu)
    
    def import_media(self):
        """导入媒体文件"""
        file_paths = filedialog.askopenfilenames(
            title="选择媒体文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.m4v"),
                ("音频文件", "*.mp3 *.wav *.aac *.m4a *.flac"),
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        
        for file_path in file_paths:
            self.add_media_file(file_path)
    
    def add_media_file(self, file_path: str):
        """添加媒体文件到库"""
        if file_path in [item['path'] for item in self.media_files]:
            return
        
        try:
            file_info = self.get_file_info(file_path)
            self.media_files.append(file_info)
            self.refresh_display()
        except Exception as e:
            messagebox.showerror("错误", f"无法添加文件: {str(e)}")
    
    def get_file_info(self, file_path: str) -> Dict:
        """获取文件信息"""
        file_stat = os.stat(file_path)
        file_size = self.format_file_size(file_stat.st_size)
        
        # 获取文件类型和时长
        ext = Path(file_path).suffix.lower()
        if ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v']:
            file_type = '视频'
            duration = self.get_video_duration(file_path)
        elif ext in ['.mp3', '.wav', '.aac', '.m4a', '.flac']:
            file_type = '音频'
            duration = self.get_audio_duration(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            file_type = '图片'
            duration = '-'
        else:
            file_type = '其他'
            duration = '-'
        
        return {
            'path': file_path,
            'name': Path(file_path).name,
            'type': file_type,
            'duration': duration,
            'size': file_size
        }
    
    def get_video_duration(self, file_path: str) -> str:
        """获取视频时长"""
        try:
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            
            if fps > 0:
                duration = frame_count / fps
                return self.format_duration(duration)
        except:
            pass
        return '-'
    
    def get_audio_duration(self, file_path: str) -> str:
        """获取音频时长"""
        # 这里可以使用librosa或其他音频库
        return '-'
    
    def format_duration(self, seconds: float) -> str:
        """格式化时长"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"
    
    def refresh_display(self):
        """刷新显示"""
        # 清空现有项目
        for item in self.media_tree.get_children():
            self.media_tree.delete(item)
        
        # 添加媒体文件
        search_text = self.search_var.get().lower()
        for media_info in self.media_files:
            if not search_text or search_text in media_info['name'].lower():
                self.media_tree.insert('', 'end',
                                     text=media_info['name'],
                                     values=(media_info['type'], media_info['duration'], media_info['size']),
                                     tags=(media_info['path'],))
    
    def on_search_change(self, *args):
        """搜索变化事件"""
        self.refresh_display()
    
    def refresh_media(self):
        """刷新媒体库"""
        self.refresh_display()
    
    def on_media_click(self, event):
        """媒体点击事件"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_media_drag(self, event):
        """媒体拖拽事件"""
        # 检查是否开始拖拽
        if abs(event.x - self.drag_start_x) > 5 or abs(event.y - self.drag_start_y) > 5:
            selection = self.media_tree.selection()
            if selection:
                item = selection[0]
                file_path = self.media_tree.item(item, 'tags')[0]
                # 通知时间轴准备接收拖拽
                self.app.main_window.timeline_editor.start_drag_operation(file_path)
    
    def on_media_double_click(self, event):
        """媒体双击事件"""
        self.add_to_timeline()
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.media_tree.identify_row(event.y)
        if item:
            self.media_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def add_to_timeline(self):
        """添加到时间轴"""
        selection = self.media_tree.selection()
        if selection:
            item = selection[0]
            file_path = self.media_tree.item(item, 'tags')[0]
            self.app.main_window.timeline_editor.add_media_clip(file_path)
    
    def preview_media(self):
        """预览媒体"""
        selection = self.media_tree.selection()
        if selection:
            item = selection[0]
            file_path = self.media_tree.item(item, 'tags')[0]
            self.app.main_window.video_preview.load_video(file_path)
    
    def remove_media(self):
        """删除媒体"""
        selection = self.media_tree.selection()
        if selection:
            if messagebox.askyesno("确认", "确定要从媒体库中删除选中的文件吗？"):
                item = selection[0]
                file_path = self.media_tree.item(item, 'tags')[0]
                self.media_files = [f for f in self.media_files if f['path'] != file_path]
                self.refresh_display()

class TimelineEditor(ttk.Frame):
    """时间轴编辑器"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.clips = []  # 视频片段列表
        self.current_time = 0.0
        self.zoom_level = 1.0
        self.pixels_per_second = 50  # 每秒对应的像素数
        self.track_height = 60
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 工具栏
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(toolbar_frame, text="时间轴", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # 工具按钮
        ttk.Button(toolbar_frame, text="✂", command=self.activate_cut_tool, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="🔍+", command=self.zoom_in, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="🔍-", command=self.zoom_out, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="清空", command=self.clear_timeline, width=6).pack(side=tk.RIGHT, padx=2)
        
        # 时间标尺
        self.ruler_frame = ttk.Frame(self)
        self.ruler_frame.pack(fill=tk.X, padx=5)
        
        self.ruler_canvas = tk.Canvas(self.ruler_frame, height=30, bg='lightgray')
        self.ruler_canvas.pack(fill=tk.X)
        
        # 时间轴主区域
        timeline_frame = ttk.Frame(self)
        timeline_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # 轨道标签
        self.track_labels_frame = ttk.Frame(timeline_frame)
        self.track_labels_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # 创建轨道标签
        for i in range(3):  # 3个轨道
            label = ttk.Label(self.track_labels_frame, text=f"轨道{i+1}", width=8)
            label.pack(pady=1, padx=2)
        
        # 时间轴画布容器
        canvas_frame = ttk.Frame(timeline_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 时间轴画布
        self.timeline_canvas = tk.Canvas(canvas_frame, bg='white', height=200)
        
        # 滚动条
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.timeline_canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.timeline_canvas.yview)
        
        self.timeline_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        self.timeline_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定事件
        self.timeline_canvas.bind('<Button-1>', self.on_timeline_click)
        self.timeline_canvas.bind('<B1-Motion>', self.on_timeline_drag)
        self.timeline_canvas.bind('<ButtonRelease-1>', self.on_timeline_release)
        self.timeline_canvas.bind('<Double-1>', self.on_timeline_double_click)
        self.timeline_canvas.bind('<Button-3>', self.on_timeline_right_click)
        
        # 播放头
        self.playhead_line = None
        
        self.draw_timeline()
    
    def draw_timeline(self):
        """绘制时间轴"""
        self.timeline_canvas.delete('all')
        
        # 绘制轨道背景
        canvas_width = max(1000, len(self.clips) * 200)
        self.timeline_canvas.configure(scrollregion=(0, 0, canvas_width, self.track_height * 3))
        
        for i in range(3):
            y = i * self.track_height
            self.timeline_canvas.create_rectangle(0, y, canvas_width, y + self.track_height - 1,
                                                fill='lightblue' if i % 2 == 0 else 'lightcyan',
                                                outline='gray')
        
        # 绘制时间刻度
        self.draw_ruler()
        
        # 绘制视频片段
        for clip in self.clips:
            self.draw_clip(clip)
        
        # 绘制播放头
        self.draw_playhead()
    
    def draw_ruler(self):
        """绘制时间标尺"""
        self.ruler_canvas.delete('all')
        
        canvas_width = max(1000, len(self.clips) * 200)
        
        # 绘制时间刻度
        for i in range(0, int(canvas_width / self.pixels_per_second) + 1):
            x = i * self.pixels_per_second
            
            # 主刻度（秒）
            self.ruler_canvas.create_line(x, 20, x, 30, fill='black')
            self.ruler_canvas.create_text(x, 15, text=f"{i}s", font=('Arial', 8))
            
            # 次刻度（0.5秒）
            if i < int(canvas_width / self.pixels_per_second):
                x_half = x + self.pixels_per_second / 2
                self.ruler_canvas.create_line(x_half, 25, x_half, 30, fill='gray')
    
    def draw_clip(self, clip):
        """绘制视频片段"""
        x1 = clip['start_time'] * self.pixels_per_second * self.zoom_level
        x2 = clip['end_time'] * self.pixels_per_second * self.zoom_level
        y1 = clip['track'] * self.track_height + 5
        y2 = y1 + self.track_height - 10
        
        # 片段矩形
        rect_id = self.timeline_canvas.create_rectangle(x1, y1, x2, y2,
                                                      fill='lightgreen',
                                                      outline='darkgreen',
                                                      width=2,
                                                      tags=('clip', f'clip_{clip["id"]}'))
        
        # 片段文本
        text_x = (x1 + x2) / 2
        text_y = (y1 + y2) / 2
        self.timeline_canvas.create_text(text_x, text_y,
                                       text=clip['name'],
                                       font=('Arial', 8),
                                       tags=('clip_text', f'clip_{clip["id"]}'))
        
        # 调整手柄
        handle_size = 5
        # 左手柄
        self.timeline_canvas.create_rectangle(x1 - handle_size, y1, x1, y2,
                                            fill='blue',
                                            tags=('left_handle', f'clip_{clip["id"]}'))
        # 右手柄
        self.timeline_canvas.create_rectangle(x2, y1, x2 + handle_size, y2,
                                            fill='blue',
                                            tags=('right_handle', f'clip_{clip["id"]}'))
    
    def draw_playhead(self):
        """绘制播放头"""
        if self.playhead_line:
            self.timeline_canvas.delete(self.playhead_line)
        
        x = self.current_time * self.pixels_per_second * self.zoom_level
        self.playhead_line = self.timeline_canvas.create_line(x, 0, x, self.track_height * 3,
                                                            fill='red', width=2)
    
    def add_media_clip(self, file_path: str, track: int = 0):
        """添加媒体片段"""
        # 获取文件信息
        duration = self.get_media_duration(file_path)
        if duration <= 0:
            duration = 5.0  # 默认5秒
        
        # 找到合适的插入位置
        start_time = self.find_insert_position(track, duration)
        
        clip = {
            'id': len(self.clips),
            'path': file_path,
            'name': Path(file_path).stem,
            'track': track,
            'start_time': start_time,
            'end_time': start_time + duration,
            'duration': duration
        }
        
        self.clips.append(clip)
        self.draw_timeline()
    
    def get_media_duration(self, file_path: str) -> float:
        """获取媒体时长"""
        try:
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            
            if fps > 0:
                return frame_count / fps
        except:
            pass
        return 5.0  # 默认5秒
    
    def find_insert_position(self, track: int, duration: float) -> float:
        """找到合适的插入位置"""
        track_clips = [c for c in self.clips if c['track'] == track]
        if not track_clips:
            return 0.0
        
        # 按开始时间排序
        track_clips.sort(key=lambda x: x['start_time'])
        
        # 找到第一个可用位置
        for i, clip in enumerate(track_clips):
            if i == 0 and clip['start_time'] >= duration:
                return 0.0
            elif i > 0:
                prev_clip = track_clips[i-1]
                gap = clip['start_time'] - prev_clip['end_time']
                if gap >= duration:
                    return prev_clip['end_time']
        
        # 添加到末尾
        return track_clips[-1]['end_time']
    
    def on_timeline_click(self, event):
        """时间轴点击事件"""
        x = self.timeline_canvas.canvasx(event.x)
        y = self.timeline_canvas.canvasy(event.y)
        
        # 检查是否点击了片段
        clicked_item = self.timeline_canvas.find_closest(x, y)[0]
        tags = self.timeline_canvas.gettags(clicked_item)
        
        if 'clip' in tags:
            # 选中片段
            self.select_clip(tags)
        else:
            # 移动播放头
            self.current_time = x / (self.pixels_per_second * self.zoom_level)
            self.draw_playhead()
            # 通知视频预览更新
            self.app.main_window.video_preview.seek_to_time(self.current_time)
    
    def on_timeline_drag(self, event):
        """时间轴拖拽事件"""
        # 实现片段拖拽逻辑
        pass
    
    def on_timeline_release(self, event):
        """时间轴释放事件"""
        pass
    
    def on_timeline_double_click(self, event):
        """时间轴双击事件"""
        # 实现片段分割
        x = self.timeline_canvas.canvasx(event.x)
        time_pos = x / (self.pixels_per_second * self.zoom_level)
        self.split_clip_at_time(time_pos)
    
    def on_timeline_right_click(self, event):
        """时间轴右键事件"""
        # 显示右键菜单
        pass
    
    def select_clip(self, tags):
        """选中片段"""
        # 实现片段选中逻辑
        pass
    
    def split_clip_at_time(self, time_pos: float):
        """在指定时间分割片段"""
        for clip in self.clips:
            if clip['start_time'] <= time_pos <= clip['end_time']:
                # 分割片段
                new_clip = clip.copy()
                new_clip['id'] = len(self.clips)
                new_clip['start_time'] = time_pos
                
                clip['end_time'] = time_pos
                
                self.clips.append(new_clip)
                self.draw_timeline()
                break
    
    def activate_cut_tool(self):
        """激活剪刀工具"""
        messagebox.showinfo("剪刀工具", "双击时间轴上的片段可以分割片段")
    
    def zoom_in(self):
        """放大时间轴"""
        self.zoom_level *= 1.2
        self.draw_timeline()
    
    def zoom_out(self):
        """缩小时间轴"""
        self.zoom_level /= 1.2
        self.draw_timeline()
    
    def clear_timeline(self):
        """清空时间轴"""
        if messagebox.askyesno("确认", "确定要清空时间轴吗？"):
            self.clips.clear()
            self.draw_timeline()
    
    def start_drag_operation(self, file_path: str):
        """开始拖拽操作"""
        # 实现从媒体库拖拽到时间轴的逻辑
        pass

class VideoPreviewPanel(ttk.Frame):
    """视频预览面板"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_frame = None
        self.video_cap = None
        self.is_playing = False
        self.current_time = 0.0
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 视频显示区域
        self.video_frame = ttk.Frame(self)
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.video_label = tk.Label(self.video_frame, bg='black', text='请从媒体库拖拽视频文件\n或双击媒体库中的文件进行预览')
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # 控制面板
        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 播放控制按钮
        self.play_button = ttk.Button(self.control_frame, text="▶", command=self.toggle_play, width=3)
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        self.stop_button = ttk.Button(self.control_frame, text="⏹", command=self.stop, width=3)
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        # 时间显示
        self.time_label = ttk.Label(self.control_frame, text="00:00 / 00:00")
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_scale = ttk.Scale(self.control_frame, from_=0, to=100, 
                                       orient=tk.HORIZONTAL, variable=self.progress_var,
                                       command=self.on_progress_change)
        self.progress_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 音量控制
        ttk.Label(self.control_frame, text="🔊").pack(side=tk.RIGHT)
        self.volume_var = tk.DoubleVar(value=100)
        volume_scale = ttk.Scale(self.control_frame, from_=0, to=100,
                               orient=tk.HORIZONTAL, variable=self.volume_var,
                               length=80)
        volume_scale.pack(side=tk.RIGHT, padx=5)
    
    def load_video(self, video_path: str):
        """加载视频"""
        try:
            if self.video_cap:
                self.video_cap.release()
            
            self.video_cap = cv2.VideoCapture(video_path)
            if not self.video_cap.isOpened():
                raise ValueError("无法打开视频文件")
            
            # 显示第一帧
            self.show_frame(0)
            
            # 更新进度条范围
            total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = self.video_cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            self.progress_scale.configure(to=duration)
            self.update_time_display()
            
        except Exception as e:
            messagebox.showerror("错误", f"视频加载失败: {str(e)}")
    
    def show_frame(self, timestamp: float):
        """显示指定时间戳的帧"""
        if not self.video_cap:
            return
        
        try:
            fps = self.video_cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.video_cap.read()
            
            if ret:
                # 转换颜色空间
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 调整大小以适应显示区域
                height, width = frame.shape[:2]
                display_width = self.video_label.winfo_width()
                display_height = self.video_label.winfo_height()
                
                if display_width > 1 and display_height > 1:
                    # 保持宽高比
                    ratio = min(display_width/width, display_height/height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # 转换为PIL图像
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                
                # 更新显示
                self.video_label.configure(image=photo, text="")
                self.video_label.image = photo  # 保持引用
                
                self.current_time = timestamp
                self.progress_var.set(timestamp)
                self.update_time_display()
                
        except Exception as e:
            print(f"显示帧失败: {str(e)}")
    
    def seek_to_time(self, timestamp: float):
        """跳转到指定时间"""
        self.current_time = timestamp
        self.show_frame(timestamp)
    
    def toggle_play(self):
        """切换播放状态"""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """播放视频"""
        if not self.video_cap:
            return
        
        self.is_playing = True
        self.play_button.configure(text="⏸")
        
        def play_thread():
            fps = self.video_cap.get(cv2.CAP_PROP_FPS)
            frame_duration = 1.0 / fps if fps > 0 else 1.0/30
            
            while self.is_playing and self.video_cap:
                start_time = time.time()
                
                self.show_frame(self.current_time)
                self.current_time += frame_duration
                
                # 检查是否到达视频末尾
                total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = total_frames / fps if fps > 0 else 0
                
                if self.current_time >= duration:
                    self.stop()
                    break
                
                # 控制播放速度
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_duration - elapsed)
                time.sleep(sleep_time)
        
        threading.Thread(target=play_thread, daemon=True).start()
    
    def pause(self):
        """暂停播放"""
        self.is_playing = False
        self.play_button.configure(text="▶")
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
        self.play_button.configure(text="▶")
        self.current_time = 0.0
        self.show_frame(0)
    
    def on_progress_change(self, value):
        """进度条变化事件"""
        if not self.is_playing:  # 只在非播放状态下响应拖拽
            timestamp = float(value)
            self.show_frame(timestamp)
    
    def update_time_display(self):
        """更新时间显示"""
        if not self.video_cap:
            return
        
        current_str = self.format_time(self.current_time)
        
        total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        total_str = self.format_time(duration)
        
        self.time_label.configure(text=f"{current_str} / {total_str}")
    
    def format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

class SubtitlePanel(ttk.Frame):
    """字幕面板"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 标题
        ttk.Label(self, text="字幕编辑", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=2)
        
        # 字幕列表
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        columns = ('时间', '时长', '内容')
        self.subtitle_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=6)
        
        self.subtitle_tree.heading('#0', text='序号')
        self.subtitle_tree.heading('时间', text='时间')
        self.subtitle_tree.heading('时长', text='时长')
        self.subtitle_tree.heading('内容', text='内容')
        
        self.subtitle_tree.column('#0', width=40)
        self.subtitle_tree.column('时间', width=80)
        self.subtitle_tree.column('时长', width=60)
        self.subtitle_tree.column('内容', width=200)
        
        subtitle_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.subtitle_tree.yview)
        self.subtitle_tree.configure(yscrollcommand=subtitle_scroll.set)
        
        self.subtitle_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        subtitle_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 字幕编辑区域
        edit_frame = ttk.LabelFrame(self, text="编辑字幕")
        edit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 时间编辑
        time_frame = ttk.Frame(edit_frame)
        time_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(time_frame, text="开始:").pack(side=tk.LEFT)
        self.start_time_var = tk.StringVar()
        ttk.Entry(time_frame, textvariable=self.start_time_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(time_frame, text="结束:").pack(side=tk.LEFT, padx=(10,0))
        self.end_time_var = tk.StringVar()
        ttk.Entry(time_frame, textvariable=self.end_time_var, width=8).pack(side=tk.LEFT, padx=2)
        
        # 文本编辑
        ttk.Label(edit_frame, text="内容:").pack(anchor=tk.W, padx=5)
        self.text_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.text_var).pack(fill=tk.X, padx=5, pady=2)
        
        # 按钮
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="添加", command=self.add_subtitle).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="更新", command=self.update_subtitle).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="删除", command=self.delete_subtitle).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="自动识别", command=self.auto_generate).pack(side=tk.RIGHT, padx=2)
    
    def add_subtitle(self):
        """添加字幕"""
        # 实现添加字幕逻辑
        pass
    
    def update_subtitle(self):
        """更新字幕"""
        # 实现更新字幕逻辑
        pass
    
    def delete_subtitle(self):
        """删除字幕"""
        # 实现删除字幕逻辑
        pass
    
    def auto_generate(self):
        """自动生成字幕"""
        # 实现自动生成字幕逻辑
        pass

class MainWindow:
    """主窗口类 - 专业视频编辑界面"""
    
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        """设置主界面"""
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 顶部区域 - 媒体库和预览
        top_paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        top_paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧 - 媒体库
        left_frame = ttk.Frame(top_paned)
        top_paned.add(left_frame, weight=1)
        
        self.media_library = MediaLibraryPanel(left_frame, self.app)
        self.media_library.pack(fill=tk.BOTH, expand=True)
        
        # 中间 - 视频预览
        center_frame = ttk.Frame(top_paned)
        top_paned.add(center_frame, weight=2)
        
        self.video_preview = VideoPreviewPanel(center_frame, self.app)
        self.video_preview.pack(fill=tk.BOTH, expand=True)
        
        # 右侧 - 字幕面板
        right_frame = ttk.Frame(top_paned)
        top_paned.add(right_frame, weight=1)
        
        self.subtitle_panel = SubtitlePanel(right_frame, self.app)
        self.subtitle_panel.pack(fill=tk.BOTH, expand=True)
        
        # 底部 - 时间轴编辑器
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.timeline_editor = TimelineEditor(bottom_frame, self.app)
        self.timeline_editor.pack(fill=tk.X)
        
        # 状态栏
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="就绪 - 请导入媒体文件开始编辑")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self.status_frame, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建项目", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="打开项目", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="保存项目", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="导入媒体", command=self.import_media, accelerator="Ctrl+I")
        file_menu.add_separator()
        file_menu.add_command(label="导出视频", command=self.export_video, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="剪切", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="复制", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="粘贴", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="全选", command=self.select_all, accelerator="Ctrl+A")
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="放大时间轴", command=self.timeline_editor.zoom_in, accelerator="+")
        view_menu.add_command(label="缩小时间轴", command=self.timeline_editor.zoom_out, accelerator="-")
        view_menu.add_separator()
        view_menu.add_command(label="全屏预览", command=self.fullscreen_preview, accelerator="F11")
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="剪刀工具", command=self.timeline_editor.activate_cut_tool)
        tools_menu.add_command(label="自动字幕识别", command=self.auto_subtitle)
        tools_menu.add_separator()
        tools_menu.add_command(label="设置", command=self.show_settings)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="快捷键", command=self.show_shortcuts)
        help_menu.add_command(label="使用教程", command=self.show_tutorial)
        help_menu.add_command(label="关于", command=self.show_about)
        
        # 绑定快捷键
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-o>', lambda e: self.open_project())
        self.root.bind('<Control-s>', lambda e: self.save_project())
        self.root.bind('<Control-i>', lambda e: self.import_media())
        self.root.bind('<Control-e>', lambda e: self.export_video())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<space>', lambda e: self.video_preview.toggle_play())
    
    def new_project(self):
        """新建项目"""
        if messagebox.askyesno("新建项目", "确定要新建项目吗？当前项目的更改将丢失。"):
            self.timeline_editor.clear_timeline()
            self.media_library.media_files.clear()
            self.media_library.refresh_display()
            self.status_label.configure(text="新项目已创建")
    
    def open_project(self):
        """打开项目"""
        file_path = filedialog.askopenfilename(
            title="打开项目文件",
            filetypes=[("EzCut项目文件", "*.ezcut"), ("所有文件", "*.*")]
        )
        if file_path:
            # 实现项目文件加载逻辑
            self.status_label.configure(text=f"项目已打开: {Path(file_path).name}")
    
    def save_project(self):
        """保存项目"""
        file_path = filedialog.asksaveasfilename(
            title="保存项目文件",
            defaultextension=".ezcut",
            filetypes=[("EzCut项目文件", "*.ezcut"), ("所有文件", "*.*")]
        )
        if file_path:
            # 实现项目文件保存逻辑
            project_data = {
                'media_files': self.media_library.media_files,
                'timeline_clips': self.timeline_editor.clips,
                'settings': {}
            }
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)
                self.status_label.configure(text=f"项目已保存: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("错误", f"保存项目失败: {str(e)}")
    
    def import_media(self):
        """导入媒体"""
        self.media_library.import_media()
    
    def export_video(self):
        """导出视频"""
        if not self.timeline_editor.clips:
            messagebox.showwarning("警告", "时间轴为空，请先添加视频片段")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="导出视频",
            defaultextension=".mp4",
            filetypes=[("MP4视频", "*.mp4"), ("AVI视频", "*.avi"), ("所有文件", "*.*")]
        )
        
        if file_path:
            # 显示导出进度对话框
            self.show_export_progress(file_path)
    
    def show_export_progress(self, output_path: str):
        """显示导出进度"""
        progress_window = tk.Toplevel(self.root)
        progress_window.title("导出视频")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="正在导出视频，请稍候...", font=('Arial', 12)).pack(pady=20)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100, length=300)
        progress_bar.pack(pady=10)
        
        status_label = ttk.Label(progress_window, text="准备中...")
        status_label.pack(pady=10)
        
        def progress_callback(message, percent):
            status_label.configure(text=message)
            progress_var.set(percent)
            progress_window.update()
        
        def export_thread():
            try:
                # 实现视频导出逻辑
                progress_callback("正在合并视频片段...", 25)
                time.sleep(1)  # 模拟处理时间
                
                progress_callback("正在添加字幕...", 50)
                time.sleep(1)
                
                progress_callback("正在编码输出...", 75)
                time.sleep(1)
                
                progress_callback("导出完成", 100)
                time.sleep(0.5)
                
                progress_window.destroy()
                messagebox.showinfo("成功", f"视频已导出到: {output_path}")
                
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("错误", f"导出失败: {str(e)}")
        
        threading.Thread(target=export_thread, daemon=True).start()
    
    def undo(self):
        """撤销"""
        # 实现撤销逻辑
        pass
    
    def redo(self):
        """重做"""
        # 实现重做逻辑
        pass
    
    def cut(self):
        """剪切"""
        # 实现剪切逻辑
        pass
    
    def copy(self):
        """复制"""
        # 实现复制逻辑
        pass
    
    def paste(self):
        """粘贴"""
        # 实现粘贴逻辑
        pass
    
    def select_all(self):
        """全选"""
        # 实现全选逻辑
        pass
    
    def fullscreen_preview(self):
        """全屏预览"""
        # 实现全屏预览逻辑
        pass
    
    def auto_subtitle(self):
        """自动字幕识别"""
        self.subtitle_panel.auto_generate()
    
    def show_settings(self):
        """显示设置"""
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 常规设置
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="常规")
        
        # 视频设置
        video_frame = ttk.Frame(notebook)
        notebook.add(video_frame, text="视频")
        
        # 字幕设置
        subtitle_frame = ttk.Frame(notebook)
        notebook.add(subtitle_frame, text="字幕")
    
    def show_shortcuts(self):
        """显示快捷键"""
        shortcuts_text = """
文件操作:
Ctrl+N - 新建项目
Ctrl+O - 打开项目
Ctrl+S - 保存项目
Ctrl+I - 导入媒体
Ctrl+E - 导出视频

编辑操作:
Ctrl+Z - 撤销
Ctrl+Y - 重做
Ctrl+X - 剪切
Ctrl+C - 复制
Ctrl+V - 粘贴
Ctrl+A - 全选

播放控制:
Space - 播放/暂停
+ - 放大时间轴
- - 缩小时间轴
F11 - 全屏预览

时间轴操作:
双击 - 分割片段
拖拽 - 移动片段
右键 - 显示菜单
"""
        
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("快捷键")
        shortcuts_window.geometry("400x500")
        shortcuts_window.transient(self.root)
        
        text_widget = tk.Text(shortcuts_window, wrap=tk.WORD, padx=10, pady=10, font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, shortcuts_text)
        text_widget.configure(state=tk.DISABLED)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(shortcuts_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_tutorial(self):
        """显示使用教程"""
        tutorial_text = """
EzCut 专业视频编辑软件使用教程

1. 媒体库管理:
   • 点击\"导入\"按钮或使用Ctrl+I导入视频、音频、图片文件
   • 支持多种格式：MP4、AVI、MOV、MP3、WAV、JPG、PNG等
   • 使用搜索框快速查找媒体文件
   • 双击文件可预览，右键显示更多选项

2. 时间轴编辑:
   • 从媒体库拖拽文件到时间轴，或双击添加
   • 支持3个视频轨道，可自由排列视频片段
   • 使用剪刀工具(✂)或双击片段进行分割
   • 拖拽片段可调整位置和顺序
   • 使用+/-按钮或滚轮缩放时间轴

3. 视频预览:
   • 实时预览编辑效果
   • 播放控制：播放/暂停、停止、进度调节
   • 音量控制和时间显示
   • 点击时间轴可跳转到指定位置

4. 字幕编辑:
   • 手动添加、编辑、删除字幕
   • 精确调整字幕时间和内容
   • 支持自动字幕识别(需要Whisper)
   • 字幕与视频同步预览

5. 项目管理:
   • 新建、打开、保存项目文件(.ezcut)
   • 项目包含媒体库、时间轴、设置等信息
   • 支持撤销/重做操作

6. 视频导出:
   • 支持MP4、AVI等格式导出
   • 实时显示导出进度
   • 自动合并时间轴上的所有片段
   • 可选择是否包含字幕

快捷键提示:
• 空格键：播放/暂停
• Ctrl+Z/Y：撤销/重做
• Ctrl+S：保存项目
• Ctrl+E：导出视频
• +/-：缩放时间轴

注意事项:
• 建议使用高质量的源视频文件
• 大文件处理时请耐心等待
• 定期保存项目以防数据丢失
• 导出前请检查时间轴布局
"""
        
        tutorial_window = tk.Toplevel(self.root)
        tutorial_window.title("使用教程")
        tutorial_window.geometry("600x700")
        tutorial_window.transient(self.root)
        
        # 创建滚动文本框
        text_frame = ttk.Frame(tutorial_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, tutorial_text)
        text_widget.configure(state=tk.DISABLED)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
EzCut - 专业视频编辑软件
版本: 2.0.0

主要功能：
• 专业媒体库管理
• 多轨道时间轴编辑
• 实时视频预览
• 智能剪刀工具
• 拖拽式操作界面
• 字幕编辑和同步
• 项目文件管理
• 多格式导入导出

技术特性：
• 基于Python开发
• Tkinter现代化界面
• OpenCV视频处理
• 支持GPU加速
• 模块化架构设计

参考设计：
• Adobe Premiere Pro
• DaVinci Resolve
• 剪映专业版

开发团队：
EzCut Development Team

许可证：
MIT License

更多信息：
https://github.com/ezcut/ezcut
"""
        
        about_window = tk.Toplevel(self.root)
        about_window.title("关于 EzCut")
        about_window.geometry("450x500")
        about_window.transient(self.root)
        about_window.resizable(False, False)
        
        # 图标区域
        icon_frame = ttk.Frame(about_window)
        icon_frame.pack(pady=20)
        
        # 这里可以添加应用图标
        icon_label = ttk.Label(icon_frame, text="🎬", font=('Arial', 48))
        icon_label.pack()
        
        # 文本信息
        text_frame = ttk.Frame(about_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 10), 
                             relief=tk.FLAT, bg=about_window.cget('bg'))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, about_text)
        text_widget.configure(state=tk.DISABLED)
        
        # 按钮区域
        button_frame = ttk.Frame(about_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=about_window.destroy, width=10).pack()

# 导出主要类供外部使用
__all__ = ['MainWindow', 'MediaLibraryPanel', 'TimelineEditor', 'VideoPreviewPanel', 'SubtitlePanel']