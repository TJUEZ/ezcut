#!/bin/bash

echo "========================================"
echo "    EzCut - 智能视频剪辑软件"
echo "    (Conda环境版本)"
echo "========================================"
echo

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到conda，请先运行./install.sh进行安装"
    exit 1
fi

# 检查ezcut环境是否存在
if ! conda env list | grep -q ezcut; then
    echo "错误: 未找到ezcut环境，请先运行./install.sh进行安装"
    exit 1
fi

echo "激活conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate ezcut

if [ $? -ne 0 ]; then
    echo "环境激活失败"
    exit 1
fi

# 创建必要目录
mkdir -p temp output fonts

# 启动程序
echo "启动EzCut..."
echo
python main.py

if [ $? -ne 0 ]; then
    echo
    echo "程序运行出错，请检查错误信息"
    echo "如果是依赖问题，请重新运行./install.sh"
fi

echo
echo "程序已退出，conda环境仍保持激活状态"
echo "输入 'conda deactivate' 可退出环境"