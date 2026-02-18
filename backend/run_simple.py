#!/usr/bin/env python3
"""
简化版启动脚本 - 用于快速测试
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ["OPENAI_BASE_URL"] = "https://api.apiyi.com/v1"
os.environ["OPENAI_API_KEY"] = "sk-yTxUvlKy5ECccUHL78725dF186Ef494d8b05CdC04d32C487"
os.environ["AI_MODEL"] = "gemini-2.0-flash"

print("🚀 启动 Day One Film AI...")
print("=" * 50)

try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    # 创建简化版应用
    app = FastAPI(title="Day One Film AI - 测试版")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 静态文件服务
    from fastapi.staticfiles import StaticFiles

    app.mount("/static", StaticFiles(directory="static"), name="static")

    # 基础路由
    @app.get("/")
    async def root():
        return {"name": "Day One Film AI", "status": "running", "version": "0.1.0"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    # 尝试导入完整路由
    try:
        from app.api.search import router as search_router

        app.include_router(search_router, prefix="/api")
        print("✅ 搜索路由加载成功")
    except Exception as e:
        print(f"⚠️ 搜索路由加载失败: {e}")

    try:
        from app.api.auth import router as auth_router

        app.include_router(auth_router)
        print("✅ 认证路由加载成功")
    except Exception as e:
        print(f"⚠️ 认证路由加载失败: {e}")

    try:
        from app.api.favorites import router as favorites_router

        app.include_router(favorites_router)
        print("✅ 收藏路由加载成功")
    except Exception as e:
        print(f"⚠️ 收藏路由加载失败: {e}")

    try:
        from app.api.admin import router as admin_router

        app.include_router(admin_router)
        print("✅ 管理路由加载成功")
    except Exception as e:
        print(f"⚠️ 管理路由加载失败: {e}")

    print("=" * 50)
    print("🌐 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("=" * 50)

    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback

    traceback.print_exc()
