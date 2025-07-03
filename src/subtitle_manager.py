#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕管理器模块

功能：
- 自动字幕识别和生成 (基于Whisper)
- 字幕文件读取和保存 (SRT格式)
- 字幕样式编辑和自定义字体
- 字幕时间轴调整

参考AutoCut项目的字幕处理方法
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import timedelta

# MoviePy导入 - 可选依赖
try:
    import sys
    import subprocess
    
    # 检查MoviePy是否在系统Python中可用
    result = subprocess.run([sys.executable, '-c', 'import moviepy.editor'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        from moviepy.editor import VideoFileClip
        MOVIEPY_AVAILABLE = True
        print("MoviePy已成功加载（字幕管理器）")
    else:
        MOVIEPY_AVAILABLE = False
        print("警告: MoviePy未安装，视频音频提取功能将不可用")
except Exception as e:
    MOVIEPY_AVAILABLE = False
    print(f"警告: MoviePy加载失败（字幕管理器） - {str(e)}，视频音频提取功能将不可用")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("警告: Whisper未安装，字幕识别功能将不可用")

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

import pysrt

@dataclass
class SubtitleStyle:
    """字幕样式类"""
    font_family: str = "Arial"
    font_size: int = 24
    font_color: str = "#FFFFFF"
    background_color: str = "#000000"
    background_opacity: float = 0.7
    position: str = "bottom"  # top, center, bottom
    alignment: str = "center"  # left, center, right
    bold: bool = False
    italic: bool = False
    outline: bool = True
    outline_color: str = "#000000"
    outline_width: int = 2

@dataclass
class SubtitleItem:
    """字幕条目类"""
    index: int
    start_time: float
    end_time: float
    text: str
    style: Optional[SubtitleStyle] = None
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    def to_srt_time(self, seconds: float) -> str:
        """转换为SRT时间格式"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = td.total_seconds() % 60
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def to_srt_format(self) -> str:
        """转换为SRT格式"""
        start_time_str = self.to_srt_time(self.start_time)
        end_time_str = self.to_srt_time(self.end_time)
        return f"{self.index}\n{start_time_str} --> {end_time_str}\n{self.text}\n"

class SubtitleManager:
    """字幕管理器类"""
    
    def __init__(self):
        self.subtitles: List[SubtitleItem] = []
        self.default_style = SubtitleStyle()
        self.whisper_model = None
        self.faster_whisper_model = None
        self.available_fonts = self._get_available_fonts()
        
    def _get_available_fonts(self) -> List[str]:
        """获取系统可用字体"""
        # 常见字体列表
        common_fonts = [
            "Arial", "Times New Roman", "Helvetica", "Calibri",
            "Microsoft YaHei", "SimHei", "SimSun", "KaiTi",
            "Consolas", "Courier New", "Georgia", "Verdana"
        ]
        
        # 检查fonts目录下的自定义字体
        fonts_dir = Path("fonts")
        custom_fonts = []
        if fonts_dir.exists():
            for font_file in fonts_dir.glob("*.ttf"):
                custom_fonts.append(font_file.stem)
            for font_file in fonts_dir.glob("*.otf"):
                custom_fonts.append(font_file.stem)
        
        return common_fonts + custom_fonts
    
    def load_whisper_model(self, model_name: str = "base", use_faster: bool = True):
        """加载Whisper模型 - 参考AutoCut的模型加载方式"""
        try:
            if use_faster and FASTER_WHISPER_AVAILABLE:
                print(f"加载Faster-Whisper模型: {model_name}")
                self.faster_whisper_model = WhisperModel(model_name, device="auto")
                print("Faster-Whisper模型加载成功")
            elif WHISPER_AVAILABLE:
                print(f"加载Whisper模型: {model_name}")
                self.whisper_model = whisper.load_model(model_name)
                print("Whisper模型加载成功")
            else:
                raise ImportError("Whisper和Faster-Whisper都不可用")
                
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
            raise
    
    def transcribe_video(self, video_path: str, language: str = "auto", 
                        progress_callback=None) -> bool:
        """转录视频生成字幕 - 参考AutoCut的转录实现"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        if not MOVIEPY_AVAILABLE:
            raise ImportError("MoviePy未安装，无法提取视频音频")
        
        if not self.whisper_model and not self.faster_whisper_model:
            raise ValueError("请先加载Whisper模型")
        
        try:
            if progress_callback:
                progress_callback("提取音频...", 10)
            
            # 提取音频
            video = VideoFileClip(video_path)
            audio_path = "temp/audio.wav"
            os.makedirs("temp", exist_ok=True)
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            
            if progress_callback:
                progress_callback("识别字幕...", 30)
            
            # 使用Whisper进行转录
            if self.faster_whisper_model:
                segments, info = self.faster_whisper_model.transcribe(
                    audio_path, 
                    language=None if language == "auto" else language,
                    word_timestamps=True
                )
                
                self.subtitles.clear()
                for i, segment in enumerate(segments):
                    if progress_callback:
                        progress_callback(f"处理字幕片段 {i+1}...", 30 + (i * 60 / 100))
                    
                    subtitle = SubtitleItem(
                        index=i + 1,
                        start_time=segment.start,
                        end_time=segment.end,
                        text=segment.text.strip(),
                        style=SubtitleStyle()
                    )
                    self.subtitles.append(subtitle)
                    
            else:
                result = self.whisper_model.transcribe(
                    audio_path,
                    language=None if language == "auto" else language,
                    word_timestamps=True
                )
                
                self.subtitles.clear()
                for i, segment in enumerate(result["segments"]):
                    if progress_callback:
                        progress_callback(f"处理字幕片段 {i+1}...", 30 + (i * 60 / 100))
                    
                    subtitle = SubtitleItem(
                        index=i + 1,
                        start_time=segment["start"],
                        end_time=segment["end"],
                        text=segment["text"].strip(),
                        style=SubtitleStyle()
                    )
                    self.subtitles.append(subtitle)
            
            # 清理临时文件
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            if progress_callback:
                progress_callback("完成", 100)
            
            print(f"字幕识别完成，共生成 {len(self.subtitles)} 条字幕")
            return True
            
        except Exception as e:
            print(f"字幕识别失败: {str(e)}")
            return False
    
    def load_srt_file(self, srt_path: str) -> bool:
        """加载SRT字幕文件"""
        try:
            subs = pysrt.open(srt_path, encoding='utf-8')
            self.subtitles.clear()
            
            for i, sub in enumerate(subs):
                start_time = (sub.start.hours * 3600 + 
                            sub.start.minutes * 60 + 
                            sub.start.seconds + 
                            sub.start.milliseconds / 1000.0)
                
                end_time = (sub.end.hours * 3600 + 
                          sub.end.minutes * 60 + 
                          sub.end.seconds + 
                          sub.end.milliseconds / 1000.0)
                
                subtitle = SubtitleItem(
                    index=i + 1,
                    start_time=start_time,
                    end_time=end_time,
                    text=sub.text,
                    style=SubtitleStyle()
                )
                self.subtitles.append(subtitle)
            
            print(f"SRT文件加载成功，共 {len(self.subtitles)} 条字幕")
            return True
            
        except Exception as e:
            print(f"SRT文件加载失败: {str(e)}")
            return False
    
    def save_srt_file(self, output_path: str) -> bool:
        """保存为SRT字幕文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for subtitle in self.subtitles:
                    f.write(subtitle.to_srt_format() + "\n")
            
            print(f"SRT文件保存成功: {output_path}")
            return True
            
        except Exception as e:
            print(f"SRT文件保存失败: {str(e)}")
            return False
    
    def add_subtitle(self, start_time: float, end_time: float, text: str) -> SubtitleItem:
        """添加字幕条目"""
        index = len(self.subtitles) + 1
        subtitle = SubtitleItem(
            index=index,
            start_time=start_time,
            end_time=end_time,
            text=text,
            style=SubtitleStyle()
        )
        self.subtitles.append(subtitle)
        return subtitle
    
    def remove_subtitle(self, index: int):
        """移除字幕条目"""
        if 0 <= index < len(self.subtitles):
            self.subtitles.pop(index)
            # 重新编号
            for i, subtitle in enumerate(self.subtitles):
                subtitle.index = i + 1
    
    def update_subtitle_text(self, index: int, text: str):
        """更新字幕文本"""
        if 0 <= index < len(self.subtitles):
            self.subtitles[index].text = text
    
    def update_subtitle_timing(self, index: int, start_time: float, end_time: float):
        """更新字幕时间"""
        if 0 <= index < len(self.subtitles):
            self.subtitles[index].start_time = start_time
            self.subtitles[index].end_time = end_time
    
    def update_subtitle_style(self, index: int, style: SubtitleStyle):
        """更新字幕样式"""
        if 0 <= index < len(self.subtitles):
            self.subtitles[index].style = style
    
    def apply_style_to_all(self, style: SubtitleStyle):
        """应用样式到所有字幕"""
        for subtitle in self.subtitles:
            subtitle.style = style
    
    def get_subtitles_info(self) -> List[dict]:
        """获取所有字幕信息"""
        return [
            {
                'index': sub.index,
                'start_time': sub.start_time,
                'end_time': sub.end_time,
                'duration': sub.duration,
                'text': sub.text,
                'style': sub.style.__dict__ if sub.style else None
            }
            for sub in self.subtitles
        ]
    
    def clear_subtitles(self):
        """清空所有字幕"""
        self.subtitles.clear()
    
    def get_available_fonts(self) -> List[str]:
        """获取可用字体列表"""
        return self.available_fonts
    
    def install_font(self, font_path: str) -> bool:
        """安装自定义字体"""
        try:
            font_file = Path(font_path)
            if not font_file.exists():
                raise FileNotFoundError(f"字体文件不存在: {font_path}")
            
            # 复制字体文件到fonts目录
            fonts_dir = Path("fonts")
            fonts_dir.mkdir(exist_ok=True)
            
            target_path = fonts_dir / font_file.name
            import shutil
            shutil.copy2(font_path, target_path)
            
            # 更新可用字体列表
            self.available_fonts = self._get_available_fonts()
            
            print(f"字体安装成功: {font_file.name}")
            return True
            
        except Exception as e:
            print(f"字体安装失败: {str(e)}")
            return False