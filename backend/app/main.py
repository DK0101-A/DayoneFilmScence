"""
Day One Film AI - 影视场景参考搜索工具
FastAPI主应用入口
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import settings
from app.api.search import router as search_router
from app.api.favorites import router as favorites_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时：初始化AI服务、检查配置
    关闭时：清理资源
    """
    # 启动
    print(f"🎬 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    print(f"   AI提供商: {settings.AI_PROVIDER}")
    print(f"   调试模式: {settings.DEBUG}")

    # 检查必要的配置
    if settings.AI_PROVIDER == "gemini" and not settings.GEMINI_API_KEY:
        print("⚠️ 警告: GEMINI_API_KEY 未设置")

    yield

    # 关闭
    print(f"👋 {settings.APP_NAME} 关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="AI驱动的影视场景参考搜索工具 - 帮助导演快速找到相似场景的影视参考",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS中间件（允许扣子跨域调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(search_router, prefix="/api")
app.include_router(favorites_router)
app.include_router(auth_router)
app.include_router(admin_router)

# 静态文件服务（管理后台前端）
app.mount("/admin", StaticFiles(directory="static/admin", html=True), name="admin")
# 前端页面
app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
async def root():
    """根路径 - 返回基本信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI驱动的影视场景参考搜索工具",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "ai_provider": settings.AI_PROVIDER,
        "timestamp": "2024-01-01T00:00:00Z",  # 实际应返回当前时间
    }
