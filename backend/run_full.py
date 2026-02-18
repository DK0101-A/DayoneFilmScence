#!/usr/bin/env python3
"""
完整版启动脚本 - 包含静态文件服务
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ["OPENAI_BASE_URL"] = "https://api.apiyi.com/v1"
os.environ["OPENAI_API_KEY"] = "sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487"
os.environ["APIYI_API_KEY"] = "sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487"
os.environ["AI_MODEL"] = "gemini-2.0-flash"

print("🚀 启动 Day One Film AI...")
print("=" * 50)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 创建应用
app = FastAPI(title="Day One Film AI", version="0.1.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")


# 基础路由
@app.get("/")
async def root():
    return {"name": "Day One Film AI", "status": "running", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# 加载API路由
try:
    from app.api.search import router as search_router

    app.include_router(search_router, prefix="/api")
    print("✅ 搜索路由加载成功")
except Exception as e:
    print(f"⚠️ 搜索路由: {e}")

try:
    from app.api.auth import router as auth_router

    app.include_router(auth_router)
    print("✅ 认证路由加载成功")
except Exception as e:
    print(f"⚠️ 认证路由: {e}")

try:
    from app.api.favorites import router as favorites_router

    app.include_router(favorites_router)
    print("✅ 收藏路由加载成功")
except Exception as e:
    print(f"⚠️ 收藏路由: {e}")

try:
    from app.api.admin import router as admin_router

    app.include_router(admin_router)
    print("✅ 管理路由加载成功")
except Exception as e:
    print(f"⚠️ 管理路由: {e}")

print("=" * 50)
print("🌐 服务地址: http://localhost:8000")
print("📚 API文档: http://localhost:8000/docs")
print("🎨 前端界面: http://localhost:8000/static/search.html")
print("=" * 50)

# 启动服务
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
