#!/bin/bash

echo "========================================"
echo "    EzCut 安装脚本 (macOS/Linux)"
echo "========================================"
echo

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到conda，请先安装Anaconda或Miniconda"
    echo "下载地址: https://www.anaconda.com/products/distribution"
    exit 1
fi

echo "检测到conda环境管理器"
echo

# 检查是否已存在ezcut环境
if conda env list | grep -q ezcut; then
    echo "检测到已存在的ezcut环境"
    read -p "是否删除并重新创建? (y/N): " choice
    if [[ $choice =~ ^[Yy]$ ]]; then
        echo "删除现有环境..."
        conda env remove -n ezcut -y
    else
        echo "使用现有环境"
        conda activate ezcut
        exit 0
    fi
fi

# 创建conda环境
echo "创建conda虚拟环境..."
if conda env create -f environment.yml; then
    echo "环境创建成功"
else
    echo "环境创建失败，尝试手动创建..."
    conda create -n ezcut python=3.9 -y
    conda activate ezcut
    conda install -c conda-forge opencv numpy pillow tqdm requests -y
    pip install moviepy pysrt whisper faster-whisper
fi

# 激活环境
echo
echo "激活conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate ezcut

# 验证安装
echo "验证安装..."
if python -c "import cv2, numpy, PIL, moviepy; print('所有依赖包安装成功!')"; then
    echo "依赖验证成功"
else
    echo "警告: 部分依赖包可能未正确安装"
fi

# 创建必要目录
mkdir -p temp output fonts

echo
echo "========================================"
echo "安装完成！"
echo
echo "使用方法:"
echo "1. 运行 'conda activate ezcut' 激活环境"
echo "2. 运行 'python main.py' 启动程序"
echo "或者直接运行 './run_conda.sh'"
echo "========================================"