"""
Gemini AI提供商实现
使用Google AI Studio的Gemini Pro和Gemini Pro Vision

开发期使用，能力最强，用于快速验证需求
后期可平滑迁移到国产模型
"""

import google.generativeai as genai
from typing import List, Dict, Any
import json
import re
import httpx

from app.services.ai_interface import AISceneProvider


class GeminiProvider(AISceneProvider):
    """
    Gemini AI提供商

    能力特点：
    - 多语言能力强（中英文都很好）
    - 原生多模态（可以分析图片）
    - 影视知识丰富（全球影片库）
    - 创意描述能力强

    使用场景：
    - 开发期快速验证
    - 专业版/旗舰版功能
    """

    def __init__(self, api_key: str):
        """
        初始化Gemini提供商

        Args:
            api_key: Google AI Studio API Key
        """
        genai.configure(api_key=api_key)
        # 使用可用的Gemini模型
        self._text_model = genai.GenerativeModel("gemini-2.0-flash")
        self._vision_model = genai.GenerativeModel("gemini-2.0-flash")

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "text_understanding": True,
            "image_analysis": True,
            "multilingual": True,
            "streaming": False,
            "batch_processing": False,
        }

    async def understand_scene(self, query: str) -> Dict[str, Any]:
        """
        使用Gemini深度理解场景描述

        优势：
        - 理解更复杂的场景描述
        - 推荐更精准的相似影片（包括海外片）
        - 生成更详细的搜索关键词
        """
        prompt = f"""你是一位资深影视导演，擅长分析场景描述并提取关键要素。

用户场景描述: "{query}"

请详细分析并输出JSON格式:
{{
    "scene_elements": ["提取的核心视觉元素，如地点、动作、氛围"],
    "keywords_zh": ["3-5个中文搜索关键词，用于搜影视片段"],
    "keywords_en": ["3-5个英文搜索关键词，扩大搜索范围"],
    "mood": "场景的情绪基调（如紧张、浪漫、悬疑）",
    "visual_style": "视觉风格建议（光线、色调、摄影风格）",
    "similar_movies": ["3-5部有相似场景的著名电影，中文片名，包括华语和海外片"],
    "shot_suggestions": ["建议的镜头类型（如广角、特写、跟拍）"]
}}

注意：
1. 必须输出合法JSON格式
2. similar_movies要包括国内外经典影片
3. 不要输出任何其他文字
"""

        try:
            response = await self._text_model.generate_content_async(prompt)
            content = response.text

            # 清理可能的Markdown代码块
            content = re.sub(r"```json\n?", "", content)
            content = re.sub(r"\n?```", "", content)
            content = content.strip()

            return json.loads(content)

        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}, 内容: {content}")
            # 降级返回
            return self._fallback_understanding(query)
        except Exception as e:
            print(f"Gemini调用失败: {e}")
            return self._fallback_understanding(query)

    def _fallback_understanding(self, query: str) -> Dict[str, Any]:
        """降级处理：当AI调用失败时返回基础结构"""
        return {
            "scene_elements": query.split(),
            "keywords_zh": [f"{query} 电影", f"{query} 片段", f"{query} 场景"],
            "keywords_en": [query.replace(" ", " ")],
            "mood": "待分析",
            "visual_style": "待分析",
            "similar_movies": [],
            "shot_suggestions": ["标准镜头"],
        }

    async def rank_scenes(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        使用Gemini智能排序候选结果

        优势：可以理解复杂的匹配逻辑，不只是关键词匹配
        """
        if not candidates:
            return []

        # 构建评估prompt
        candidates_text = "\n\n".join(
            [
                f"[{i + 1}] {c.get('title', '未知')} ({c.get('year', '未知')})\n"
                f"    简介: {c.get('summary', c.get('description', '无'))[:150]}..."
                for i, c in enumerate(candidates[:20])
            ]
        )

        prompt = f"""用户想找的场景: "{query}"

候选影片:
{candidates_text}

请评估每个候选与用户场景的匹配度，输出JSON数组:
[
    {{
        "index": 1,
        "relevance_score": 85,
        "explanation": "为什么匹配，如'都有雨夜追车的紧张氛围，镜头语言相似'",
        "scene_match": "具体匹配的scene描述"
    }},
    ...
]

评分标准:
- 90-100: 完美匹配，场景几乎一致
- 70-89: 高度相关，值得参考
- 50-69: 有一定参考价值
- <50: 不太相关

必须输出合法JSON数组，不要有其他文字。
"""

        try:
            response = await self._text_model.generate_content_async(prompt)
            content = response.text

            # 清理
            content = re.sub(r"```json\n?", "", content)
            content = re.sub(r"\n?```", "", content)
            content = content.strip()

            rankings = json.loads(content)

            # 合并评分到原数据
            for rank in rankings:
                idx = rank.get("index", 0) - 1
                if 0 <= idx < len(candidates):
                    candidates[idx]["relevance_score"] = rank.get("relevance_score", 50)
                    candidates[idx]["explanation"] = rank.get("explanation", "")
                    candidates[idx]["scene_match"] = rank.get("scene_match", "")

            # 排序
            candidates.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            return candidates[:top_k]

        except Exception as e:
            print(f"排序失败: {e}")
            # 降级：按年份排序
            candidates.sort(key=lambda x: x.get("year", 0), reverse=True)
            return candidates[:top_k]

    async def analyze_image_relevance(
        self, scene_description: str, image_url: str
    ) -> Dict[str, Any]:
        """
        使用Gemini Vision分析图片是否与场景匹配

        这是Gemini的独特优势：可以直接看懂图片内容！
        用于：验证搜索到的剧照是否真的匹配场景
        """
        try:
            # 下载图片
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=10.0)
                image_data = response.content

            prompt = f"""分析这张图片是否符合场景描述: "{scene_description}"

请输出JSON格式:
{{
    "relevance_score": 85,
    "explanation": "详细解释为什么匹配或不匹配",
    "visual_elements": ["图片中的关键视觉元素"],
    "mood_match": "情绪氛围是否匹配",
    "visual_style": "视觉风格分析（光线、色调、构图）"
}}

评分标准:
- 90-100: 完美匹配
- 70-89: 高度相关
- 50-69: 有一定相似性
- <50: 不太相关
"""

            response = await self._vision_model.generate_content_async(
                [prompt, {"mime_type": "image/jpeg", "data": image_data}]
            )

            content = response.text
            content = re.sub(r"```json\n?", "", content)
            content = re.sub(r"\n?```", "", content)

            return json.loads(content)

        except Exception as e:
            print(f"图片分析失败: {e}")
            return {
                "relevance_score": 50,
                "explanation": "无法分析图片",
                "visual_elements": [],
                "mood_match": "未知",
                "visual_style": "未知",
            }
