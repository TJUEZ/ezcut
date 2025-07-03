#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频处理器模块

功能：
- 视频文件加载和预览
- 视频剪切和合并
- 视频格式转换
- 视频质量调整

参考AutoCut项目的视频处理方法
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from tqdm import tqdm

# MoviePy导入 - 可选依赖
try:
    import sys
    import subprocess
    
    # 检查MoviePy是否在系统Python中可用
    result = subprocess.run([sys.executable, '-c', 'import moviepy.editor'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        MOVIEPY_AVAILABLE = True
        print("MoviePy已成功加载")
    else:
        MOVIEPY_AVAILABLE = False
        print("警告: MoviePy未安装，部分视频处理功能将不可用")
except Exception as e:
    MOVIEPY_AVAILABLE = False
    print(f"警告: MoviePy加载失败 - {str(e)}，部分视频处理功能将不可用")

# FFmpeg导入 - 可选依赖
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

class VideoSegment:
    """视频片段类"""
    
    def __init__(self, start_time: float, end_time: float, video_path: str = None):
        self.start_time = start_time
        self.end_time = end_time
        self.video_path = video_path
        self.selected = True  # 是否被选中用于输出
        
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    def __repr__(self):
        return f"VideoSegment({self.start_time:.2f}s - {self.end_time:.2f}s)"

class VideoProcessor:
    """视频处理器类"""
    
    def __init__(self):
        self.current_video = None
        self.video_path = None
        self.segments = []
        self.fps = 30
        self.resolution = (1920, 1080)
        
    def load_video(self, video_path: str) -> bool:
        """加载视频文件"""
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            self.video_path = video_path
            
            if MOVIEPY_AVAILABLE:
                # 使用MoviePy加载
                self.current_video = VideoFileClip(video_path)
                self.fps = self.current_video.fps
                self.resolution = (self.current_video.w, self.current_video.h)
                duration = self.current_video.duration
            else:
                # 使用OpenCV加载
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    raise ValueError("无法打开视频文件")
                
                self.fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                self.resolution = (width, height)
                duration = frame_count / self.fps if self.fps > 0 else 0
                
                cap.release()
                self.current_video = video_path  # 存储路径而不是对象
            
            print(f"视频加载成功: {video_path}")
            print(f"时长: {duration:.2f}秒")
            print(f"分辨率: {self.resolution}")
            print(f"帧率: {self.fps}")
            
            return True
            
        except Exception as e:
            print(f"视频加载失败: {str(e)}")
            return False
    
    def get_video_info(self) -> dict:
        """获取当前视频信息"""
        if not self.current_video:
            return {}
        
        if MOVIEPY_AVAILABLE and hasattr(self.current_video, 'duration'):
            duration = self.current_video.duration
        else:
            # 使用OpenCV计算时长
            cap = cv2.VideoCapture(self.video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
        
        return {
            'path': self.video_path,
            'duration': duration,
            'fps': self.fps,
            'resolution': self.resolution,
            'size': os.path.getsize(self.video_path) if self.video_path else 0
        }
    
    def extract_frame(self, timestamp: float) -> Optional[np.ndarray]:
        """提取指定时间戳的帧"""
        if not self.current_video:
            return None
        
        try:
            if MOVIEPY_AVAILABLE and hasattr(self.current_video, 'get_frame'):
                # 使用MoviePy提取帧
                frame = self.current_video.get_frame(timestamp)
                return frame
            else:
                # 使用OpenCV提取帧
                cap = cv2.VideoCapture(self.video_path)
                if not cap.isOpened():
                    return None
                
                # 设置到指定时间戳
                cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # OpenCV使用BGR，转换为RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    return frame
                return None
                
        except Exception as e:
            print(f"提取帧失败: {str(e)}")
            return None
    
    def add_segment(self, start_time: float, end_time: float) -> VideoSegment:
        """添加视频片段"""
        if start_time >= end_time:
            raise ValueError("开始时间必须小于结束时间")
        
        if not self.current_video:
            raise ValueError("请先加载视频文件")
        
        if end_time > self.current_video.duration:
            end_time = self.current_video.duration
        
        segment = VideoSegment(start_time, end_time, self.video_path)
        self.segments.append(segment)
        return segment
    
    def remove_segment(self, segment: VideoSegment):
        """移除视频片段"""
        if segment in self.segments:
            self.segments.remove(segment)
    
    def clear_segments(self):
        """清空所有片段"""
        self.segments.clear()
    
    def reorder_segments(self, new_order: List[int]):
        """重新排序视频片段"""
        if len(new_order) != len(self.segments):
            raise ValueError("新顺序长度与片段数量不匹配")
        
        self.segments = [self.segments[i] for i in new_order]
    
    def cut_video(self, output_path: str, bitrate: str = "10M", 
                  progress_callback=None) -> bool:
        """剪切视频 - 参考AutoCut的实现方式"""
        if not self.segments:
            raise ValueError("没有可剪切的片段")
        
        if not self.current_video:
            raise ValueError("请先加载视频文件")
        
        try:
            # 获取选中的片段
            selected_segments = [seg for seg in self.segments if seg.selected]
            
            if not selected_segments:
                raise ValueError("没有选中的片段")
            
            if MOVIEPY_AVAILABLE and hasattr(self.current_video, 'subclip'):
                # 使用MoviePy进行视频剪切
                clips = []
                total_segments = len(selected_segments)
                
                for i, segment in enumerate(selected_segments):
                    if progress_callback:
                        progress_callback(f"处理片段 {i+1}/{total_segments}", 
                                        (i / total_segments) * 100)
                    
                    # 剪切片段
                    clip = self.current_video.subclip(segment.start_time, segment.end_time)
                    clips.append(clip)
                
                # 合并所有片段
                if progress_callback:
                    progress_callback("合并视频片段...", 90)
                
                final_clip = concatenate_videoclips(clips)
                
                # 输出视频
                if progress_callback:
                    progress_callback("导出视频...", 95)
                
                final_clip.write_videofile(
                    output_path,
                    bitrate=bitrate,
                    audio_codec='aac',
                    verbose=False,
                    logger=None
                )
                
                # 清理资源
                final_clip.close()
                for clip in clips:
                    clip.close()
            else:
                # 使用OpenCV进行基础视频处理（仅支持单个片段）
                if len(selected_segments) > 1:
                    print("警告: 当前模式仅支持单个片段剪切，将处理第一个片段")
                
                segment = selected_segments[0]
                
                if progress_callback:
                    progress_callback("使用OpenCV处理视频...", 50)
                
                cap = cv2.VideoCapture(self.video_path)
                if not cap.isOpened():
                    raise ValueError("无法打开视频文件")
                
                # 设置输出视频编码器
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, self.fps, self.resolution)
                
                # 跳转到开始时间
                start_frame = int(segment.start_time * self.fps)
                end_frame = int(segment.end_time * self.fps)
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                
                frame_count = 0
                total_frames = end_frame - start_frame
                
                while cap.isOpened() and frame_count < total_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    out.write(frame)
                    frame_count += 1
                    
                    if progress_callback and frame_count % 30 == 0:
                        progress = 50 + (frame_count / total_frames) * 45
                        progress_callback(f"处理帧 {frame_count}/{total_frames}", progress)
                
                cap.release()
                out.release()
            
            if progress_callback:
                progress_callback("完成", 100)
            
            print(f"视频剪切完成: {output_path}")
            return True
            
        except Exception as e:
            print(f"视频剪切失败: {str(e)}")
            return False
    
    def get_segments_info(self) -> List[dict]:
        """获取所有片段信息"""
        return [
            {
                'index': i,
                'start_time': seg.start_time,
                'end_time': seg.end_time,
                'duration': seg.duration,
                'selected': seg.selected
            }
            for i, seg in enumerate(self.segments)
        ]
    
    def toggle_segment_selection(self, index: int):
        """切换片段选中状态"""
        if 0 <= index < len(self.segments):
            self.segments[index].selected = not self.segments[index].selected
    
    def close(self):
        """关闭视频处理器，释放资源"""
        if self.current_video:
            self.current_video.close()
            self.current_video = None
        
        self.segments.clear()
        self.video_path = None
    
    def __del__(self):
        """析构函数"""
        self.close()