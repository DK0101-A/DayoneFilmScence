#!/bin/bash
# 一键部署脚本 - Day One Film AI
# 用法: ./deploy.sh

set -e

echo "🚀 Day One Film AI - 部署助手"
echo "=================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git 未安装${NC}"
    exit 1
fi

# 检查GitHub CLI
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✅ GitHub CLI 已安装${NC}"
    USE_GH=true
else
    echo -e "${YELLOW}⚠️  GitHub CLI 未安装${NC}"
    echo "   安装: brew install gh"
    USE_GH=false
fi

echo ""
echo "请选择部署方式:"
echo "1) Render (推荐，完全免费)"
echo "2) Railway (免费额度)"
echo "3) 自有服务器/Docker"
echo "4) 仅推送到GitHub"
echo ""
read -p "输入选项 (1-4): " choice

case $choice in
    1)
        PLATFORM="Render"
        ;;
    2)
        PLATFORM="Railway"
        ;;
    3)
        PLATFORM="Docker"
        ;;
    4)
        PLATFORM="GitHub Only"
        ;;
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}选择了: $PLATFORM${NC}"
echo ""

# GitHub部分
if [ "$USE_GH" = true ]; then
    echo "检查GitHub认证..."
    if ! gh auth status &> /dev/null; then
        echo -e "${YELLOW}请先登录GitHub CLI:${NC}"
        gh auth login
    fi
    
    echo -e "${GREEN}✅ 已登录GitHub${NC}"
    
    # 创建仓库
    echo ""
    echo "创建GitHub仓库..."
    REPO_NAME="day-one-film-ai"
    
    if gh repo create "$REPO_NAME" --public --source=. --remote=origin --push 2>/dev/null; then
        echo -e "${GREEN}✅ 仓库创建成功并推送代码${NC}"
        REPO_URL="https://github.com/$(gh api user | grep -o '"login":"[^"]*' | cut -d'"' -f4)/$REPO_NAME"
    else
        echo -e "${YELLOW}⚠️  仓库可能已存在，尝试推送...${NC}"
        git remote remove origin 2>/dev/null || true
        git remote add origin "https://github.com/$(gh api user | grep -o '"login":"[^"]*' | cut -d'"' -f4)/$REPO_NAME.git"
        git push -u origin main
        REPO_URL="https://github.com/$(gh api user | grep -o '"login":"[^"]*' | cut -d'"' -f4)/$REPO_NAME"
    fi
else
    echo -e "${YELLOW}⚠️  请手动创建GitHub仓库:${NC}"
    echo "   1. 访问: https://github.com/new"
    echo "   2. 仓库名: day-one-film-ai"
    echo "   3. 选择 Public"
    echo ""
    read -p "创建完成后，输入你的GitHub用户名: " GITHUB_USER
    
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://github.com/$GITHUB_USER/day-one-film-ai.git"
    git branch -M main
    git push -u origin main
    
    REPO_URL="https://github.com/$GITHUB_USER/day-one-film-ai"
    echo -e "${GREEN}✅ 代码已推送到: $REPO_URL${NC}"
fi

echo ""
echo "=================================="

# 根据平台部署
case $choice in
    1)
        echo -e "${GREEN}🚀 部署到 Render${NC}"
        echo ""
        echo "步骤:"
        echo "1. 访问: https://dashboard.render.com"
        echo "2. 点击 New + → Web Service"
        echo "3. 连接GitHub仓库: $REPO_URL"
        echo "4. 配置:"
        echo "   - Build Command: pip install -r backend/requirements.txt"
        echo "   - Start Command: cd backend && python run_full.py"
        echo "5. 添加环境变量:"
        echo "   OPENAI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487"
        echo "   APIYI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487"
        echo "6. 点击 Create Web Service"
        echo ""
        echo -e "${YELLOW}提示: Render免费版15分钟无活动会休眠，首次访问较慢${NC}"
        ;;
        
    2)
        echo -e "${GREEN}🚀 部署到 Railway${NC}"
        echo ""
        echo "步骤:"
        echo "1. 访问: https://railway.app"
        echo "2. 点击 New Project → Deploy from GitHub repo"
        echo "3. 选择仓库: day-one-film-ai"
        echo "4.  Railway会自动读取 railway.json 配置"
        echo "5. 添加环境变量:"
        echo "   OPENAI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487"
        echo "   APIYI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487"
        echo "6. 重新部署"
        ;;
        
    3)
        echo -e "${GREEN}🐳 Docker部署${NC}"
        echo ""
        if command -v docker &> /dev/null; then
            echo "构建Docker镜像..."
            docker build -t day-one-film-ai .
            
            echo ""
            echo "运行容器..."
            docker run -d \
                -p 8000:8000 \
                -e OPENAI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487 \
                -e APIYI_API_KEY=sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487 \
                --name day-one-film-ai \
                day-one-film-ai
            
            echo ""
            echo -e "${GREEN}✅ Docker容器已启动${NC}"
            echo "访问: http://localhost:8000"
        else
            echo -e "${RED}❌ Docker 未安装${NC}"
            echo "安装: https://docs.docker.com/get-docker/"
        fi
        ;;
        
    4)
        echo -e "${GREEN}✅ 代码已推送到GitHub${NC}"
        echo "仓库地址: $REPO_URL"
        echo ""
        echo "接下来你可以:"
        echo "1. 在Render/Railway部署"
        echo "2. 查看详细部署指南: docs/DEPLOYMENT-GUIDE.md"
        ;;
esac

echo ""
echo "=================================="
echo -e "${GREEN}🎉 完成！${NC}"
echo ""

# 显示后续步骤
if [ "$choice" != "4" ]; then
    echo "部署完成后:"
    echo "1. 获取公网URL"
    echo "2. 更新扣子Agent的API地址"
    echo "3. 在豆包中测试"
    echo ""
fi

echo "详细指南: docs/DEPLOYMENT-GUIDE.md"
