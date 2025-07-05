# EzCut - 专业视频编辑器

基于 PyQt6 的专业桌面视频编辑软件，支持多轨道编辑、拖拽操作、实时预览等功能。

## 🚀 快速启动

### 方法一：一键启动（推荐）
```bash
# Windows 用户
双击运行: 启动EzCut.bat

# 或使用 Python 脚本
python start.py
```

### 方法二：直接启动
```bash
python video_editor_qt.py
```

## 📋 系统要求

- Python 3.8+
- PyQt6
- OpenCV
- NumPy
- Pillow

## 🔧 依赖安装

```bash
pip install PyQt6 opencv-python numpy pillow
# 或
pip install -r requirements_qt.txt
```

## 主要功能

### 🎬 视频处理

- **视频加载与预览**: 支持 MP4、AVI、MOV、MKV 等主流视频格式
- **视频剪切**: 精确的时间轴剪切，支持多片段选择
- **视频合并**: 将多个片段按顺序合并为完整视频
- **拖拽操作**: 直观的片段拖拽和重新排序
- **画面控制**: 支持画面放大、缩小、移动等操作

### 📝 字幕功能

- **自动识别**: 基于 OpenAI Whisper 的高精度语音识别
- **字幕编辑**: 实时编辑字幕文本和时间轴
- **样式定制**: 丰富的字幕样式选项（字体、颜色、位置等）
- **自定义字体**: 支持安装和使用自定义字体文件
- **格式支持**: 导入/导出 SRT 字幕文件

### 🎨 界面特性

- **现代化 UI**: 基于 Tkinter 的清爽界面设计
- **实时预览**: 视频播放和字幕同步预览
- **进度显示**: 详细的处理进度和状态提示
- **快捷操作**: 丰富的快捷键和右键菜单

## 技术架构

### 核心技术栈

- **界面框架**: Tkinter (Python 标准库)
- **视频处理**: OpenCV + MoviePy
- **音频识别**: OpenAI Whisper / Faster-Whisper
- **字幕处理**: pysrt
- **图像处理**: PIL/Pillow

### 项目结构

```
ezcut/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
├── config.json            # 配置文件
├── src/                   # 源代码目录
│   ├── video_processor.py # 视频处理模块
│   ├── subtitle_manager.py# 字幕管理模块
│   ├── gui/               # 用户界面模块
│   │   └── main_window.py # 主窗口界面
│   └── utils/             # 工具模块
│       └── config.py      # 配置管理
├── temp/                  # 临时文件目录
├── output/                # 输出文件目录
└── fonts/                 # 自定义字体目录
```

## 安装指南

### 环境要求

- Python 3.8 或更高版本
- Anaconda 或 Miniconda (推荐)
- Windows 10/11, macOS 10.14+, 或 Linux
- 至少 4GB 内存
- 2GB 可用磁盘空间

### 推荐安装方式 (使用 Conda)

**适用于所有平台，提供最佳兼容性**

1. **安装 Anaconda 或 Miniconda**

   - Anaconda: https://www.anaconda.com/products/distribution
   - Miniconda: https://docs.conda.io/en/latest/miniconda.html

2. **克隆项目**

```bash
git clone https://github.com/your-username/ezcut.git
cd ezcut
```

3. **自动安装 (Windows)**

```bash
# 运行安装脚本
install.bat

# 启动程序
run_conda.bat
```

4. **自动安装 (macOS/Linux)**

```bash
# 给脚本执行权限
chmod +x install.sh run_conda.sh

# 运行安装脚本
./install.sh

# 启动程序
./run_conda.sh
```

5. **手动安装**

```bash
# 创建conda环境
conda env create -f environment.yml

# 激活环境
conda activate ezcut

# 运行程序
python main.py
```

### 传统安装方式 (使用 pip)

1. **克隆项目**

```bash
git clone https://github.com/your-username/ezcut.git
cd ezcut
```

2. **创建虚拟环境 (推荐)**

```bash
python -m venv ezcut_env

# Windows
ezcut_env\Scripts\activate

# macOS/Linux
source ezcut_env/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **运行程序**

```bash
python main.py
```

### 依赖说明

**FFmpeg** (自动安装):

- conda 环境会自动安装 FFmpeg
- pip 安装需要手动安装 FFmpeg 并添加到 PATH

**GPU 加速支持** (可选):

```bash
# 在激活的环境中安装
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 使用指南

### 基本工作流程

1. **加载视频**

   - 方式一：点击 `文件` → `打开视频`
   - 方式二：直接从文件管理器拖拽视频文件到媒体库（推荐）
   - 视频将在预览窗口中显示

2. **生成字幕**

   - 点击 `字幕` → `自动识别字幕`
   - 等待 AI 模型处理完成
   - 字幕将显示在右侧编辑面板

3. **编辑字幕**

   - 在字幕列表中选择要编辑的条目
   - 修改文本内容和时间轴
   - 点击 `更新` 保存修改

4. **视频剪辑**

   - 使用时间轴选择要保留的片段
   - 拖拽调整片段顺序
   - 预览剪辑效果

5. **导出结果**
   - 点击 `文件` → `导出视频`
   - 选择输出路径和格式
   - 等待处理完成

### 拖拽功能

本项目支持完整的拖拽操作，让媒体文件管理更加便捷：

- **文件拖拽到媒体库**：从文件管理器直接拖拽媒体文件到媒体库面板
- **媒体库到时间轴**：从媒体库拖拽文件到时间轴进行编辑
- **多文件同时拖拽**：支持批量导入多个文件
- **实时视觉反馈**：拖拽过程中提供界面提示和状态反馈

详细的拖拽功能使用方法请参考：[拖拽功能使用指南](DRAG_DROP_GUIDE.md)

### 高级功能

**字幕样式定制**:

- 字体选择和大小调整
- 颜色和背景设置
- 位置和对齐方式
- 描边和阴影效果

**自定义字体安装**:

- 点击 `字幕` → `安装字体`
- 选择 TTF 或 OTF 字体文件
- 字体将自动添加到可用列表

**批量处理**:

- 支持多个视频文件的批量字幕生成
- 批量应用相同的剪辑规则
- 自动化的输出文件命名

## 参考项目

本项目在开发过程中参考了以下优秀的开源项目：

### AutoCut

- **项目地址**: https://github.com/mli/autocut
- **参考内容**:
  - Whisper 模型的加载和使用方法
  - 视频音频提取和处理流程
  - SRT 字幕文件的生成和解析
  - 视频剪切和合并的实现思路
- **致谢**: 感谢 AutoCut 项目提供的字幕识别和视频处理的优秀实现方案

### Tailor

- **项目地址**: https://github.com/FutureUniant/Tailor
- **参考内容**:
  - 视频处理的整体架构设计
  - 用户界面的布局和交互设计
  - 视频优化和处理算法的思路
  - 多媒体文件的处理方式
- **致谢**: 感谢 Tailor 项目在视频编辑软件设计方面的启发

### iVideo

- **项目地址**: https://github.com/icodebase/ivideo <mcreference link="https://github.com/icodebase/ivideo" index="0">0</mcreference>
- **参考内容**:
  - 视频拖拽到媒体库的实现思路
  - 媒体库到时间轴的拖拽操作设计
  - Tkinter 拖拽事件处理机制
  - 视频编辑软件的用户交互设计
- **借鉴实现**:
  - **跨平台拖拽支持**: 使用`tkinterdnd2`库实现跨平台文件拖拽功能
  - **多文件拖拽**: 支持同时拖拽多个媒体文件到媒体库
  - **拖拽视觉反馈**: 实现拖拽进入、移动、离开时的界面反馈
  - **文件格式验证**: 在拖拽时验证文件类型和格式支持
  - **时间轴拖拽**: 从媒体库拖拽文件到时间轴的交互设计
- **核心技术实现**:

  ```python
  # 媒体库拖拽支持 (借鉴iVideo项目架构)
  def setup_drag_drop(self):
      import tkinterdnd2 as tkdnd
      # 注册拖拽目标
      self.media_canvas.drop_target_register(tkdnd.DND_FILES)
      # 绑定拖拽事件
      self.media_canvas.dnd_bind('<<DropEnter>>', self.on_drag_enter)
      self.media_canvas.dnd_bind('<<DropPosition>>', self.on_drag_motion)
      self.media_canvas.dnd_bind('<<DropLeave>>', self.on_drag_leave)
      self.media_canvas.dnd_bind('<<Drop>>', self.on_drop)

  def on_drag_enter(self, event):
      # 拖拽进入时的视觉反馈
      self.media_canvas.configure(bg='lightblue')
      return 'copy'

  def on_drop(self, event):
      # 处理拖拽文件
      files = event.data.split() if hasattr(event.data, 'split') else [event.data]
      for file_path in files:
          if self.validate_media_file(file_path):
              self.add_media_file(file_path)

  # 时间轴拖拽支持
  def setup_timeline_drag_drop(self):
      self.timeline_canvas.drop_target_register(tkdnd.DND_FILES)
      self.timeline_canvas.dnd_bind('<<Drop>>', self.on_timeline_drop)

  def on_timeline_drop(self, event):
      # 计算拖拽位置和轨道
      x, y = self.timeline_canvas.canvasx(event.x), self.timeline_canvas.canvasy(event.y)
      track_index = self.get_track_at_position(y)
      time_position = self.pixel_to_time(x)
      self.add_clip_to_timeline(event.data, track_index, time_position)
  ```

- **拖拽功能特性**:
  - 支持从文件管理器直接拖拽文件到媒体库
  - 支持媒体库内文件拖拽到时间轴
  - 拖拽过程中提供实时预览和位置指示
  - 自动检测拖拽目标区域和有效性
  - 支持多种媒体格式的拖拽导入
- **致谢**: 感谢 iVideo 项目在视频拖拽操作实现方面的参考价值

### Tkinter 拖拽技术参考

- **技术文档**: Python 官方 Tkinter.dnd 模块文档
- **参考内容**:
  - Tkinter 原生拖拽支持的使用方法
  - 拖拽事件的生命周期管理
  - 跨组件拖拽的实现技巧
  - 拖拽数据的序列化和传输
- **实现要点**:
  - 使用`tkinter.dnd`模块提供的拖拽框架
  - 实现`dnd_accept`、`dnd_enter`、`dnd_leave`、`dnd_commit`方法
  - 处理拖拽过程中的鼠标事件和位置计算
  - 提供拖拽过程中的用户界面反馈

## 开发计划

### 近期计划 (v1.1)

- [ ] 视频片段管理器界面
- [ ] 字幕样式编辑器
- [ ] 更多视频格式支持
- [ ] 性能优化和内存管理

### 中期计划 (v1.2)

- [ ] 视频特效和滤镜
- [ ] 音频处理和混音
- [ ] 多语言界面支持
- [ ] 插件系统架构

### 长期计划 (v2.0)

- [ ] 基于深度学习的智能剪辑
- [ ] 云端处理和协作功能
- [ ] 移动端应用开发
- [ ] 商业版本功能扩展

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目！

### 开发环境设置

1. Fork 本项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 添加适当的注释和文档字符串
- 编写单元测试覆盖新功能
- 确保代码通过现有测试

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页: https://github.com/your-username/ezcut
- 问题反馈: https://github.com/your-username/ezcut/issues
- 邮箱: your-email@example.com

## 致谢

特别感谢以下项目和技术：

- [OpenAI Whisper](https://github.com/openai/whisper) - 强大的语音识别模型
- [MoviePy](https://github.com/Zulko/moviepy) - 优秀的视频处理库
- [OpenCV](https://opencv.org/) - 计算机视觉处理库
- AutoCut 和 Tailor 项目的开源贡献

---

**EzCut** - 让视频剪辑变得简单高效！ 🎬✨
