"""
Claude AI提供商实现
使用Anthropic Claude 3.5 Sonnet

适用场景：
- 剧本解析（长文本理解）
- 分镜生成（创意描述）
- 复杂场景分析（推理能力）
"""

import httpx
from typing import List, Dict, Any
import json

from app.services.ai_interface import AISceneProvider


class ClaudeProvider(AISceneProvider):
    """
    Claude 3.5 Sonnet AI提供商

    能力特点：
    - 长文本理解能力最强（适合剧本）
    - 创意写作优秀（适合分镜描述）
    - 推理能力强（适合复杂分析）
    - 结构化输出稳定

    使用场景：
    - A模块：剧本拆解、场景提取、分镜生成
    - 复杂场景分析
    - 导演大脑训练（创意模式）

    成本：¥0.015/1K tokens（比Flash贵5倍，但能力强）
    """

    def __init__(self, api_key: str, base_url: str = "https://api.apiyi.com/v1"):
        """
        初始化Claude提供商

        Args:
            api_key: API易或Anthropic API Key
            base_url: API基础URL（默认API易）
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = "claude-3-5-sonnet-20241022"

    @property
    def provider_name(self) -> str:
        return "claude"

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "text_understanding": True,
            "image_analysis": False,  # Claude 3.5 Sonnet不支持图片
            "multilingual": True,
            "streaming": True,
            "long_context": True,  # 200K上下文
            "creative_writing": True,  # 创意写作强
        }

    async def understand_scene(self, query: str) -> Dict[str, Any]:
        """
        使用Claude深度理解场景

        优势：比Flash更深入的理解，更详细的分析
        """
        prompt = f"""你是一位资深影视导演和编剧，擅长深度分析场景。

请深度分析以下场景描述："{query}"

请提供以下分析：
1. 场景核心要素（地点、时间、动作、情绪）
2. 视觉风格建议（光线、色调、摄影风格、镜头语言）
3. 叙事功能（这个场景在故事中的作用）
4. 推荐参考影片（3-5部，说明为什么相似）
5. 分镜建议（3-5个关键镜头的描述）
6. 中英文搜索关键词（各5个）

请以JSON格式输出：
{{
    "scene_elements": {{"地点": "", "时间": "", "动作": "", "情绪": ""}},
    "visual_style": "",
    "narrative_function": "",
    "similar_movies": ["片名（年份）- 相似理由"],
    "shot_suggestions": ["镜头1描述", "镜头2描述"],
    "keywords": {{"zh": [], "en": []}}
}}
"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 2000,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )

                result = response.json()
                content = result["content"][0]["text"]

                # 解析JSON
                try:
                    return json.loads(content)
                except:
                    # 如果解析失败，返回结构化文本
                    return {
                        "scene_elements": [query],
                        "visual_style": "请参考详细分析",
                        "similar_movies": [],
                        "analysis": content,
                        "keywords": {"zh": [query], "en": [query]},
                    }
        except Exception as e:
            print(f"Claude调用失败: {e}")
            # 降级到简单返回
            return {
                "scene_elements": [query],
                "visual_style": "待分析",
                "similar_movies": [],
                "keywords": {"zh": [query], "en": [query]},
            }

    async def rank_scenes(
        self, query: str, candidates: List[Dict[str, Any]], top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        使用Claude智能排序候选结果

        优势：更深入的语义理解，更准确的匹配判断
        """
        if not candidates:
            return []

        # 构建评估prompt
        candidates_text = "\n\n".join(
            [
                f"[{i + 1}] {c.get('title', '未知')} ({c.get('year', '未知')})\n"
                f"    简介: {c.get('summary', c.get('description', '无'))[:200]}..."
                for i, c in enumerate(candidates[:15])
            ]
        )

        prompt = f"""用户想找的场景: "{query}"

候选影片:
{candidates_text}

请评估每个候选与用户场景的匹配度。考虑：
1. 场景描述的相似性
2. 视觉风格的匹配
3. 情绪氛围的一致
4. 叙事功能的相似

输出JSON数组:
[
    {{
        "index": 1,
        "relevance_score": 85,
        "explanation": "详细解释为什么匹配",
        "scene_match": "具体匹配的scene描述",
        "visual_match": "视觉风格匹配度"
    }},
    ...
]

评分标准:
- 90-100: 完美匹配，强烈推荐
- 75-89: 高度相关，值得参考  
- 60-74: 有一定参考价值
- <60: 不太相关
"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 2000,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )

                result = response.json()
                content = result["content"][0]["text"]

                # 解析JSON
                try:
                    rankings = json.loads(content)

                    # 合并评分到原数据
                    for rank in rankings:
                        idx = rank.get("index", 0) - 1
                        if 0 <= idx < len(candidates):
                            candidates[idx]["relevance_score"] = rank.get(
                                "relevance_score", 50
                            )
                            candidates[idx]["explanation"] = rank.get("explanation", "")
                            candidates[idx]["scene_match"] = rank.get("scene_match", "")
                            candidates[idx]["visual_match"] = rank.get(
                                "visual_match", ""
                            )

                    # 排序
                    candidates.sort(
                        key=lambda x: x.get("relevance_score", 0), reverse=True
                    )
                    return candidates[:top_k]
                except:
                    # 降级排序
                    candidates.sort(key=lambda x: x.get("year", 0), reverse=True)
                    return candidates[:top_k]

        except Exception as e:
            print(f"Claude排序失败: {e}")
            # 降级排序
            candidates.sort(key=lambda x: x.get("year", 0), reverse=True)
            return candidates[:top_k]

    async def analyze_image_relevance(
        self, scene_description: str, image_url: str
    ) -> Dict[str, Any]:
        """
        Claude 3.5 Sonnet不支持图片分析

        如果需要图片分析，请使用Gemini或GPT-4V
        """
        return {
            "relevance_score": 50,
            "explanation": "Claude 3.5 Sonnet不支持图片分析，请使用Gemini Vision",
            "visual_elements": [],
            "mood_match": "未知",
            "visual_style": "未知",
        }

    # A模块专用方法
    async def parse_script(self, script_content: str) -> Dict[str, Any]:
        """
        解析剧本内容（A模块核心功能）

        使用Claude的长文本能力解析剧本
        """
        prompt = f"""你是一位专业编剧，请解析以下剧本内容。

剧本内容：
{script_content[:8000]}  # 限制长度，避免超长

请提取：
1. 剧本基本信息（标题、类型、风格）
2. 所有场景列表（场景编号、地点、时间、场景描述）
3. 主要角色列表
4. 剧情结构分析（开端、发展、高潮、结局）

输出JSON格式。
"""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 4000,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )

                result = response.json()
                content = result["content"][0]["text"]

                try:
                    return json.loads(content)
                except:
                    return {"raw_analysis": content}
        except Exception as e:
            return {"error": str(e)}

    async def generate_shots(self, scene_description: str) -> List[Dict[str, Any]]:
        """
        为场景生成分镜（A模块功能）

        Claude的创意写作能力在这里发挥优势
        """
        prompt = f"""你是一位专业分镜师，请为以下场景设计分镜。

场景描述：{scene_description}

请设计5-8个分镜，每个包含：
1. 镜头编号
2. 镜头类型（特写/中景/全景/运动镜头等）
3. 画面描述
4. 镜头运动
5. 时长建议
6. 声音/音效建议

输出JSON数组格式。
"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 2000,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )

                result = response.json()
                content = result["content"][0]["text"]

                try:
                    return json.loads(content)
                except:
                    return [{"description": content}]
        except Exception as e:
            return [{"error": str(e)}]
