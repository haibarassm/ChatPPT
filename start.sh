#!/bin/bash

# ChatPPT 启动脚本

echo "🚀 启动 ChatPPT..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python -m venv .venv"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，请先配置API密钥"
    echo "💡 复制.env.example到.env并填入你的API密钥"
    exit 1
fi

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 启动应用
echo "🎯 启动Gradio应用..."
python src/app.py
