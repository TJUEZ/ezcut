#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI主题管理器 - 支持DPI适配和现代化界面
"""

import tkinter as tk
from tkinter import ttk
import sys
import platform
from typing import Dict, Any, Tuple
from pathlib import Path

class ThemeManager:
    """主题管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ui_config = config.get('ui', {})
        self.dpi_scale = 1.0
        self.font_scale = self.ui_config.get('font_scale', 1.0)
        
        # 检测DPI缩放
        self._detect_dpi_scale()
        
        # 现代化主题配置
        self.modern_colors = {
            'primary': self.ui_config.get('accent_color', '#0078d4'),
            'background': '#ffffff' if not self.ui_config.get('dark_mode', False) else '#2d2d2d',
            'surface': '#f8f9fa' if not self.ui_config.get('dark_mode', False) else '#3d3d3d',
            'text': '#212529' if not self.ui_config.get('dark_mode', False) else '#ffffff',
            'text_secondary': '#6c757d' if not self.ui_config.get('dark_mode', False) else '#adb5bd',
            'border': '#dee2e6' if not self.ui_config.get('dark_mode', False) else '#495057',
            'hover': '#e9ecef' if not self.ui_config.get('dark_mode', False) else '#495057',
            'active': '#007bff' if not self.ui_config.get('dark_mode', False) else '#0d6efd',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8'
        }
        
        # 字体配置
        self.fonts = self._setup_fonts()
        
    def _detect_dpi_scale(self):
        """检测DPI缩放比例"""
        try:
            if platform.system() == 'Windows':
                import ctypes
                # 获取系统DPI
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                dc = user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
                user32.ReleaseDC(0, dc)
                
                # 计算缩放比例 (96 DPI = 100%)
                self.dpi_scale = dpi / 96.0
                
                # 应用用户设置的缩放
                ui_scale = self.ui_config.get('ui_scale', 'auto')
                if ui_scale != 'auto':
                    try:
                        self.dpi_scale = float(ui_scale)
                    except (ValueError, TypeError):
                        pass
                        
            elif platform.system() == 'Darwin':  # macOS
                # macOS通常自动处理DPI
                self.dpi_scale = 1.0
            else:  # Linux
                # 尝试从环境变量获取
                import os
                scale = os.environ.get('GDK_SCALE', '1.0')
                try:
                    self.dpi_scale = float(scale)
                except (ValueError, TypeError):
                    self.dpi_scale = 1.0
                    
        except Exception:
            self.dpi_scale = 1.0
            
        # 限制缩放范围
        self.dpi_scale = max(0.5, min(3.0, self.dpi_scale))
        
    def _setup_fonts(self) -> Dict[str, tuple]:
        """设置字体配置"""
        base_size = int(9 * self.dpi_scale * self.font_scale)
        
        # 根据系统选择合适的字体
        if platform.system() == 'Windows':
            default_font = 'Microsoft YaHei UI'
            mono_font = 'Consolas'
        elif platform.system() == 'Darwin':
            default_font = 'SF Pro Display'
            mono_font = 'SF Mono'
        else:
            default_font = 'Ubuntu'
            mono_font = 'Ubuntu Mono'
            
        return {
            'default': (default_font, base_size),
            'small': (default_font, max(8, base_size - 1)),
            'large': (default_font, base_size + 2),
            'title': (default_font, base_size + 4, 'bold'),
            'subtitle': (default_font, base_size + 1, 'bold'),
            'mono': (mono_font, base_size),
            'button': (default_font, base_size),
            'menu': (default_font, base_size)
        }
        
    def scale_size(self, size: int) -> int:
        """根据DPI缩放尺寸"""
        return int(size * self.dpi_scale)
        
    def get_font(self, font_type: str = 'default') -> tuple:
        """获取字体配置"""
        return self.fonts.get(font_type, self.fonts['default'])
        
    def apply_theme(self, root: tk.Tk):
        """应用主题到根窗口"""
        # 设置DPI感知
        if self.ui_config.get('dpi_awareness', True) and platform.system() == 'Windows':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
                
        # 配置ttk样式
        style = ttk.Style()
        
        if self.ui_config.get('modern_theme', True):
            self._apply_modern_theme(style)
        else:
            style.theme_use('clam')
            
        # 设置根窗口属性
        root.configure(bg=self.modern_colors['background'])
        
        # 设置默认字体
        root.option_add('*Font', self.get_font('default'))
        
    def _apply_modern_theme(self, style: ttk.Style):
        """应用现代化主题"""
        style.theme_use('clam')
        
        colors = self.modern_colors
        padding = self.scale_size(self.ui_config.get('button_padding', 8))
        
        # 配置各种控件样式
        style.configure('TFrame', 
                       background=colors['background'],
                       relief='flat')
                       
        style.configure('TLabel',
                       background=colors['background'],
                       foreground=colors['text'],
                       font=self.get_font('default'))
                       
        style.configure('Title.TLabel',
                       background=colors['background'],
                       foreground=colors['text'],
                       font=self.get_font('title'))
                       
        style.configure('Subtitle.TLabel',
                       background=colors['background'],
                       foreground=colors['text_secondary'],
                       font=self.get_font('subtitle'))
                       
        # 按钮样式
        style.configure('TButton',
                       background=colors['surface'],
                       foreground=colors['text'],
                       borderwidth=1,
                       relief='solid',
                       padding=(padding, padding//2),
                       font=self.get_font('button'))
                       
        style.map('TButton',
                 background=[('active', colors['hover']),
                           ('pressed', colors['active'])],
                 relief=[('pressed', 'sunken')])
                 
        # 主要按钮样式
        style.configure('Primary.TButton',
                       background=colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       padding=(padding, padding//2))
                       
        style.map('Primary.TButton',
                 background=[('active', colors['active']),
                           ('pressed', colors['active'])])
                           
        # 输入框样式
        style.configure('TEntry',
                       fieldbackground=colors['surface'],
                       foreground=colors['text'],
                       borderwidth=1,
                       relief='solid',
                       padding=(padding//2, padding//4))
                       
        # 树形视图样式
        style.configure('Treeview',
                       background=colors['surface'],
                       foreground=colors['text'],
                       fieldbackground=colors['surface'],
                       borderwidth=1,
                       relief='solid')
                       
        style.configure('Treeview.Heading',
                       background=colors['background'],
                       foreground=colors['text'],
                       relief='flat',
                       font=self.get_font('subtitle'))
                       
        # 笔记本标签样式
        style.configure('TNotebook',
                       background=colors['background'],
                       borderwidth=0)
                       
        style.configure('TNotebook.Tab',
                       background=colors['surface'],
                       foreground=colors['text'],
                       padding=(padding, padding//2),
                       borderwidth=1,
                       relief='solid')
                       
        style.map('TNotebook.Tab',
                 background=[('selected', colors['background']),
                           ('active', colors['hover'])])
                           
        # 进度条样式
        style.configure('TProgressbar',
                       background=colors['primary'],
                       troughcolor=colors['surface'],
                       borderwidth=0,
                       lightcolor=colors['primary'],
                       darkcolor=colors['primary'])
                       
        # 分隔器样式
        style.configure('TPanedwindow',
                       background=colors['background'])
                       
        style.configure('Sash',
                       background=colors['border'],
                       relief='flat',
                       sashwidth=self.scale_size(3))
                       
    def create_modern_button(self, parent, text: str, command=None, style='TButton', **kwargs) -> ttk.Button:
        """创建现代化按钮"""
        return ttk.Button(parent, text=text, command=command, style=style, **kwargs)
        
    def create_icon_button(self, parent, icon: str, command=None, tooltip: str = None) -> ttk.Button:
        """创建图标按钮"""
        btn = ttk.Button(parent, text=icon, command=command, width=3)
        if tooltip:
            self._create_tooltip(btn, tooltip)
        return btn
        
    def _create_tooltip(self, widget, text: str):
        """创建工具提示"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text,
                           background=self.modern_colors['surface'],
                           foreground=self.modern_colors['text'],
                           relief='solid', borderwidth=1,
                           font=self.get_font('small'),
                           padx=5, pady=2)
            label.pack()
            
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        
    def get_spacing(self) -> int:
        """获取界面间距"""
        return self.scale_size(self.ui_config.get('panel_spacing', 5))
        
    def get_padding(self) -> int:
        """获取控件内边距"""
        return self.scale_size(self.ui_config.get('button_padding', 8))
        
    def get_color(self, color_name: str) -> str:
        """获取主题颜色"""
        return self.modern_colors.get(color_name, '#000000')
        
    def update_dpi_scale(self, scale: float):
        """更新DPI缩放"""
        self.dpi_scale = max(0.5, min(3.0, scale))
        self.fonts = self._setup_fonts()