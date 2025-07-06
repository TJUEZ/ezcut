#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
播放头控制器 - 统一管理两个播放头的同步和交互
基于常见视频播放器的最佳实践实现
"""

import time
from typing import Optional, Callable, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication


class PlayheadController(QObject):
    """播放头控制器 - 统一管理播放头同步和交互"""
    
    # 信号定义
    position_changed = pyqtSignal(float)  # 播放头位置变化信号
    scrub_started = pyqtSignal()  # 开始拖动信号
    scrub_ended = pyqtSignal()  # 结束拖动信号
    
    def __init__(self):
        super().__init__()
        
        # 播放头状态
        self.current_time = 0.0
        self.duration = 0.0
        self.is_scrubbing = False
        self.was_playing_before_scrub = False
        
        # 交互状态
        self.interaction_mode = None  # None, 'click', 'drag'
        self.drag_start_time = 0.0
        self.drag_threshold = 5  # 像素阈值，超过此值认为是拖动
        self.click_tolerance = 15  # 播放头点击容差
        
        # 性能优化
        self.last_update_time = 0.0
        self.update_throttle = 0.016  # 60fps限制
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._emit_position_change)
        
        # 注册的播放头组件
        self.timeline_playhead = None  # 红色播放头 (TimelineWidget)
        self.preview_playhead = None   # 方块播放头 (main_window)
        self.preview_playhead_callback = None  # 预览播放头回调函数
        self.media_player = None       # 媒体播放器
        
        # 回调函数
        self.on_play_callback: Optional[Callable] = None
        self.on_pause_callback: Optional[Callable] = None
        self.on_seek_callback: Optional[Callable[[float], None]] = None
    
    def register_timeline_playhead(self, timeline_widget):
        """注册时间轴播放头 (红色播放头)"""
        self.timeline_playhead = timeline_widget
        print("[PlayheadController] 注册时间轴播放头")
    
    def register_preview_playhead(self, timeline_editor):
        """注册预览播放头 (方块播放头)"""
        self.preview_playhead = timeline_editor
        # 为 tkinter 组件添加回调函数
        if hasattr(timeline_editor, 'on_playhead_controller_position_changed'):
            self.preview_playhead_callback = timeline_editor.on_playhead_controller_position_changed
        print("[PlayheadController] 注册预览播放头")
    
    def register_media_player(self, media_player):
        """注册媒体播放器"""
        self.media_player = media_player
        print("[PlayheadController] 注册媒体播放器")
    
    def set_callbacks(self, on_play=None, on_pause=None, on_seek=None):
        """设置回调函数"""
        self.on_play_callback = on_play
        self.on_pause_callback = on_pause
        self.on_seek_callback = on_seek
    
    def set_duration(self, duration: float):
        """设置总时长"""
        self.duration = max(0.0, duration)
        print(f"[PlayheadController] 设置总时长: {self.duration:.2f}s")
    
    def get_current_time(self) -> float:
        """获取当前播放时间"""
        return self.current_time
    
    def is_near_playhead(self, position: float, pixels_per_second: float) -> bool:
        """检查位置是否靠近播放头"""
        playhead_x = self.current_time * pixels_per_second
        position_x = position * pixels_per_second
        return abs(position_x - playhead_x) <= self.click_tolerance
    
    def handle_click(self, time_position: float, is_on_playhead: bool = False) -> bool:
        """处理点击事件
        
        Args:
            time_position: 点击的时间位置
            is_on_playhead: 是否点击在播放头上
            
        Returns:
            bool: 是否处理了点击事件
        """
        if is_on_playhead:
            # 点击在播放头上，准备拖动
            self.interaction_mode = 'click'
            self.drag_start_time = time_position
            print(f"[PlayheadController] 播放头点击，准备拖动模式")
            return True
        else:
            # 点击在时间轴上，跳转播放头
            self.seek_to(time_position)
            print(f"[PlayheadController] 时间轴点击跳转: {time_position:.2f}s")
            return True
    
    def handle_drag_start(self, time_position: float):
        """开始拖动"""
        if self.interaction_mode == 'click':
            self.interaction_mode = 'drag'
            self.is_scrubbing = True
            
            # 暂停播放
            if self.on_pause_callback and not self.was_playing_before_scrub:
                # 记录拖动前的播放状态
                self.was_playing_before_scrub = self._is_playing()
                if self.was_playing_before_scrub:
                    self.on_pause_callback()
            
            self.scrub_started.emit()
            print(f"[PlayheadController] 开始拖动播放头")
    
    def handle_drag(self, time_position: float):
        """处理拖动"""
        if self.interaction_mode == 'click':
            # 检查是否超过拖动阈值
            time_diff = abs(time_position - self.drag_start_time)
            if time_diff > 0.1:  # 100ms阈值
                self.handle_drag_start(time_position)
        
        if self.interaction_mode == 'drag':
            # 更新播放头位置（带性能优化）
            self._update_position_throttled(time_position, scrub=True)
    
    def handle_drag_end(self):
        """结束拖动"""
        if self.interaction_mode in ['click', 'drag']:
            if self.interaction_mode == 'drag':
                self.is_scrubbing = False
                
                # 恢复播放状态
                if self.was_playing_before_scrub and self.on_play_callback:
                    self.on_play_callback()
                
                self.scrub_ended.emit()
                print(f"[PlayheadController] 结束拖动播放头")
            
            self.interaction_mode = None
            self.was_playing_before_scrub = False
    
    def seek_to(self, time_position: float, emit_signal: bool = True):
        """跳转到指定时间位置"""
        # 限制在有效范围内
        time_position = max(0.0, min(time_position, self.duration))
        
        if abs(time_position - self.current_time) < 0.001:  # 1ms阈值
            return  # 位置没有显著变化
        
        self.current_time = time_position
        
        # 同步所有播放头
        self._sync_all_playheads()
        
        # 同步媒体播放器
        if self.on_seek_callback:
            self.on_seek_callback(time_position)
        
        # 发射信号
        if emit_signal:
            self.position_changed.emit(time_position)
        
        print(f"[PlayheadController] 跳转到: {time_position:.3f}s")
    
    def update_from_player(self, time_position: float):
        """从媒体播放器更新位置（播放时）"""
        if not self.is_scrubbing:  # 只在非拖动状态下更新
            self._update_position_throttled(time_position, scrub=False)
    
    def _update_position_throttled(self, time_position: float, scrub: bool = False):
        """带性能优化的位置更新"""
        current_time = time.time()
        
        # 性能优化：限制更新频率
        if current_time - self.last_update_time < self.update_throttle:
            # 使用防抖定时器延迟更新
            self.debounce_timer.stop()
            self.debounce_timer.start(int(self.update_throttle * 1000))
            self._pending_time = time_position
            self._pending_scrub = scrub
            return
        
        self.last_update_time = current_time
        self._do_update_position(time_position, scrub)
    
    def _do_update_position(self, time_position: float, scrub: bool = False):
        """实际执行位置更新"""
        # 限制在有效范围内
        time_position = max(0.0, min(time_position, self.duration))
        
        if abs(time_position - self.current_time) < 0.001:  # 1ms阈值
            return  # 位置没有显著变化
        
        self.current_time = time_position
        
        # 同步所有播放头
        self._sync_all_playheads()
        
        # 在拖动时同步媒体播放器
        if scrub and self.on_seek_callback:
            self.on_seek_callback(time_position)
        
        # 发射信号
        self.position_changed.emit(time_position)
    
    def _emit_position_change(self):
        """防抖定时器回调"""
        if hasattr(self, '_pending_time'):
            self._do_update_position(self._pending_time, getattr(self, '_pending_scrub', False))
            delattr(self, '_pending_time')
            if hasattr(self, '_pending_scrub'):
                delattr(self, '_pending_scrub')
    
    def _sync_all_playheads(self):
        """同步所有播放头的显示"""
        try:
            # 同步时间轴播放头 (红色播放头)
            if self.timeline_playhead:
                if hasattr(self.timeline_playhead, 'on_playhead_controller_position_changed'):
                    self.timeline_playhead.on_playhead_controller_position_changed(self.current_time)
                elif hasattr(self.timeline_playhead, 'set_current_time'):
                    self.timeline_playhead.set_current_time(self.current_time)
                elif hasattr(self.timeline_playhead, 'draw_playhead'):
                    self.timeline_playhead.current_time = self.current_time
                    # 使用 QApplication.processEvents() 确保UI更新
                    QApplication.processEvents()
                    self.timeline_playhead.draw_playhead()
            
            # 同步预览播放头 (方块播放头)
            if self.preview_playhead:
                if hasattr(self, 'preview_playhead_callback') and hasattr(self.preview_playhead_callback, '__call__'):
                    self.preview_playhead_callback(self.current_time)
                elif hasattr(self.preview_playhead, 'current_time'):
                    self.preview_playhead.current_time = self.current_time
                    if hasattr(self.preview_playhead, 'draw_playhead'):
                        # 延迟更新以避免UI冲突
                        if hasattr(self.preview_playhead, 'app') and hasattr(self.preview_playhead.app, 'root'):
                            self.preview_playhead.app.root.after_idle(self.preview_playhead.draw_playhead)
                        else:
                            self.preview_playhead.draw_playhead()
        
        except Exception as e:
            print(f"[PlayheadController] 同步播放头时出错: {e}")
    
    def _is_playing(self) -> bool:
        """检查是否正在播放"""
        try:
            if self.media_player and hasattr(self.media_player, 'playbackState'):
                from PyQt6.QtMultimedia import QMediaPlayer
                return self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
            return False
        except Exception:
            return False
    
    def reset(self):
        """重置播放头状态"""
        self.current_time = 0.0
        self.is_scrubbing = False
        self.was_playing_before_scrub = False
        self.interaction_mode = None
        self._sync_all_playheads()
        print("[PlayheadController] 重置播放头状态")


# 全局播放头控制器实例
playhead_controller = PlayheadController()