#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EzCut - 专业桌面视频编辑器 (PyQt6版本)

基于以下开源项目的最佳实践:
- OpenShot Video Editor: https://github.com/OpenShot/openshot-qt
- QTimeLine Widget: https://github.com/asnunes/QTimeLine
- Simple Video Editor: https://github.com/Oscarshu0719/video-editor

主要功能:
- 多轨道时间轴编辑
- 拖拽式媒体导入
- 实时视频预览
- 视频剪切、分割、合并
- 音频轨道编辑
- 效果和转场
- 导出多种格式
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
import threading
import time

# PyQt6 imports
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
        QLabel, QPushButton, QSlider, QProgressBar, QMenuBar, QMenu,
        QToolBar, QStatusBar, QFileDialog, QMessageBox, QDialog,
        QDialogButtonBox, QFormLayout, QLineEdit, QSpinBox, QComboBox,
        QGroupBox, QCheckBox, QTabWidget, QTextEdit, QScrollArea,
        QFrame, QSizePolicy, QGraphicsView, QGraphicsScene, QGraphicsItem,
        QGraphicsRectItem, QGraphicsPixmapItem, QRubberBand, QHeaderView
    )
    from PyQt6.QtCore import (
        Qt, QTimer, QThread, pyqtSignal, QObject, QRect, QPoint, QSize,
        QPropertyAnimation, QEasingCurve, QAbstractAnimation, QMimeData,
        QUrl, QFileInfo, QDir, QStandardPaths, QSettings
    )
    from PyQt6.QtGui import (
        QPixmap, QIcon, QFont, QColor, QPalette, QPainter, QBrush, QPen,
        QLinearGradient, QAction, QKeySequence, QDragEnterEvent, QDropEvent,
        QDrag, QCursor, QMovie, QFontDatabase, QImage, QPainterPath
    )
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PyQt6.QtMultimediaWidgets import QVideoWidget
    PYQT_AVAILABLE = True
except ImportError as e:
    print(f"PyQt6 未安装: {e}")
    print("请安装 PyQt6: pip install PyQt6")
    PYQT_AVAILABLE = False
    sys.exit(1)

# OpenCV for video processing
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    print("OpenCV 未安装，视频处理功能将受限")
    CV2_AVAILABLE = False

# MoviePy for advanced video editing
try:
    import moviepy
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
        MOVIEPY_AVAILABLE = True
        print("MoviePy 已安装 (完整版本)")
    except ImportError:
        print("MoviePy 已安装但editor模块缺失，高级编辑功能将受限")
        print("建议重新安装: pip install --upgrade moviepy")
        MOVIEPY_AVAILABLE = False
except ImportError:
    print("MoviePy 未安装，高级编辑功能将受限")
    MOVIEPY_AVAILABLE = False

# PIL for image processing
try:
    from PIL import Image, ImageQt
    PIL_AVAILABLE = True
except ImportError:
    print("Pillow 未安装，图像处理功能将受限")
    PIL_AVAILABLE = False

class MediaItem:
    """媒体项目类"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.name = self.file_path.name
        self.duration = 0.0
        self.fps = 30.0
        self.width = 0
        self.height = 0
        self.file_size = 0
        self.media_type = self._detect_media_type()
        self.thumbnail = None
        self._load_metadata()
    
    def _detect_media_type(self) -> str:
        """检测媒体类型"""
        ext = self.file_path.suffix.lower()
        if ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.webm']:
            return 'video'
        elif ext in ['.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg']:
            return 'audio'
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']:
            return 'image'
        else:
            return 'unknown'
    
    def is_valid_media_file(self) -> bool:
        """检查是否为有效的媒体文件"""
        return self.media_type != 'unknown'
    
    def _load_metadata(self):
        """加载媒体元数据"""
        try:
            if not self.file_path.exists():
                return
            
            self.file_size = self.file_path.stat().st_size
            
            if self.media_type == 'video' and CV2_AVAILABLE:
                cap = cv2.VideoCapture(str(self.file_path))
                if cap.isOpened():
                    self.fps = cap.get(cv2.CAP_PROP_FPS)
                    self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    if self.fps > 0:
                        self.duration = frame_count / self.fps
                    cap.release()
            
            elif self.media_type == 'image' and PIL_AVAILABLE:
                with Image.open(self.file_path) as img:
                    self.width, self.height = img.size
                    self.duration = 5.0  # 默认图片显示5秒
                    
        except Exception as e:
            print(f"加载媒体元数据失败 {self.file_path}: {e}")
    
    def generate_thumbnail(self, size: Tuple[int, int] = (120, 90)) -> Optional[QPixmap]:
        """生成缩略图"""
        try:
            if self.media_type == 'video' and CV2_AVAILABLE:
                cap = cv2.VideoCapture(str(self.file_path))
                if cap.isOpened():
                    # 尝试获取多个帧，选择最佳的一帧
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    best_frame = None
                    
                    # 尝试获取几个不同位置的帧
                    positions = [frame_count // 4, frame_count // 2, frame_count * 3 // 4]
                    
                    for pos in positions:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
                        ret, frame = cap.read()
                        if ret:
                            # 检查帧是否不是纯黑色（避免黑屏）
                            if cv2.mean(frame)[0] > 10:  # 平均亮度大于10
                                best_frame = frame
                                break
                    
                    # 如果没有找到合适的帧，使用中间帧
                    if best_frame is None:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
                        ret, best_frame = cap.read()
                    
                    if best_frame is not None:
                        # 转换颜色空间
                        frame_rgb = cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = frame_rgb.shape
                        bytes_per_line = ch * w
                        
                        # 创建QImage
                        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                        
                        # 转换为QPixmap并缩放
                        pixmap = QPixmap.fromImage(qt_image)
                        self.thumbnail = pixmap.scaled(
                            size[0], size[1], 
                            Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        
                        # 添加圆角效果
                        self.thumbnail = self._add_rounded_corners(self.thumbnail)
                    
                    cap.release()
            
            elif self.media_type == 'image' and PIL_AVAILABLE:
                with Image.open(self.file_path) as img:
                    # 转换为RGB模式（处理RGBA等格式）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 计算缩放比例，保持宽高比
                    img_ratio = img.width / img.height
                    target_ratio = size[0] / size[1]
                    
                    if img_ratio > target_ratio:
                        # 图片更宽，以宽度为准
                        new_width = size[0]
                        new_height = int(size[0] / img_ratio)
                    else:
                        # 图片更高，以高度为准
                        new_height = size[1]
                        new_width = int(size[1] * img_ratio)
                    
                    # 高质量缩放
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # 转换为QPixmap
                    qt_image = ImageQt.ImageQt(img_resized)
                    self.thumbnail = QPixmap.fromImage(qt_image)
                    
                    # 添加圆角效果
                    self.thumbnail = self._add_rounded_corners(self.thumbnail)
            
            elif self.media_type == 'audio':
                # 为音频文件创建美观的默认图标
                self.thumbnail = self._create_audio_thumbnail(size)
            
            return self.thumbnail
            
        except Exception as e:
            print(f"生成缩略图失败 {self.file_path}: {e}")
            return None
    
    def _add_rounded_corners(self, pixmap: QPixmap, radius: int = 8) -> QPixmap:
        """为缩略图添加圆角效果"""
        try:
            rounded = QPixmap(pixmap.size())
            rounded.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 创建圆角矩形路径
            path = QPainterPath()
            path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), radius, radius)
            
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            
            return rounded
        except:
            return pixmap  # 如果失败，返回原图
    
    def _create_audio_thumbnail(self, size: Tuple[int, int]) -> QPixmap:
        """创建音频文件的美观缩略图"""
        pixmap = QPixmap(size[0], size[1])
        
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, size[0], size[1])
        gradient.setColorAt(0, QColor(76, 175, 80))  # 绿色
        gradient.setColorAt(1, QColor(139, 195, 74))  # 浅绿色
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(pixmap.rect(), QBrush(gradient))
        
        # 绘制音频波形图案
        painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
        
        # 绘制简化的音频波形
        import random
        random.seed(hash(str(self.file_path)))  # 基于文件路径生成固定的随机数
        
        wave_width = size[0] - 20
        wave_height = size[1] - 40
        start_x = 10
        start_y = size[1] // 2
        
        for i in range(0, wave_width, 4):
            height = random.randint(5, wave_height // 2)
            painter.drawLine(start_x + i, start_y - height, start_x + i, start_y + height)
        
        # 绘制音符图标
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "♪")
        
        painter.end()
        return pixmap

class TimelineClip:
    """时间轴剪辑片段"""
    
    def __init__(self, media_item: MediaItem, track: int, start_time: float, duration: float):
        self.media_item = media_item
        self.track = track
        self.start_time = start_time
        self.duration = duration
        self.in_point = 0.0  # 媒体文件内的起始点
        self.out_point = duration  # 媒体文件内的结束点
        self.selected = False
        self.locked = False
        
    @property
    def end_time(self) -> float:
        return self.start_time + self.duration
    
    def move_to(self, new_start_time: float):
        """移动剪辑到新位置"""
        self.start_time = new_start_time
    
    def resize(self, new_duration: float):
        """调整剪辑长度"""
        if new_duration > 0:
            self.duration = new_duration
            self.out_point = self.in_point + new_duration

class CustomMediaListWidget(QListWidget):
    """自定义媒体列表组件，重写拖拽方法"""
    
    def __init__(self):
        super().__init__()
        self.media_library = None
    
    def startDrag(self, supportedActions):
        """重写拖拽方法，避免返回值问题"""
        try:
            current_item = self.currentItem()
            if current_item is None:
                return
                
            # 获取媒体项索引
            media_index = current_item.data(Qt.ItemDataRole.UserRole)
            if media_index is None:
                return
                
            # 创建拖拽对象
            drag = QDrag(self)
            mime_data = QMimeData()
            
            # 设置自定义数据
            mime_data.setText(f"media_item:{media_index}")
            mime_data.setData("application/x-media-item", str(media_index).encode())
            
            # 设置拖拽图标
            if current_item.icon():
                pixmap = current_item.icon().pixmap(64, 48)
                drag.setPixmap(pixmap)
                drag.setHotSpot(pixmap.rect().center())
            
            drag.setMimeData(mime_data)
            
            # 执行拖拽，不处理返回值
            drag.exec(Qt.DropAction.CopyAction)
            
        except Exception as e:
            print(f"拖拽操作出错: {e}")

class MediaLibraryWidget(QWidget):
    """媒体库组件"""
    
    media_dropped = pyqtSignal(str, int)  # 文件路径, 轨道号
    
    def __init__(self):
        super().__init__()
        self.media_items: List[MediaItem] = []
        self.setup_ui()
        self.setAcceptDrops(True)
        
        # 启用鼠标点击事件
        self.setMouseTracking(True)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题栏
        header = QHBoxLayout()
        title = QLabel("媒体库")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(title)
        
        import_btn = QPushButton("导入")
        import_btn.clicked.connect(self.import_media)
        header.addWidget(import_btn)
        
        layout.addLayout(header)
        
        # 媒体列表 - 使用自定义组件
        self.media_list = CustomMediaListWidget()
        self.media_list.media_library = self  # 设置引用
        self.media_list.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.media_list.setDefaultDropAction(Qt.DropAction.CopyAction)
        
        # 连接双击事件
        self.media_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # 设置为图标视图模式，突出显示缩略图
        self.media_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.media_list.setIconSize(QSize(120, 90))  # 更大的图标尺寸
        self.media_list.setGridSize(QSize(140, 130))  # 网格大小
        self.media_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.media_list.setMovement(QListWidget.Movement.Static)
        self.media_list.setWordWrap(True)
        
        # 启用拖拽功能
        self.media_list.setDragEnabled(True)
        self.media_list.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        
        # 设置样式
        self.media_list.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QListWidget::item {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin: 2px;
                padding: 4px;
                text-align: center;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
                border-color: #0056b3;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
                border-color: #2196f3;
            }
        """)
        
        layout.addWidget(self.media_list)
    
    def import_media(self):
        """导入媒体文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择媒体文件",
            "",
            "媒体文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.m4v *.webm *.mp3 *.wav *.aac *.m4a *.flac *.ogg *.jpg *.jpeg *.png *.bmp *.gif *.tiff);;" +
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.m4v *.webm);;" +
            "音频文件 (*.mp3 *.wav *.aac *.m4a *.flac *.ogg);;" +
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif *.tiff);;" +
            "所有文件 (*)"
        )
        
        for file_path in file_paths:
            self.add_media_item(file_path)
    
    def add_media_item(self, file_path: str):
        """添加媒体项目"""
        # 创建媒体项目并验证文件类型
        media_item = MediaItem(file_path)
        
        # 检查是否为有效的媒体文件
        if not media_item.is_valid_media_file():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "无效文件类型",
                f"文件 '{media_item.name}' 不是支持的媒体文件类型。\n\n"
                f"支持的格式：\n"
                f"• 视频：mp4, avi, mov, mkv, wmv, flv, m4v, webm\n"
                f"• 音频：mp3, wav, aac, m4a, flac, ogg\n"
                f"• 图片：jpg, jpeg, png, bmp, gif, tiff"
            )
            return
        
        self.media_items.append(media_item)
        
        # 创建列表项
        list_item = QListWidgetItem()
        
        # 简化文本显示，重点突出文件名
        file_name = media_item.name
        if len(file_name) > 15:
            file_name = file_name[:12] + "..."
        
        # 根据媒体类型显示不同信息
        if media_item.media_type == 'video':
            duration_text = f"{media_item.duration:.1f}s"
            resolution_text = f"{media_item.width}x{media_item.height}" if media_item.width > 0 else ""
            list_item.setText(f"{file_name}\n{duration_text}\n{resolution_text}")
        elif media_item.media_type == 'audio':
            duration_text = f"{media_item.duration:.1f}s"
            list_item.setText(f"{file_name}\n{duration_text}\n♪ 音频")
        elif media_item.media_type == 'image':
            resolution_text = f"{media_item.width}x{media_item.height}" if media_item.width > 0 else ""
            list_item.setText(f"{file_name}\n🖼️ 图片\n{resolution_text}")
        else:
            list_item.setText(f"{file_name}\n未知格式")
        
        list_item.setData(Qt.ItemDataRole.UserRole, len(self.media_items) - 1)
        
        # 生成更大尺寸的缩略图
        thumbnail = media_item.generate_thumbnail((120, 90))
        if thumbnail:
            list_item.setIcon(QIcon(thumbnail))
        else:
            # 如果无法生成缩略图，创建默认图标
            self._create_default_icon(list_item, media_item.media_type)
        
        # 设置工具提示显示完整信息
        tooltip = f"文件: {media_item.name}\n"
        tooltip += f"路径: {media_item.file_path}\n"
        tooltip += f"类型: {media_item.media_type}\n"
        if media_item.duration > 0:
            tooltip += f"时长: {media_item.duration:.2f}秒\n"
        if media_item.width > 0 and media_item.height > 0:
            tooltip += f"分辨率: {media_item.width}x{media_item.height}\n"
        if media_item.file_size > 0:
            size_mb = media_item.file_size / (1024 * 1024)
            tooltip += f"大小: {size_mb:.1f}MB"
        list_item.setToolTip(tooltip)
        
        self.media_list.addItem(list_item)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def _create_default_icon(self, list_item: QListWidgetItem, media_type: str):
        """为无法生成缩略图的文件创建默认图标"""
        pixmap = QPixmap(120, 90)
        
        if media_type == 'video':
            pixmap.fill(QColor(100, 150, 255))
            icon_text = "🎬"
        elif media_type == 'audio':
            pixmap.fill(QColor(100, 255, 150))
            icon_text = "🎵"
        elif media_type == 'image':
            pixmap.fill(QColor(255, 150, 100))
            icon_text = "🖼️"
        else:
            pixmap.fill(QColor(200, 200, 200))
            icon_text = "📄"
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 24))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, icon_text)
        painter.end()
        
        list_item.setIcon(QIcon(pixmap))
    

    
    def get_media_item(self, index: int) -> Optional[MediaItem]:
        """根据索引获取媒体项"""
        if 0 <= index < len(self.media_items):
            return self.media_items[index]
        return None
    
    def on_item_double_clicked(self, item):
        """处理媒体项双击事件"""
        try:
            # 获取媒体项索引
            media_index = item.data(Qt.ItemDataRole.UserRole)
            if media_index is not None:
                media_item = self.get_media_item(media_index)
                if media_item:
                    # 获取主窗口引用
                    main_window = self.get_main_window()
                    if main_window and hasattr(main_window, 'video_preview'):
                        # 加载媒体到预览器
                        main_window.video_preview.load_media(media_item.file_path)
                        print(f"已加载媒体到预览器: {media_item.name}")
        except Exception as e:
            print(f"双击加载媒体时出错: {e}")
    
    def get_main_window(self):
        """获取主窗口引用"""
        widget = self
        while widget.parent():
            widget = widget.parent()
            if isinstance(widget, QMainWindow):
                return widget
        return None
    
    def dropEvent(self, event: QDropEvent):
        """处理文件拖拽事件"""
        valid_files = []
        invalid_files = []
        
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                # 预先检查文件类型
                temp_media_item = MediaItem(file_path)
                if temp_media_item.is_valid_media_file():
                    valid_files.append(file_path)
                else:
                    invalid_files.append(os.path.basename(file_path))
        
        # 添加有效文件
        for file_path in valid_files:
            self.add_media_item(file_path)
        
        # 如果有无效文件，显示警告
        if invalid_files:
            from PyQt6.QtWidgets import QMessageBox
            invalid_list = "\n• ".join(invalid_files)
            QMessageBox.warning(
                self,
                "部分文件无法导入",
                f"以下文件不是支持的媒体文件类型，已跳过：\n\n• {invalid_list}\n\n"
                f"支持的格式：\n"
                f"• 视频：mp4, avi, mov, mkv, wmv, flv, m4v, webm\n"
                f"• 音频：mp3, wav, aac, m4a, flac, ogg\n"
                f"• 图片：jpg, jpeg, png, bmp, gif, tiff"
            )
        
        event.acceptProposedAction()

class TimelineWidget(QGraphicsView):
    """时间轴组件"""
    
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        self.clips: List[TimelineClip] = []
        self.tracks = 5  # 默认5个轨道
        self.track_height = 60
        self.pixels_per_second = 50
        self.timeline_duration = 300  # 5分钟
        self.current_time = 0.0  # 当前播放时间
        
        # 拖拽状态管理
        self.is_dragging = False
        self.last_preview_pos = None
        self.preview_items = []  # 跟踪预览项
        
        # 播放头
        self.playhead = None
        
        self.setup_ui()
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """设置UI"""
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置场景大小
        scene_width = self.timeline_duration * self.pixels_per_second
        scene_height = self.tracks * self.track_height
        self.scene.setSceneRect(0, 0, scene_width, scene_height)
        
        # 绘制轨道背景
        self.draw_tracks()
        
        # 绘制时间标尺
        self.draw_time_ruler()
        
        # 绘制播放头
        self.draw_playhead()
    
    def draw_tracks(self):
        """绘制轨道背景"""
        for i in range(self.tracks):
            y = i * self.track_height
            
            # 轨道背景
            track_rect = QGraphicsRectItem(0, y, self.scene.width(), self.track_height)
            if i % 2 == 0:
                track_rect.setBrush(QBrush(QColor(240, 240, 240)))
            else:
                track_rect.setBrush(QBrush(QColor(250, 250, 250)))
            track_rect.setPen(QPen(QColor(200, 200, 200)))
            self.scene.addItem(track_rect)
            
            # 轨道标签
            label = self.scene.addText(f"轨道 {i+1}", QFont("Arial", 10))
            label.setPos(5, y + 5)
    
    def draw_time_ruler(self):
        """绘制时间标尺"""
        ruler_height = 30
        ruler_rect = QGraphicsRectItem(0, -ruler_height, self.scene.width(), ruler_height)
        ruler_rect.setBrush(QBrush(QColor(220, 220, 220)))
        ruler_rect.setPen(QPen(QColor(180, 180, 180)))
        self.scene.addItem(ruler_rect)
        
        # 时间刻度
        for second in range(0, int(self.timeline_duration) + 1, 10):
            x = second * self.pixels_per_second
            
            # 主刻度线
            line = self.scene.addLine(x, -ruler_height, x, -ruler_height + 15, QPen(QColor(100, 100, 100)))
            
            # 时间标签
            minutes = second // 60
            seconds = second % 60
            time_text = f"{minutes:02d}:{seconds:02d}"
            label = self.scene.addText(time_text, QFont("Arial", 8))
            label.setPos(x + 2, -ruler_height + 2)
    
    def draw_playhead(self):
        """绘制播放头"""
        if self.playhead:
            self.scene.removeItem(self.playhead)
        
        # 播放头线条
        x = self.current_time * self.pixels_per_second
        self.playhead = self.scene.addLine(
            x, -30, x, self.scene.height(),
            QPen(QColor(255, 0, 0), 2)  # 红色播放头
        )
        
        # 播放头顶部三角形
        triangle_size = 8
        triangle_points = [
            QPoint(int(x), -30),
            QPoint(int(x - triangle_size), -30 + triangle_size),
            QPoint(int(x + triangle_size), -30 + triangle_size)
        ]
        
        from PyQt6.QtGui import QPolygonF
        from PyQt6.QtCore import QPointF
        triangle = QPolygonF([QPointF(p.x(), p.y()) for p in triangle_points])
        triangle_item = self.scene.addPolygon(triangle, QPen(QColor(255, 0, 0)), QBrush(QColor(255, 0, 0)))
        triangle_item.setZValue(10)  # 确保三角形在最上层
    
    def update_playhead_position(self, time_seconds: float):
        """更新播放头位置"""
        self.current_time = max(0, min(time_seconds, self.timeline_duration))
        self.draw_playhead()
        
        # 自动滚动到播放头位置
        x = self.current_time * self.pixels_per_second
        self.centerOn(x, self.scene.height() / 2)
    
    def get_current_time(self) -> float:
        """获取当前播放时间"""
        return self.current_time
    
    def mousePressEvent(self, event):
        """鼠标点击事件 - 设置播放位置"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 将点击位置转换为场景坐标
            scene_pos = self.mapToScene(event.position().toPoint())
            
            # 计算时间位置
            clicked_time = max(0, min(scene_pos.x() / self.pixels_per_second, self.timeline_duration))
            
            # 更新播放头位置
            self.update_playhead_position(clicked_time)
            
            # 通知主窗口更新播放位置
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'video_preview'):
                # 设置视频播放位置（转换为毫秒）
                position_ms = int(clicked_time * 1000)
                main_window.video_preview.media_player.setPosition(position_ms)
        
        super().mousePressEvent(event)
    
    def get_main_window(self):
        """获取主窗口引用"""
        widget = self
        while widget.parent():
            widget = widget.parent()
            if isinstance(widget, MainWindow):
                return widget
        return None
    
    def add_clip(self, media_item: MediaItem, track: int, start_time: float):
        """添加剪辑到时间轴"""
        clip = TimelineClip(media_item, track, start_time, media_item.duration)
        self.clips.append(clip)
        
        # 创建剪辑的图形表示
        x = start_time * self.pixels_per_second
        y = track * self.track_height
        width = clip.duration * self.pixels_per_second
        height = self.track_height - 4
        
        clip_rect = QGraphicsRectItem(x, y + 2, width, height)
        
        # 根据媒体类型设置颜色
        if media_item.media_type == 'video':
            clip_rect.setBrush(QBrush(QColor(100, 150, 255)))
        elif media_item.media_type == 'audio':
            clip_rect.setBrush(QBrush(QColor(100, 255, 150)))
        else:
            clip_rect.setBrush(QBrush(QColor(255, 150, 100)))
        
        clip_rect.setPen(QPen(QColor(50, 50, 50)))
        self.scene.addItem(clip_rect)
        
        # 添加剪辑标签
        label = self.scene.addText(media_item.name, QFont("Arial", 9))
        label.setPos(x + 5, y + 5)
        label.setDefaultTextColor(QColor(255, 255, 255))
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        # 接受来自媒体库的拖拽或文件拖拽
        if (event.mimeData().hasFormat("application/x-media-item") or 
            event.mimeData().hasUrls()):
            self.is_dragging = False  # 重置状态
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        try:
            self.clear_drop_preview()
            self.last_preview_pos = None
            self.is_dragging = False
        except:
            pass  # 忽略清理时的错误
        super().dragLeaveEvent(event)
    
    def dragMoveEvent(self, event):
        """拖拽移动事件 - 显示放置预览"""
        if (event.mimeData().hasFormat("application/x-media-item") or 
            event.mimeData().hasUrls()):
            
            current_pos = event.position().toPoint()
            
            # 防抖：只有位置变化超过阈值才更新预览
            if (self.last_preview_pos is None or 
                abs(current_pos.x() - self.last_preview_pos.x()) > 10 or
                abs(current_pos.y() - self.last_preview_pos.y()) > 5):
                
                # 计算当前位置
                pos = self.mapToScene(current_pos)
                track = max(0, min(int(pos.y() // self.track_height), self.tracks - 1))
                start_time = max(0, pos.x() / self.pixels_per_second)
                
                # 清除之前的预览
                self.clear_drop_preview()
                
                # 获取实际媒体时长用于预览
                duration = 5.0  # 默认时长
                if event.mimeData().hasFormat("application/x-media-item"):
                    try:
                        media_index_data = event.mimeData().data("application/x-media-item")
                        media_index = int(media_index_data.data().decode())
                        
                        main_window = self.get_main_window()
                        if main_window and hasattr(main_window, 'media_library'):
                            media_item = main_window.media_library.get_media_item(media_index)
                            if media_item and media_item.duration > 0:
                                duration = media_item.duration
                    except:
                        pass
                
                # 显示放置预览
                self.show_drop_preview(track, start_time, duration)
                self.last_preview_pos = current_pos
            
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def clear_drop_preview(self):
        """清除拖拽预览"""
        # 移除所有预览项
        for item in self.preview_items[:]:
            if item.scene() == self.scene:
                self.scene.removeItem(item)
        self.preview_items.clear()
    
    def show_drop_preview(self, track: int, start_time: float, duration: float = 5.0):
        """显示拖拽预览"""
        # 创建预览矩形
        x = start_time * self.pixels_per_second
        y = track * self.track_height
        width = duration * self.pixels_per_second  # 根据实际时长计算宽度
        height = self.track_height - 4
        
        preview_rect = self.scene.addRect(x, y + 2, width, height)
        preview_rect.setBrush(QBrush(QColor(100, 150, 255, 100)))  # 半透明蓝色
        preview_rect.setPen(QPen(QColor(50, 100, 200), 2, Qt.PenStyle.DashLine))
        preview_rect.is_preview = True  # 标记为预览项
        self.preview_items.append(preview_rect)
        
        # 添加预览标签
        preview_label = self.scene.addText(f"预览 ({duration:.1f}s)", QFont("Arial", 8))
        preview_label.setPos(x + 5, y + 5)
        preview_label.setDefaultTextColor(QColor(50, 100, 200))
        preview_label.is_preview = True
        self.preview_items.append(preview_label)
    
    def dropEvent(self, event: QDropEvent):
        """处理拖拽放置事件"""
        # 防止重复处理
        if self.is_dragging:
            return
            
        self.is_dragging = True
        
        try:
            # 清除预览
            self.clear_drop_preview()
            self.last_preview_pos = None
            
            # 计算放置位置
            pos = self.mapToScene(event.position().toPoint())
            track = max(0, min(int(pos.y() // self.track_height), self.tracks - 1))
            start_time = max(0, pos.x() / self.pixels_per_second)
            
            if event.mimeData().hasFormat("application/x-media-item"):
                # 处理来自媒体库的拖拽
                try:
                    media_index_data = event.mimeData().data("application/x-media-item")
                    media_index = int(media_index_data.data().decode())
                    
                    # 获取主窗口和媒体项
                    main_window = self.get_main_window()
                    if main_window and hasattr(main_window, 'media_library'):
                        media_item = main_window.media_library.get_media_item(media_index)
                        if media_item:
                            # 添加到时间轴
                            self.add_clip(media_item, track, start_time)
                            print(f"媒体已添加到轨道 {track + 1}，时间 {start_time:.2f}s")
                            event.acceptProposedAction()
                            return
                except Exception as e:
                    print(f"处理媒体拖拽时出错: {e}")
            
            elif event.mimeData().hasUrls():
                # 处理文件拖拽
                valid_files = []
                invalid_files = []
                
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if os.path.isfile(file_path):
                            # 验证文件类型
                            temp_media_item = MediaItem(file_path)
                            if temp_media_item.is_valid_media_file():
                                valid_files.append(file_path)
                            else:
                                invalid_files.append(os.path.basename(file_path))
                
                # 添加有效文件到时间轴
                for file_path in valid_files:
                    media_item = MediaItem(file_path)
                    self.add_clip(media_item, track, start_time)
                    print(f"文件已添加到轨道 {track + 1}，时间 {start_time:.2f}s")
                    # 只添加第一个有效文件到当前位置
                    break
                
                # 如果有无效文件，显示警告
                if invalid_files:
                    from PyQt6.QtWidgets import QMessageBox
                    invalid_list = "\n• ".join(invalid_files)
                    QMessageBox.warning(
                        self,
                        "无法添加到时间轴",
                        f"以下文件不是支持的媒体文件类型：\n\n• {invalid_list}\n\n"
                        f"支持的格式：\n"
                        f"• 视频：mp4, avi, mov, mkv, wmv, flv, m4v, webm\n"
                        f"• 音频：mp3, wav, aac, m4a, flac, ogg\n"
                        f"• 图片：jpg, jpeg, png, bmp, gif, tiff"
                    )
                
                if valid_files or invalid_files:
                    event.acceptProposedAction()
                else:
                    event.ignore()
            else:
                event.ignore()
        finally:
            # 重置拖拽状态
            self.is_dragging = False
    
    def get_main_window(self):
        """获取主窗口引用"""
        parent = self.parent()
        while parent:
            if isinstance(parent, QMainWindow):
                return parent
            parent = parent.parent()
        return None

class VideoPreviewWidget(QWidget):
    """视频预览组件"""
    
    # 添加信号
    positionChanged = pyqtSignal(float)  # 播放位置改变信号
    
    def __init__(self):
        super().__init__()
        self.current_media = None
        self.timeline_widget = None  # 时间轴组件引用
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 视频显示区域
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(400, 300)
        # 设置背景色以便调试
        self.video_widget.setStyleSheet("background-color: #2b2b2b; border: 1px solid #555;")
        layout.addWidget(self.video_widget)
        
        # 播放控制
        controls = QHBoxLayout()
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 40)
        controls.addWidget(self.play_btn)
        
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        controls.addWidget(self.position_slider)
        
        self.time_label = QLabel("00:00 / 00:00")
        controls.addWidget(self.time_label)
        
        layout.addLayout(controls)
        
        # 媒体播放器
        print("[DEBUG] 初始化QMediaPlayer...")
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        
        # 设置音频输出
        self.media_player.setAudioOutput(self.audio_output)
        print(f"[DEBUG] 音频输出已设置: {self.audio_output}")
        
        # 设置视频输出
        self.media_player.setVideoOutput(self.video_widget)
        print(f"[DEBUG] 视频输出已设置: {self.video_widget}")
        
        # 连接信号
        self.play_btn.clicked.connect(self.toggle_playback)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.position_slider.sliderMoved.connect(self.set_position)
        
        # 添加错误处理和状态监控
        self.media_player.errorOccurred.connect(self.handle_error)
        self.media_player.playbackStateChanged.connect(self.handle_state_change)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        
        print(f"[DEBUG] QMediaPlayer初始化完成，初始状态: {self.media_player.playbackState()}")
    
    def load_media(self, file_path):
        """加载媒体文件"""
        # 确保文件路径是字符串格式
        if hasattr(file_path, '__str__'):
            file_path_str = str(file_path)
        else:
            file_path_str = file_path
            
        self.current_media = file_path_str
        
        # 检查文件是否存在
        import os
        if not os.path.exists(file_path_str):
            print(f"[ERROR] 文件不存在 - {file_path_str}")
            return
            
        # 检查文件大小
        file_size = os.path.getsize(file_path_str)
        print(f"[DEBUG] 文件大小: {file_size / (1024*1024):.2f}MB")
        
        # 检查文件扩展名
        file_ext = os.path.splitext(file_path_str)[1].lower()
        print(f"[DEBUG] 文件扩展名: {file_ext}")
        
        # 设置媒体源
        media_url = QUrl.fromLocalFile(file_path_str)
        print(f"[DEBUG] 正在加载媒体: {file_path_str}")
        print(f"[DEBUG] 媒体URL: {media_url.toString()}")
        print(f"[DEBUG] URL是否有效: {media_url.isValid()}")
        print(f"[DEBUG] URL是否为本地文件: {media_url.isLocalFile()}")
        
        # 停止当前播放
        print(f"[DEBUG] 停止当前播放，当前状态: {self.media_player.playbackState()}")
        self.media_player.stop()
        
        # 设置新的媒体源
        print(f"[DEBUG] 设置媒体源...")
        self.media_player.setSource(media_url)
        
        # 重置播放按钮状态
        self.play_btn.setText("▶")
        
        print(f"[DEBUG] 媒体源已设置，当前播放状态: {self.media_player.playbackState()}")
        print(f"[DEBUG] 媒体状态: {self.media_player.mediaStatus()}")
        print(f"[DEBUG] 媒体持续时间: {self.media_player.duration()}ms")
        print(f"[DEBUG] 视频输出对象: {self.media_player.videoOutput()}")
        print(f"[DEBUG] 音频输出对象: {self.media_player.audioOutput()}")
        
        # 尝试立即播放以测试
        print(f"[DEBUG] 尝试立即播放进行测试...")
        self.media_player.play()
        
        # 等待一小段时间后检查状态
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, self.check_media_load_status)
    
    def check_media_load_status(self):
        """检查媒体加载状态"""
        print(f"[DEBUG] === 媒体加载状态检查 ===")
        print(f"[DEBUG] 播放状态: {self.media_player.playbackState()}")
        print(f"[DEBUG] 媒体状态: {self.media_player.mediaStatus()}")
        print(f"[DEBUG] 媒体持续时间: {self.media_player.duration()}ms")
        print(f"[DEBUG] 当前位置: {self.media_player.position()}ms")
        print(f"[DEBUG] 是否有错误: {self.media_player.error()}")
        print(f"[DEBUG] 视频输出连接状态: {self.media_player.videoOutput() is not None}")
        print(f"[DEBUG] 音频输出连接状态: {self.media_player.audioOutput() is not None}")
        
        # 如果媒体状态是无效的，尝试其他方法
        if self.media_player.mediaStatus() == QMediaPlayer.MediaStatus.InvalidMedia:
            print(f"[ERROR] 媒体无效，可能是格式不支持")
        elif self.media_player.mediaStatus() == QMediaPlayer.MediaStatus.LoadedMedia:
            print(f"[SUCCESS] 媒体已成功加载")
        elif self.media_player.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia:
            print(f"[ERROR] 没有媒体源")
        
        print(f"[DEBUG] === 状态检查结束 ===")
    
    def toggle_playback(self):
        """切换播放/暂停"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_btn.setText("▶")
        else:
            # 如果没有加载媒体，尝试智能处理
            if not self.current_media:
                main_window = self.get_main_window()
                if main_window:
                    main_window.smart_play_handler()
                    return
            
            self.media_player.play()
            self.play_btn.setText("⏸")
    
    def get_main_window(self):
        """获取主窗口引用"""
        parent = self.parent()
        while parent:
            if isinstance(parent, QMainWindow):
                return parent
            parent = parent.parent()
        return None
    
    def update_position(self, position):
        """更新播放位置"""
        self.position_slider.setValue(position)
        
        # 更新时间显示
        current_time = self.format_time(position)
        total_time = self.format_time(self.media_player.duration())
        self.time_label.setText(f"{current_time} / {total_time}")
        
        # 发出位置改变信号（转换为秒）
        time_seconds = position / 1000.0
        self.positionChanged.emit(time_seconds)
        
        # 同步时间轴播放头
        if self.timeline_widget:
            self.timeline_widget.update_playhead_position(time_seconds)
    
    def update_duration(self, duration):
        """更新总时长"""
        self.position_slider.setRange(0, duration)
    
    def set_position(self, position):
        """设置播放位置"""
        self.media_player.setPosition(position)
    
    def format_time(self, ms):
        """格式化时间显示"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def handle_error(self, error, error_string):
        """处理媒体播放错误"""
        print(f"媒体播放错误: {error} - {error_string}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(
            self,
            "播放错误",
            f"无法播放媒体文件:\n{error_string}\n\n请检查文件格式是否支持。"
        )
    
    def handle_state_change(self, state):
        """处理播放状态变化"""
        state_names = {
            QMediaPlayer.PlaybackState.StoppedState: "已停止",
            QMediaPlayer.PlaybackState.PlayingState: "正在播放",
            QMediaPlayer.PlaybackState.PausedState: "已暂停"
        }
        print(f"播放状态变化: {state_names.get(state, '未知状态')}")
    
    def handle_media_status_change(self, status):
        """处理媒体状态变化"""
        status_names = {
            QMediaPlayer.MediaStatus.NoMedia: "无媒体",
            QMediaPlayer.MediaStatus.LoadingMedia: "正在加载",
            QMediaPlayer.MediaStatus.LoadedMedia: "已加载",
            QMediaPlayer.MediaStatus.StalledMedia: "停滞",
            QMediaPlayer.MediaStatus.BufferingMedia: "缓冲中",
            QMediaPlayer.MediaStatus.BufferedMedia: "已缓冲",
            QMediaPlayer.MediaStatus.EndOfMedia: "播放结束",
            QMediaPlayer.MediaStatus.InvalidMedia: "无效媒体"
        }
        print(f"媒体状态变化: {status_names.get(status, '未知状态')}")
        
        if status == QMediaPlayer.MediaStatus.InvalidMedia:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "媒体错误",
                "无法识别的媒体格式或文件已损坏。\n\n请尝试使用其他媒体文件。"
            )

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EzCut - 专业视频编辑器")
        self.setGeometry(100, 100, 1400, 900)
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()
    
    def setup_ui(self):
        """设置主界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板 (媒体库)
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        self.media_library = MediaLibraryWidget()
        left_layout.addWidget(self.media_library)
        
        main_layout.addWidget(left_panel)
        
        # 中央区域
        center_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 视频预览
        self.video_preview = VideoPreviewWidget()
        center_splitter.addWidget(self.video_preview)
        
        # 时间轴
        timeline_container = QWidget()
        timeline_layout = QVBoxLayout(timeline_container)
        
        timeline_label = QLabel("时间轴")
        timeline_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        timeline_layout.addWidget(timeline_label)
        
        self.timeline = TimelineWidget()
        timeline_layout.addWidget(self.timeline)
        
        # 建立视频预览和时间轴的连接
        self.video_preview.timeline_widget = self.timeline
        
        # 连接视频预览器的播放状态变化信号到工具栏更新
        self.video_preview.media_player.playbackStateChanged.connect(self.update_toolbar_play_button)
        
        center_splitter.addWidget(timeline_container)
        center_splitter.setSizes([400, 300])
        
        main_layout.addWidget(center_splitter)
        
        # 右侧面板 (属性)
        right_panel = QWidget()
        right_panel.setFixedWidth(250)
        right_layout = QVBoxLayout(right_panel)
        
        properties_label = QLabel("属性")
        properties_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(properties_label)
        
        # 属性编辑区域
        self.properties_widget = QTabWidget()
        
        # 剪辑属性
        clip_props = QWidget()
        clip_layout = QFormLayout(clip_props)
        clip_layout.addRow("名称:", QLineEdit())
        clip_layout.addRow("开始时间:", QLineEdit())
        clip_layout.addRow("持续时间:", QLineEdit())
        self.properties_widget.addTab(clip_props, "剪辑")
        
        # 视频属性
        video_props = QWidget()
        video_layout = QFormLayout(video_props)
        video_layout.addRow("亮度:", QSlider(Qt.Orientation.Horizontal))
        video_layout.addRow("对比度:", QSlider(Qt.Orientation.Horizontal))
        video_layout.addRow("饱和度:", QSlider(Qt.Orientation.Horizontal))
        self.properties_widget.addTab(video_props, "视频")
        
        # 音频属性
        audio_props = QWidget()
        audio_layout = QFormLayout(audio_props)
        audio_layout.addRow("音量:", QSlider(Qt.Orientation.Horizontal))
        audio_layout.addRow("平衡:", QSlider(Qt.Orientation.Horizontal))
        self.properties_widget.addTab(audio_props, "音频")
        
        right_layout.addWidget(self.properties_widget)
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel)
    
    def setup_menus(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_action = QAction("新建项目", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开项目", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存项目", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        import_action = QAction("导入媒体", self)
        import_action.triggered.connect(self.media_library.import_media)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("导出视频", self)
        export_action.triggered.connect(self.export_video)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        undo_action = QAction("撤销", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("剪切", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("复制", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        edit_menu.addAction(paste_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        zoom_in_action = QAction("放大", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        view_menu.addAction(zoom_out_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = self.addToolBar("主工具栏")
        
        # 播放控制
        self.play_action = QAction("▶", self)
        self.play_action.setToolTip("播放/暂停")
        self.play_action.triggered.connect(self.toggle_timeline_playback)
        toolbar.addAction(self.play_action)
        
        self.stop_action = QAction("⏹", self)
        self.stop_action.setToolTip("停止")
        self.stop_action.triggered.connect(self.stop_timeline_playback)
        toolbar.addAction(self.stop_action)
        
        toolbar.addSeparator()
        
        # 编辑工具
        cut_tool = QAction("✂", self)
        cut_tool.setToolTip("剪切工具")
        toolbar.addAction(cut_tool)
        
        select_tool = QAction("🔍", self)
        select_tool.setToolTip("选择工具")
        toolbar.addAction(select_tool)
        
        toolbar.addSeparator()
        
        # 缩放控制
        zoom_in_action = QAction("🔍+", self)
        zoom_in_action.setToolTip("放大时间轴")
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("🔍-", self)
        zoom_out_action.setToolTip("缩小时间轴")
        toolbar.addAction(zoom_out_action)
    
    def setup_statusbar(self):
        """设置状态栏"""
        statusbar = self.statusBar()
        statusbar.showMessage("就绪")
        
        # 添加永久状态信息
        self.fps_label = QLabel("FPS: 30")
        statusbar.addPermanentWidget(self.fps_label)
        
        self.resolution_label = QLabel("分辨率: 1920x1080")
        statusbar.addPermanentWidget(self.resolution_label)
    
    def export_video(self):
        """导出视频"""
        if not self.timeline.clips:
            QMessageBox.warning(self, "警告", "时间轴上没有剪辑，无法导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出视频",
            "",
            "MP4文件 (*.mp4);;AVI文件 (*.avi);;所有文件 (*)"
        )
        
        if file_path:
            # 这里应该实现实际的视频导出逻辑
            QMessageBox.information(self, "导出", f"视频将导出到: {file_path}")
    
    def toggle_timeline_playback(self):
        """切换时间轴播放状态"""
        if self.video_preview.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            # 当前正在播放，暂停
            self.video_preview.media_player.pause()
            self.play_action.setText("▶")
            self.play_action.setToolTip("播放")
        else:
            # 当前暂停或停止，开始播放
            if self.video_preview.current_media:
                # 如果有加载的媒体，直接播放
                self.video_preview.media_player.play()
                self.play_action.setText("⏸")
                self.play_action.setToolTip("暂停")
            else:
                # 如果没有加载媒体，智能处理播放请求
                self.smart_play_handler()
    
    def stop_timeline_playback(self):
        """停止时间轴播放"""
        self.video_preview.media_player.stop()
        self.play_action.setText("▶")
        self.play_action.setToolTip("播放")
        
        # 重置播放头到开始位置
        self.timeline.update_playhead_position(0.0)
    
    def smart_play_handler(self):
        """智能播放处理器 - 自动处理媒体加载和播放"""
        print(f"[DEBUG] 智能播放处理器启动")
        
        # 优先级1: 检查时间轴上是否有剪辑
        if self.timeline.clips:
            print(f"[DEBUG] 时间轴上有剪辑，尝试播放")
            self.play_timeline_at_current_position()
            return
        
        # 优先级2: 检查媒体库中是否有媒体文件
        if self.media_library.media_items:
            print(f"[DEBUG] 媒体库中有文件，自动加载第一个文件")
            first_media = self.media_library.media_items[0]
            self.video_preview.load_media(first_media.file_path)
            
            # 延迟播放，等待媒体加载完成
            QTimer.singleShot(500, lambda: self.start_playback_after_load())
            return
        
        # 优先级3: 没有任何媒体，提示用户导入
        result = QMessageBox.question(
            self,
            "导入媒体",
            "还没有导入任何媒体文件。\n\n是否现在导入媒体文件？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # 自动打开导入对话框
            self.media_library.import_media()
    
    def start_playback_after_load(self):
        """媒体加载后开始播放"""
        if self.video_preview.current_media:
            self.video_preview.media_player.play()
            self.play_action.setText("⏸")
            self.play_action.setToolTip("暂停")
            print(f"[DEBUG] 自动播放已开始")
    
    def play_timeline_at_current_position(self):
        """在当前时间轴位置播放剪辑"""
        current_time = self.timeline.get_current_time()
        print(f"[DEBUG] 尝试播放时间轴位置: {current_time:.2f}s")
        print(f"[DEBUG] 时间轴上的剪辑数量: {len(self.timeline.clips)}")
        
        # 查找当前时间位置的剪辑
        active_clip = None
        for i, clip in enumerate(self.timeline.clips):
            clip_start = clip.start_time
            clip_end = clip.start_time + clip.duration
            print(f"[DEBUG] 剪辑 {i}: {clip.media_item.name}, 时间范围: {clip_start:.2f}s - {clip_end:.2f}s")
            
            if clip_start <= current_time <= clip_end:
                active_clip = clip
                print(f"[DEBUG] 找到活动剪辑: {clip.media_item.name}")
                break
        
        if active_clip:
            print(f"[DEBUG] 加载媒体文件: {active_clip.media_item.file_path}")
            # 加载并播放找到的剪辑
            self.video_preview.load_media(active_clip.media_item.file_path)
            
            # 设置播放位置到剪辑内的相对时间
            relative_time = current_time - active_clip.start_time
            position_ms = int(relative_time * 1000)
            print(f"[DEBUG] 设置播放位置: {relative_time:.2f}s ({position_ms}ms)")
            self.video_preview.media_player.setPosition(position_ms)
            
            # 开始播放
            print(f"[DEBUG] 开始播放")
            self.video_preview.media_player.play()
            self.play_action.setText("⏸")
            self.play_action.setToolTip("暂停")
            
            print(f"播放剪辑: {active_clip.media_item.name}，从 {relative_time:.2f}s 开始")
        else:
            print(f"[DEBUG] 在时间轴位置 {current_time:.2f}s 处没有找到剪辑")
            # 如果时间轴上有剪辑但当前位置没有，尝试播放第一个剪辑
            if self.timeline.clips:
                first_clip = self.timeline.clips[0]
                print(f"[DEBUG] 播放第一个剪辑: {first_clip.media_item.name}")
                self.video_preview.load_media(first_clip.media_item.file_path)
                self.video_preview.media_player.setPosition(0)
                self.video_preview.media_player.play()
                self.play_action.setText("⏸")
                self.play_action.setToolTip("暂停")
                # 更新播放头到第一个剪辑的开始位置
                self.timeline.update_playhead_position(first_clip.start_time)
    
    def update_toolbar_play_button(self, state):
        """根据播放状态更新工具栏播放按钮"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_action.setText("⏸")
            self.play_action.setToolTip("暂停")
            # 同步更新视频预览器的播放按钮
            self.video_preview.play_btn.setText("⏸")
        else:
            self.play_action.setText("▶")
            self.play_action.setToolTip("播放")
            # 同步更新视频预览器的播放按钮
            self.video_preview.play_btn.setText("▶")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 EzCut",
            "EzCut - 专业视频编辑器\n\n"
            "基于 PyQt6 开发的现代化视频编辑软件\n"
            "支持多轨道编辑、实时预览、丰富的效果等功能\n\n"
            "版本: 1.0.0"
        )

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("EzCut")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("EzCut Studio")
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()