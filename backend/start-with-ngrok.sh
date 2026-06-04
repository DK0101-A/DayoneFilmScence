#!/bin/bash
# 启动后端服务 + ngrok 内网穿透
# 用于扣子Agent本地开发测试

echo "🎬 Day One Film AI - 启动开发环境"
echo "=================================="

# 检查ngrok是否安装
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok 未安装"
    echo "安装命令: brew install ngrok"
    exit 1
fi

echo "✅ ngrok 已安装"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python -m venv venv"
    exit 1
fi

echo "✅ 虚拟环境存在"

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -q -r requirements.txt

# 启动后端服务（后台）
echo "🚀 启动后端服务..."
python run_simple.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ 后端服务已启动: http://localhost:8000"

# 启动ngrok
echo ""
echo "🔗 启动 ngrok 内网穿透..."
echo "=================================="
echo "等待ngrok生成公网URL..."
echo ""

# 启动ngrok并捕获输出
ngrok http 8000 &
NGROK_PID=$!

# 等待ngrok启动
sleep 5

# 获取ngrok URL
echo ""
echo "🌐 你的公网地址:"
curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'https://[^"]*'

echo ""
echo "=================================="
echo "✅ 开发环境已启动！"
echo ""
echo "📋 使用说明:"
echo "1. 后端服务: http://localhost:8000"
echo "2. API文档: http://localhost:8000/docs"
echo "3. 扣子配置: 使用上面的 https://xxx.ngrok.io 地址"
echo "4. 测试命令: curl http://localhost:8000/health"
echo ""
echo "⚠️  按 Ctrl+C 停止所有服务"
echo "=================================="

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $NGROK_PID 2>/dev/null; exit 0" INT
wait
