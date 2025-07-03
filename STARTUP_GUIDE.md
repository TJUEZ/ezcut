# EzCut 启动指南

## 启动方式

### 1. 推荐方式：使用简化启动脚本
```bash
run_simple.bat
```
- 最简单可靠的启动方式
- 跳过复杂的环境检查
- 直接启动程序

### 2. 完整检查启动脚本
```bash
run_conda.bat
```
- 包含完整的环境检查
- 提供详细的错误诊断
- 适合首次运行或故障排除

### 3. 直接启动（推荐用于开发）
```bash
conda activate ezcut
python main.py
```
- 最直接的启动方式
- 便于查看详细输出
- 适合开发和调试

## 常见问题解决

### 问题1：bat脚本无法启动
**症状**：双击bat文件后程序没有启动

**解决方案**：
1. 使用 `run_simple.bat` 替代 `run_conda.bat`
2. 检查conda环境是否正确安装：`conda info --envs`
3. 手动激活环境后启动：
   ```bash
   conda activate ezcut
   python main.py
   ```

### 问题2：GUI没有显示
**症状**：程序启动但看不到界面

**解决方案**：
1. 检查任务栏是否有EzCut窗口
2. 使用Alt+Tab切换窗口
3. 检查是否有多个显示器，窗口可能在其他屏幕上
4. 重启程序

### 问题3：环境检查失败
**症状**：提示ezcut环境未找到

**解决方案**：
1. 运行 `install.bat` 重新安装环境
2. 检查conda是否正确安装
3. 手动创建环境：
   ```bash
   conda env create -f environment.yml
   ```

### 问题4：依赖包缺失
**症状**：ImportError或ModuleNotFoundError

**解决方案**：
1. 运行环境检查：`python check_environment.py`
2. 重新安装依赖：
   ```bash
   conda activate ezcut
   pip install -r requirements.txt
   ```
3. 使用conda安装：
   ```bash
   conda activate ezcut
   conda install --file requirements.txt
   ```

## 调试工具

### 1. 环境检查脚本
```bash
python check_environment.py
```
检查Python版本、依赖包安装状态

### 2. 调试启动脚本
```bash
debug_start.bat
```
逐步检查启动过程，定位问题

### 3. 简单测试脚本
```bash
simple_test.bat
```
测试基本的conda环境和Python运行

## 建议的启动流程

1. **首次使用**：
   - 运行 `install.bat` 安装环境
   - 使用 `run_conda.bat` 进行完整检查
   - 如果成功，后续可使用 `run_simple.bat`

2. **日常使用**：
   - 直接使用 `run_simple.bat`
   - 如果有问题，切换到 `run_conda.bat`

3. **开发调试**：
   - 使用命令行直接启动：`conda activate ezcut && python main.py`
   - 可以看到详细的输出和错误信息

## 技术说明

- `conda run -n ezcut` 比 `conda activate` 在批处理文件中更可靠
- GUI程序启动后可能没有控制台输出，这是正常现象
- 如果程序正在运行但看不到界面，检查任务管理器中的Python进程
- 某些杀毒软件可能会阻止GUI程序启动，请添加信任