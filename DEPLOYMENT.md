# EzCut 部署指南

本文档详细说明了如何在不同环境和平台上部署EzCut智能视频剪辑软件。

## 目录

- [快速开始](#快速开始)
- [环境要求](#环境要求)
- [部署方式](#部署方式)
- [平台特定说明](#平台特定说明)
- [故障排除](#故障排除)
- [性能优化](#性能优化)

## 快速开始

### 方式一：自动安装（推荐）

**Windows用户：**
```bash
# 1. 下载项目
git clone https://github.com/your-username/ezcut.git
cd ezcut

# 2. 运行安装脚本
install.bat

# 3. 启动程序
run_conda.bat
```

**macOS/Linux用户：**
```bash
# 1. 下载项目
git clone https://github.com/your-username/ezcut.git
cd ezcut

# 2. 给脚本执行权限
chmod +x install.sh run_conda.sh

# 3. 运行安装脚本
./install.sh

# 4. 启动程序
./run_conda.sh
```

### 方式二：环境检查

如果遇到问题，可以运行环境检查脚本：
```bash
python check_environment.py
```

## 环境要求

### 基础要求

| 组件 | 最低版本 | 推荐版本 | 说明 |
|------|----------|----------|------|
| Python | 3.8 | 3.9+ | 核心运行环境 |
| 内存 | 4GB | 8GB+ | 视频处理需要较多内存 |
| 存储 | 2GB | 5GB+ | 包含模型和临时文件 |
| 显卡 | 无要求 | NVIDIA GPU | GPU加速可提升性能 |

### 依赖包要求

**必需依赖：**
- opencv-python >= 4.5.0
- numpy >= 1.20.0
- Pillow >= 8.0.0
- tkinter (Python内置)
- tqdm >= 4.60.0
- requests >= 2.25.0

**可选依赖：**
- moviepy >= 1.0.3 (高级视频处理)
- openai-whisper >= 20230314 (AI字幕识别)
- faster-whisper >= 0.9.0 (更快的字幕识别)
- pysrt >= 1.1.2 (字幕文件处理)

## 部署方式

### 1. Conda环境部署（推荐）

**优势：**
- 最佳兼容性
- 自动依赖管理
- 跨平台支持
- 环境隔离

**步骤：**

1. **安装Anaconda/Miniconda**
   ```bash
   # 下载并安装Anaconda
   # Windows: https://www.anaconda.com/products/distribution
   # macOS: brew install --cask anaconda
   # Linux: wget https://repo.anaconda.com/archive/Anaconda3-latest-Linux-x86_64.sh
   ```

2. **创建专用环境**
   ```bash
   # 使用environment.yml创建环境
   conda env create -f environment.yml
   
   # 或手动创建
   conda create -n ezcut python=3.9 -y
   conda activate ezcut
   conda install -c conda-forge opencv numpy pillow tqdm requests -y
   pip install moviepy pysrt whisper faster-whisper
   ```

3. **激活和使用**
   ```bash
   conda activate ezcut
   python main.py
   ```

### 2. 虚拟环境部署

**适用场景：**
- 不想安装Conda
- 系统资源有限
- 简单部署需求

**步骤：**

1. **创建虚拟环境**
   ```bash
   # Windows
   python -m venv ezcut_env
   ezcut_env\Scripts\activate
   
   # macOS/Linux
   python3 -m venv ezcut_env
   source ezcut_env/bin/activate
   ```

2. **安装依赖**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **安装FFmpeg**
   ```bash
   # Windows (使用Scoop)
   scoop install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg
   
   # CentOS/RHEL
   sudo yum install epel-release
   sudo yum install ffmpeg
   ```

### 3. Docker部署

**创建Dockerfile：**
```dockerfile
FROM continuumio/miniconda3:latest

WORKDIR /app

# 复制环境文件
COPY environment.yml .

# 创建conda环境
RUN conda env create -f environment.yml

# 激活环境
SHELL ["conda", "run", "-n", "ezcut", "/bin/bash", "-c"]

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p temp output fonts

# 设置入口点
ENTRYPOINT ["conda", "run", "-n", "ezcut", "python", "main.py"]
```

**构建和运行：**
```bash
# 构建镜像
docker build -t ezcut .

# 运行容器
docker run -it --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  ezcut
```

## 平台特定说明

### Windows

**系统要求：**
- Windows 10 1903+ 或 Windows 11
- Visual C++ Redistributable 2019+

**常见问题：**
1. **编码问题**
   ```batch
   # 在批处理文件开头添加
   chcp 65001
   ```

2. **路径问题**
   ```batch
   # 使用绝对路径
   set PYTHON_PATH=C:\Python39\python.exe
   ```

3. **权限问题**
   ```batch
   # 以管理员身份运行命令提示符
   ```

### macOS

**系统要求：**
- macOS 10.14 (Mojave) 或更高版本
- Xcode Command Line Tools

**安装Command Line Tools：**
```bash
xcode-select --install
```

**使用Homebrew管理依赖：**
```bash
# 安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Python和FFmpeg
brew install python@3.9 ffmpeg
```

### Linux

**Ubuntu/Debian：**
```bash
# 更新包列表
sudo apt update

# 安装Python和依赖
sudo apt install python3.9 python3.9-venv python3.9-dev
sudo apt install ffmpeg libopencv-dev

# 安装pip
curl https://bootstrap.pypa.io/get-pip.py | python3.9
```

**CentOS/RHEL：**
```bash
# 启用EPEL仓库
sudo yum install epel-release

# 安装Python和依赖
sudo yum install python39 python39-devel
sudo yum install ffmpeg opencv-devel
```

**Arch Linux：**
```bash
# 安装依赖
sudo pacman -S python python-pip ffmpeg opencv
```

## 故障排除

### 常见错误及解决方案

#### 1. ModuleNotFoundError

**错误信息：**
```
ModuleNotFoundError: No module named 'cv2'
```

**解决方案：**
```bash
# 检查环境
python check_environment.py

# 重新安装依赖
pip install opencv-python

# 或使用conda
conda install -c conda-forge opencv
```

#### 2. FFmpeg not found

**错误信息：**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**解决方案：**
```bash
# 检查FFmpeg安装
ffmpeg -version

# 如果未安装，根据平台安装
# Windows: scoop install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

#### 3. 内存不足

**错误信息：**
```
MemoryError: Unable to allocate array
```

**解决方案：**
1. 减少视频分辨率
2. 分段处理长视频
3. 增加虚拟内存
4. 使用更强的硬件

#### 4. 权限错误

**错误信息：**
```
PermissionError: [Errno 13] Permission denied
```

**解决方案：**
```bash
# 检查文件权限
ls -la

# 修改权限
chmod 755 install.sh run_conda.sh

# 或使用sudo（谨慎）
sudo python main.py
```

### 性能问题

#### 1. 视频处理慢

**优化方案：**
- 启用GPU加速
- 降低视频分辨率
- 使用faster-whisper替代whisper
- 增加内存和CPU核心数

#### 2. 字幕识别慢

**优化方案：**
```bash
# 安装GPU版本的PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# 使用更快的模型
# 在代码中设置model="base"而不是"large"
```

## 性能优化

### 硬件优化

1. **CPU优化**
   - 使用多核CPU
   - 启用超线程
   - 设置CPU亲和性

2. **内存优化**
   - 至少8GB RAM
   - 启用虚拟内存
   - 使用SSD存储

3. **GPU加速**
   ```bash
   # 安装CUDA支持
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   
   # 验证GPU可用性
   python -c "import torch; print(torch.cuda.is_available())"
   ```

### 软件优化

1. **模型选择**
   ```python
   # 使用更小的Whisper模型
   model = whisper.load_model("base")  # 而不是"large"
   
   # 使用faster-whisper
   from faster_whisper import WhisperModel
   model = WhisperModel("base", device="cuda")
   ```

2. **批处理优化**
   ```python
   # 批量处理多个文件
   for video_file in video_files:
       process_video(video_file)
   ```

3. **缓存优化**
   ```python
   # 启用模型缓存
   os.environ['TRANSFORMERS_CACHE'] = './cache'
   ```

### 监控和调试

1. **性能监控**
   ```bash
   # 监控资源使用
   htop  # Linux/macOS
   # 或任务管理器 (Windows)
   ```

2. **日志记录**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

3. **性能分析**
   ```bash
   # 使用cProfile分析性能
   python -m cProfile -o profile.stats main.py
   ```

## 生产环境部署

### 服务器部署

1. **系统服务**
   ```bash
   # 创建systemd服务文件
   sudo nano /etc/systemd/system/ezcut.service
   ```

2. **负载均衡**
   - 使用Nginx反向代理
   - 配置多个工作进程
   - 实现故障转移

3. **监控告警**
   - 配置Prometheus监控
   - 设置Grafana仪表板
   - 配置告警规则

### 安全考虑

1. **文件权限**
   ```bash
   # 设置适当的文件权限
   chmod 644 *.py
   chmod 755 *.sh
   ```

2. **网络安全**
   - 配置防火墙规则
   - 使用HTTPS
   - 限制访问IP

3. **数据保护**
   - 定期备份
   - 加密敏感数据
   - 实现访问控制

---

如有问题，请查看[故障排除](#故障排除)部分或提交Issue。