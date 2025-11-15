#!/bin/bash
# 快速设置虚拟环境脚本

echo "=========================================="
echo "AlphaChain - 环境设置脚本"
echo "=========================================="

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "项目目录: $SCRIPT_DIR"

# 检查是否已存在虚拟环境
if [ -d "venv" ]; then
    echo "⚠ 虚拟环境已存在"
    read -p "是否重新创建？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除旧虚拟环境..."
        rm -rf venv
    else
        echo "使用现有虚拟环境"
        echo ""
        echo "激活虚拟环境:"
        echo "  source venv/bin/activate"
        exit 0
    fi
fi

# 检查python3是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    echo "请先安装 Python 3"
    exit 1
fi

echo ""
echo "创建虚拟环境..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ 创建虚拟环境失败"
    echo "可能需要安装 python3-venv:"
    echo "  sudo apt-get install python3-venv"
    exit 1
fi

echo "✓ 虚拟环境创建成功"

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo ""
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "安装项目依赖..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 环境设置完成！"
    echo "=========================================="
    echo ""
    echo "下次使用时，请先激活虚拟环境："
    echo "  source venv/bin/activate"
    echo ""
    echo "然后运行测试："
    echo "  python -m src.data_sources.test_data_sources --source defillama"
    echo ""
    echo "退出虚拟环境："
    echo "  deactivate"
    echo ""
else
    echo ""
    echo "❌ 依赖安装失败"
    echo "请检查 requirements.txt 文件"
    exit 1
fi

