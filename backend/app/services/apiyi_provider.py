"""
API易 OpenAI兼容适配器

支持：
- Gemini 2.0 Flash（主力）
- Claude 3.5 Sonnet（专业）
- 其他200+模型

使用OpenAI API格式，一套代码切换所有模型
"""

import httpx
from typing import List, Dict, Any, Optional
import json
import os

from app.services.ai_interface import AISceneProvider


class APIYiProvider(AISceneProvider):
    """
    API易 OpenAI兼容提供商

    统一接口支持：
    - Gemini 2.0 Flash（速度快、便宜）
    - Claude 3.5 Sonnet（能力强、创意好）
    - 其他200+主流模型

    只需更换model参数，无需改动其他代码

    使用方法：
    provider = APIYiProvider(
        api_key="your_key",
        model="gemini-2.0-flash"  # 或 "claude-3-5-sonnet-20241022"
    )
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        base_url: str = "https://api.apiyi.com/v1",
    ):
        """
        初始化API易提供商

        Args:
            api_key: API易API Key
            model: 模型名称
                - gemini-2.0-flash: 主力模型（快、便宜）
                - claude-3-5-sonnet-20241022: 专业模型（强、创意）
            base_url: API基础URL
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

        # 根据模型名称识别提供商类型
        if "claude" in model.lower():
            self.provider_type = "claude"
        elif "gemini" in model.lower():
            self.provider_type = "gemini"
        else:
            self.provider_type = "openai"

    @property
    def provider_name(self) -> str:
        return f"apiyi-{self.provider_type}"

    @property
    def capabilities(self) -> Dict[str, bool]:
        caps = {
            "text_understanding": True,
            "multilingual": True,
            "streaming": True,
        }

        # Claude不支持图片，Gemini支持
        if self.provider_type == "claude":
            caps["image_analysis"] = False
        else:
            caps["image_analysis"] = True

        return caps

    async def _call_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        调用API易OpenAI兼容接口

        核心方法，所有其他方法都基于此
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )

                if response.status_code != 200:
                    error_data = response.json()
                    raise Exception(
                        f"API错误: {error_data.get('error', {}).get('message', '未知错误')}"
                    )

                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"API调用失败: {e}")
            raise

    async def understand_scene(self, query: str) -> Dict[str, Any]:
        """
        场景理解

        根据模型类型使用不同的prompt策略
        """
        if self.provider_type == "claude":
            # Claude用更详细的prompt，发挥其长文本优势
            messages = [
                {
                    "role": "system",
                    "content": "你是一位资深影视导演和编剧，擅长深度分析影视场景。",
                },
                {
                    "role": "user",
                    "content": f"""请深度分析以下场景描述："{query}"

请提供以下分析：
1. 场景核心要素（地点、时间、动作、情绪）
2. 视觉风格建议（光线、色调、摄影风格）
3. 推荐参考影片（3-5部华语和海外电影）
4. 中英文搜索关键词（各3-5个）

以JSON格式输出：
{{
    "scene_elements": ["要素1", "要素2"],
    "mood": "情绪描述",
    "visual_style": "视觉风格建议",
    "similar_movies": ["《电影名1》（年份）", "电影名2 (年份)"],
    "keywords": {{"zh": ["中文词1"], "en": ["english keyword"]}}
}}""",
                },
            ]
        else:
            # Gemini用简洁prompt，追求速度
            messages = [
                {
                    "role": "user",
                    "content": f"""分析影视场景："{query}"

输出JSON：
{{
    "scene_elements": ["核心要素"],
    "mood": "情绪",
    "visual_style": "视觉风格",
    "similar_movies": ["电影名（年份）"],
    "keywords": {{"zh": ["中文词"], "en": ["英文词"]}}
}}""",
                }
            ]

        try:
            content = await self._call_api(messages, temperature=0.7)

            # 解析JSON
            try:
                # 清理可能的markdown
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                return json.loads(content)
            except:
                # 解析失败返回简化结构
                return {
                    "scene_elements": [query],
                    "mood": "待分析",
                    "visual_style": "待分析",
                    "similar_movies": [],
                    "keywords": {"zh": [query], "en": [query]},
                    "raw_response": content[:200],
                }
        except Exception as e:
            print(f"场景理解失败: {e}")
            return {
                "scene_elements": [query],
                "mood": "分析失败",
                "similar_movies": [],
                "keywords": {"zh": [query], "en": [query]},
            }

    async def rank_scenes(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        智能排序候选结果，并添加时间戳信息
        """
        if not candidates:
            return []

        # 构建候选列表文本
        candidates_text = "\n".join(
            [
                f"{i + 1}. {c.get('title', '未知')} ({c.get('year', '')}) - {c.get('summary', '无简介')[:100]}"
                for i, c in enumerate(candidates[:15])
            ]
        )

        messages = [
            {
                "role": "user",
                "content": f"""用户想找的场景: "{query}"

候选影片:
{candidates_text}

请评估匹配度，并为每部影片提供场景时间戳。

输出JSON数组:
[{{
    "index": 1, 
    "relevance_score": 85, 
    "explanation": "为什么匹配",
    "timestamp": "00:32:15",
    "timestamp_note": "影片第32分钟左右"
}}]

要求:
1. timestamp: 估算的场景出现时间，格式 HH:MM:SS 或 中文描述
2. timestamp_note: 时间戳说明，如"开场15分钟"、"高潮部分"、"结尾前20分钟"
3. 基于你对电影的了解，估算该场景大概出现在影片的什么时间
4. 如果不确定，可以写"约第30-40分钟"

评分: 90-100完美, 70-89高度相关, 50-69一般, <50不相关""",
            }
        ]

        try:
            content = await self._call_api(messages, temperature=0.3, max_tokens=2000)

            try:
                # 清理并解析
                content = content.strip()
                if "```" in content:
                    content = content.split("```")[1].replace("json", "").strip()

                rankings = json.loads(content)

                # 合并评分和时间戳
                for rank in rankings:
                    idx = rank.get("index", 0) - 1
                    if 0 <= idx < len(candidates):
                        candidates[idx]["relevance_score"] = rank.get(
                            "relevance_score", 50
                        )
                        candidates[idx]["explanation"] = rank.get("explanation", "")
                        candidates[idx]["timestamp"] = rank.get("timestamp", "")
                        candidates[idx]["timestamp_note"] = rank.get(
                            "timestamp_note", ""
                        )

                # 排序
                candidates.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                return candidates[:top_k]
            except Exception as parse_error:
                print(f"解析排序结果失败: {parse_error}")
                # 降级排序
                candidates.sort(key=lambda x: x.get("year", 0), reverse=True)
                return candidates[:top_k]
        except Exception as e:
            print(f"排序失败: {e}")
            candidates.sort(key=lambda x: x.get("year", 0), reverse=True)
            return candidates[:top_k]

    async def analyze_image_relevance(
        self, scene_description: str, image_url: str
    ) -> Dict[str, Any]:
        """
        图片相关性分析（仅Gemini支持）
        """
        if self.provider_type == "claude":
            return {
                "relevance_score": 50,
                "explanation": "Claude不支持图片分析",
                "visual_style": "未知",
            }

        # Gemini可以通过多模态支持图片
        # 这里简化处理，返回默认值
        return {
            "relevance_score": 70,
            "explanation": "图片分析功能待实现",
            "visual_style": "待分析",
        }

    # ===== A模块专用方法 =====

    async def parse_script(self, script_content: str) -> Dict[str, Any]:
        """
        解析剧本（A模块）

        推荐使用Claude模型
        """
        # 截断过长内容
        script_truncated = script_content[:8000]

        messages = [
            {"role": "system", "content": "你是一位专业编剧，擅长解析剧本结构。"},
            {
                "role": "user",
                "content": f"""请解析以下剧本：

{script_truncated}

提取：
1. 剧本标题和类型
2. 所有场景（编号、地点、时间、描述）
3. 主要角色
4. 剧情结构

输出JSON格式。""",
            },
        ]

        try:
            content = await self._call_api(messages, max_tokens=4000)
            try:
                return json.loads(content)
            except:
                return {"raw_analysis": content}
        except Exception as e:
            return {"error": str(e)}

    async def generate_shots(self, scene_description: str) -> List[Dict[str, Any]]:
        """
        生成分镜（A模块）
        """
        messages = [
            {
                "role": "user",
                "content": f"""为以下场景设计5-8个分镜：

场景：{scene_description}

每个分镜包含：
1. 镜头编号
2. 镜头类型
3. 画面描述
4. 镜头运动
5. 时长建议

输出JSON数组。""",
            }
        ]

        try:
            content = await self._call_api(messages, max_tokens=2000)
            try:
                return json.loads(content)
            except:
                return [{"description": content}]
        except Exception as e:
            return [{"error": str(e)}]
