#!/bin/bash

echo "HylReg-RAG 环境设置脚本"
echo "========================"

# 检查是否安装了uv
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到 uv。请先安装uv:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  或者使用 Homebrew: brew install uv"
    exit 1
fi

echo "找到 uv 版本: $(uv --version)"

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "检测到 Python 版本: $PYTHON_VERSION"

# 检查Python版本是否满足要求
if [[ $(printf '%s\n' "3.12" "$PYTHON_VERSION" | sort -V | head -n1) != "3.12" ]]; then
    echo "警告: 推荐使用 Python 3.12 或更高版本"
fi

# 检查是否有虚拟环境
if [[ ! -d ".venv" ]]; then
    echo "创建虚拟环境..."
    uv venv
fi

echo "激活虚拟环境..."
source .venv/bin/activate

echo "安装项目依赖..."
uv pip sync requirements.txt
echo "安装开发依赖..."
uv pip install -e ".[dev]"

echo "检查依赖安装情况..."
pip list

echo ""
echo "环境设置完成!"
echo "使用以下命令运行项目:"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo ""
echo "或者直接运行:"
echo "  .venv/bin/python main.py"
