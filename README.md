# EzCut - 智能视频剪辑软件

一个基于Python开发的智能视频剪辑软件，具备自动字幕识别、字幕样式编辑、视频剪切拖拽等功能。

## 主要功能

### 🎬 视频处理
- **视频加载与预览**: 支持MP4、AVI、MOV、MKV等主流视频格式
- **视频剪切**: 精确的时间轴剪切，支持多片段选择
- **视频合并**: 将多个片段按顺序合并为完整视频
- **拖拽操作**: 直观的片段拖拽和重新排序
- **画面控制**: 支持画面放大、缩小、移动等操作

### 📝 字幕功能
- **自动识别**: 基于OpenAI Whisper的高精度语音识别
- **字幕编辑**: 实时编辑字幕文本和时间轴
- **样式定制**: 丰富的字幕样式选项（字体、颜色、位置等）
- **自定义字体**: 支持安装和使用自定义字体文件
- **格式支持**: 导入/导出SRT字幕文件

### 🎨 界面特性
- **现代化UI**: 基于Tkinter的清爽界面设计
- **实时预览**: 视频播放和字幕同步预览
- **进度显示**: 详细的处理进度和状态提示
- **快捷操作**: 丰富的快捷键和右键菜单

## 技术架构

### 核心技术栈
- **界面框架**: Tkinter (Python标准库)
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

### 推荐安装方式 (使用Conda)

**适用于所有平台，提供最佳兼容性**

1. **安装Anaconda或Miniconda**
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

### 传统安装方式 (使用pip)

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
- conda环境会自动安装FFmpeg
- pip安装需要手动安装FFmpeg并添加到PATH

**GPU加速支持** (可选):
```bash
# 在激活的环境中安装
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 使用指南

### 基本工作流程

1. **加载视频**
   - 点击 `文件` → `打开视频`
   - 选择要编辑的视频文件
   - 视频将在预览窗口中显示

2. **生成字幕**
   - 点击 `字幕` → `自动识别字幕`
   - 等待AI模型处理完成
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

### 高级功能

**字幕样式定制**:
- 字体选择和大小调整
- 颜色和背景设置
- 位置和对齐方式
- 描边和阴影效果

**自定义字体安装**:
- 点击 `字幕` → `安装字体`
- 选择TTF或OTF字体文件
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
  - Whisper模型的加载和使用方法
  - 视频音频提取和处理流程
  - SRT字幕文件的生成和解析
  - 视频剪切和合并的实现思路
- **致谢**: 感谢AutoCut项目提供的字幕识别和视频处理的优秀实现方案

### Tailor
- **项目地址**: https://github.com/FutureUniant/Tailor
- **参考内容**:
  - 视频处理的整体架构设计
  - 用户界面的布局和交互设计
  - 视频优化和处理算法的思路
  - 多媒体文件的处理方式
- **致谢**: 感谢Tailor项目在视频编辑软件设计方面的启发

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

欢迎提交Issue和Pull Request来帮助改进项目！

### 开发环境设置
1. Fork本项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建Pull Request

### 代码规范
- 遵循PEP 8 Python代码规范
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
- AutoCut和Tailor项目的开源贡献

---

**EzCut** - 让视频剪辑变得简单高效！ 🎬✨
