"""
Day One Film AI - Configuration Module
影视场景参考搜索工具配置模块
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional


class Settings(BaseSettings):
    """
    应用配置类

    支持多环境配置，通过.env文件加载
    """

    # 应用信息
    APP_NAME: str = "Day One Film AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]

    # ============================================
    # AI模型配置
    # ============================================

    # AI Studio / Gemini (开发期)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"  # 免费版推荐
    GEMINI_VISION_MODEL: str = "gemini-1.5-flash"

    # 国产大模型（生产环境）
    DOUBAO_API_KEY: str = ""
    DOUBAO_MODEL: str = "doubao-lite-4k"

    QWEN_API_KEY: str = ""
    QWEN_MODEL: str = "qwen-turbo"

    ZHIPU_API_KEY: str = ""

    # 当前使用的AI提供商
    AI_PROVIDER: str = "apiyi"  # gemini | doubao | qwen | zhipu | apiyi

    # ============================================
    # API易配置（OpenAI兼容）
    # ============================================

    OPENAI_BASE_URL: str = "https://api.apiyi.com/v1"
    OPENAI_API_KEY: str = ""
    APIYI_API_KEY: str = ""  # 兼容旧代码
    AI_MODEL: str = "gemini-2.5-flash-image"  # 默认使用 Gemini 2.5
    FLASH_MODEL: str = "gemini-2.5-flash-image"
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    DEFAULT_MODEL: str = "gemini-2.5-flash-image"

    # ============================================
    # 数据源配置
    # ============================================

    DOUBAN_API_KEY: Optional[str] = None
    TMDB_API_KEY: Optional[str] = None

    # YouTube Data API v3 (免费配额：每天100次搜索)
    YOUTUBE_API_KEY: Optional[str] = None

    # ============================================
    # 功能开关
    # ============================================

    # 是否启用图片分析（需要多模态模型）
    ENABLE_IMAGE_ANALYSIS: bool = True

    # 是否启用缓存
    ENABLE_CACHE: bool = False

    # 搜索配置
    DEFAULT_SEARCH_LIMIT: int = 10
    MAX_SEARCH_LIMIT: int = 20

    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_SEARCH_PER_USER_PER_DAY: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例（单例模式）

    Returns:
        Settings实例
    """
    return Settings()


# 全局配置实例
settings = get_settings()
