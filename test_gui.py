#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的GUI测试脚本
用于验证Tkinter和主要依赖是否正常工作
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

def test_gui():
    """测试GUI功能"""
    root = tk.Tk()
    root.title("EzCut GUI 测试")
    root.geometry("400x300")
    
    # 设置UTF-8编码
    if sys.platform.startswith('win'):
        root.option_add('*Font', 'SimSun 9')
    
    # 创建测试界面
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = ttk.Label(frame, text="EzCut 专业视频编辑软件", font=('Arial', 16, 'bold'))
    title_label.pack(pady=10)
    
    # 测试信息
    info_text = """GUI测试成功！
    
✓ Tkinter 正常工作
✓ 中文显示正常
✓ 窗口创建成功
✓ 控件布局正常
    
现在可以启动完整的EzCut程序了！"""
    
    info_label = ttk.Label(frame, text=info_text, justify=tk.CENTER)
    info_label.pack(pady=20)
    
    # 按钮
    def show_success():
        messagebox.showinfo("成功", "GUI测试通过！EzCut可以正常运行。")
    
    def close_app():
        root.destroy()
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="测试消息框", command=show_success).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="关闭", command=close_app).pack(side=tk.LEFT, padx=5)
    
    # 状态栏
    status_frame = ttk.Frame(root)
    status_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    status_label = ttk.Label(status_frame, text="状态：GUI测试运行中...")
    status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    print("GUI测试窗口已启动")
    print("如果看到窗口，说明GUI功能正常")
    print("关闭窗口或点击关闭按钮退出测试")
    
    root.mainloop()
    print("GUI测试完成")

if __name__ == "__main__":
    try:
        print("开始GUI测试...")
        test_gui()
    except Exception as e:
        print(f"GUI测试失败: {e}")
        input("按回车键退出...")