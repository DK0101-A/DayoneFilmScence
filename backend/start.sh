#!/bin/bash

# Day One Film AI - 启动脚本
# 影视场景参考搜索工具后端启动脚本

echo "🎬 Day One Film AI 启动脚本"
echo "=============================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，复制 .env.example..."
    cp .env.example .env
    echo "✅ 请编辑 .env 文件，添加你的 API Keys"
    echo "   特别是 GEMINI_API_KEY（从 https://aistudio.google.com/app/apikey 获取）"
fi

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 启动服务
echo ""
echo "🚀 启动服务..."
echo "   访问: http://localhost:8000"
echo "   文档: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
