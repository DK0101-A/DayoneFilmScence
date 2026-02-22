"""
通义千问 Provider - 使用 DashScope SDK
"""

import os
import dashscope
from typing import List, Dict, Any, Optional
from app.services.ai_interface import AISceneProvider


class QwenProvider(AISceneProvider):
    """通义千问 AI 提供商"""

    def __init__(self, api_key: str, model: str = "qwen-turbo"):
        self.api_key = api_key
        self.model = model
        dashscope.api_key = api_key

    @property
    def provider_name(self) -> str:
        return "qwen-turbo"

    @property
    def capabilities(self) -> Dict[str, Any]:
        return {
            "supports_streaming": False,
            "supports_vision": False,
            "max_tokens": 2000,
        }

    async def analyze_image_relevance(self, image_url: str, query: str) -> float:
        """分析图片与场景的相关度"""
        return 0.5

    @property
    def provider_type(self) -> str:
        return "qwen"

    async def understand_scene(self, query: str) -> Dict[str, Any]:
        """理解场景，返回关键词"""
        prompt = f"""分析以下电影场景描述，提取关键信息：

场景描述: {query}

请以JSON格式返回：
{{
    "keywords_zh": ["关键词1", "关键词2"],
    "keywords_en": ["keyword1", "keyword2"],
    "mood": "情绪/氛围",
    "scene_elements": ["场景元素1", "场景元素2"]
}}

只返回JSON，不要其他内容。"""

        response = dashscope.Generation.call(
            model=self.model,
            prompt=prompt,
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            try:
                import json
                result = json.loads(content)
                return result
            except:
                return {
                    "keywords_zh": [query],
                    "keywords_en": [],
                    "mood": "",
                    "scene_elements": []
                }
        else:
            return {
                "keywords_zh": [query],
                "keywords_en": [],
                "mood": "",
                "scene_elements": []
            }

    async def rank_scenes(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """对候选场景进行AI排序"""
        if not candidates:
            return []

        prompt = f"""电影场景匹配任务：

用户需求: {query}

候选电影:
{chr(10).join([f"- {c.get('title', '')} ({c.get('year', '')}): {c.get('summary', '')[:100]}" for c in candidates[:10]])}

请根据与用户需求的匹配度，给每个电影打分(0-100)，返回JSON数组格式:
[{{"index": 0, "score": 85, "reason": "理由"}}, ...]

只返回JSON数组。"""

        response = dashscope.Generation.call(
            model=self.model,
            prompt=prompt,
            result_format='message'
        )

        if response.status_code == 200:
            try:
                import json
                content = response.output.choices[0].message.content
                scores = json.loads(content)
                for sc in scores:
                    idx = sc.get("index", 0)
                    score = int(sc.get("score", 50))
                    if idx < len(candidates):
                        candidates[idx]["relevance_score"] = score
            except:
                pass
        
        return candidates[:top_k]

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成内容"""
        response = dashscope.Generation.call(
            model=self.model,
            prompt=prompt,
            result_format='message'
        )
        if response.status_code == 200:
            return response.output.choices[0].message.content
        return ""
