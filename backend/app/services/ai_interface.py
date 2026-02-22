"""
AI服务抽象接口层
支持多模型切换：Gemini、豆包、通义千问等

架构设计：
- 抽象基类定义统一接口
- 各模型实现具体逻辑
- 工厂模式动态创建实例
- 便于分层收费和A/B测试
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AISceneProvider(ABC):
    """
    AI场景理解抽象接口

    所有AI提供商（Gemini、豆包、通义等）都需要实现此接口
    便于后期分层收费：
    - 基础版：豆包/通义
    - 专业版：Gemini
    - 旗舰版：Gemini + 更多功能
    """

    @abstractmethod
    async def understand_scene(self, query: str) -> Dict[str, Any]:
        """
        理解场景描述，提取关键要素

        Args:
            query: 用户场景描述，如"雨夜追车"

        Returns:
            {
                "scene_elements": ["雨夜", "追车", "紧张"],
                "keywords_zh": ["雨夜追车 电影", ...],
                "keywords_en": ["rainy night car chase", ...],
                "mood": "紧张刺激",
                "visual_style": "暗调、霓虹反光",
                "similar_movies": ["《盗梦空间》", ...],
                "shot_suggestions": ["广角镜头", ...]
            }
        """
        pass

    @abstractmethod
    async def rank_scenes(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        对候选结果进行AI智能排序

        Args:
            query: 原始查询
            candidates: 候选结果列表
            top_k: 返回前K个

        Returns:
            排序后的结果，每个带relevance_score和explanation
        """
        pass

    @abstractmethod
    async def analyze_image_relevance(
        self, scene_description: str, image_url: str
    ) -> Dict[str, Any]:
        """
        分析图片是否与场景描述匹配（多模态能力）

        Args:
            scene_description: 场景描述
            image_url: 图片URL

        Returns:
            {
                "relevance_score": 85,
                "explanation": "为什么匹配",
                "visual_style": "视觉风格分析"
            }
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """返回提供商名称"""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """
        返回能力清单

        Returns:
            {
                "text_understanding": True,
                "image_analysis": True,
                "multilingual": True,
                "streaming": False
            }
        """
        pass


class AIProviderFactory:
    """
    AI提供商工厂

    根据配置动态创建对应的AI提供商实例
    支持运行时切换（用于A/B测试、分层收费等）
    """

    _providers = {}

    @classmethod
    def register(cls, name: str, provider_class: type):
        """注册新的AI提供商"""
        cls._providers[name] = provider_class

    @classmethod
    def create(cls, provider_name: str, **kwargs) -> AISceneProvider:
        """
        创建AI提供商实例

        Args:
            provider_name: 提供商名称 (gemini, doubao, qwen等)
            **kwargs: 传递给提供商构造函数的参数

        Returns:
            AISceneProvider实例
        """
        if provider_name not in cls._providers:
            raise ValueError(
                f"未知的AI提供商: {provider_name}. 可用: {list(cls._providers.keys())}"
            )

        return cls._providers[provider_name](**kwargs)

    @classmethod
    def list_providers(cls) -> List[str]:
        """列出所有已注册的提供商"""
        return list(cls._providers.keys())


# 延迟导入具体实现（避免循环导入）
def _register_providers():
    """注册所有可用的AI提供商"""
    try:
        from app.services.gemini_provider import GeminiProvider

        AIProviderFactory.register("gemini", GeminiProvider)
        AIProviderFactory.register("flash", GeminiProvider)  # 别名
    except ImportError as e:
        print(f"Gemini提供商未注册: {e}")

    try:
        from app.services.claude_provider import ClaudeProvider

        AIProviderFactory.register("claude", ClaudeProvider)
    except ImportError as e:
        print(f"Claude提供商未注册: {e}")

    # 注册API易提供商（OpenAI兼容，支持Gemini+Claude）
    try:
        from app.services.apiyi_provider import APIYiProvider

        AIProviderFactory.register("apiyi", APIYiProvider)
        AIProviderFactory.register(
            "apiyi-flash",
            lambda **kwargs: APIYiProvider(model="gemini-2.0-flash", **kwargs),
        )
        AIProviderFactory.register(
            "apiyi-claude",
            lambda **kwargs: APIYiProvider(
                model="claude-3-5-sonnet-20241022", **kwargs
            ),
        )
    except ImportError as e:
        print(f"API易提供商未注册: {e}")

    # 注册通义千问提供商
    try:
        from app.services.qwen_provider import QwenProvider

        AIProviderFactory.register("qwen", QwenProvider)
    except ImportError as e:
        print(f"通义千问提供商未注册: {e}")

    # 未来注册其他提供商
    # try:
    #     from app.services.doubao_provider import DoubaoProvider
    #     AIProviderFactory.register("doubao", DoubaoProvider)
    # except ImportError:
    #     pass


# 自动注册
_register_providers()
