# 🎬 Day One Film AI - 第一阶段实施计划（AI Studio快速验证版）

> **策略**: 开发期用AI Studio (Gemini) 快速验证 → 成功后迁移国产大模型  
> **优势**: 1周出MVP，验证效果后再优化  
> **时间**: 2周完成验证版，第3周迁移国产

---

## 🎯 分阶段策略

### Phase 1: 快速验证（AI Studio/Gemini）
**目标**: 1周内跑通B模块，验证核心需求
**工具**: 
- AI Studio（Gemini Pro）- 免费额度足够
- 香港服务器（国内访问）
- 扣子Agent（前端）

**为什么先用Gemini？**
| 维度 | Gemini | 国产模型 |
|------|--------|----------|
| **启动速度** | ⚡ 立即开始 | 需申请审核 |
| **效果验证** | 🎯 最强能力 | 需调优 |
| **免费额度** | ✅ 60次/分钟 | 有限额 |
| **多模态** | ✅ 原生支持 | 部分支持 |

### Phase 2: 迁移优化（国产大模型）
**目标**: 将验证成功的方案迁移到国产模型
**迁移路径**:
```
Gemini代码 ──→ 抽象AI接口层 ──→ 豆包/通义实现
     │              │                │
   验证成功      统一接口         国产合规版
```

---

## 🚀 Week 1: AI Studio快速验证版

### Day 1: 项目初始化 + AI Studio配置

#### 1. 获取AI Studio API Key
```bash
# 步骤1: 访问 https://aistudio.google.com/app/apikey
# 步骤2: 点击"Create API Key"
# 步骤3: 复制Key保存

# 免费额度：
# - Gemini Pro: 60 requests/minute
# - Gemini Pro Vision: 60 requests/minute
# - 足够支撑开发 + 测试 + 100个种子用户
```

#### 2. 项目结构
```bash
mkdir -p /Users/seven/Desktop/v/backend
cd /Users/seven/Desktop/v/backend

# 初始化Python项目
python3 -m venv venv
source venv/bin/activate

# requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
httpx==0.25.2
google-generativeai==0.3.0
pydantic==2.5.0
redis==5.0.1
EOF

pip install -r requirements.txt
```

#### 3. 核心配置
```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # AI Studio / Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_VISION_MODEL: str = "gemini-pro-vision"
    
    # 数据源API
    DOUBAN_API_KEY: str = ""  # 可选，豆瓣有公开API
    
    # 缓存（搜索结果缓存1小时）
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600
    
    # 限流（每秒5次搜索）
    RATE_LIMIT: int = 5
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

---

### Day 2: Gemini场景理解服务

```python
# app/services/gemini_scene_service.py

import google.generativeai as genai
from typing import List, Dict, Optional
import json
import re

class GeminiSceneService:
    """
    Gemini场景理解服务（AI Studio版）
    
    核心能力：
    1. 深度理解场景描述
    2. 生成多语言搜索关键词
    3. 推荐相似影片
    4. 分析剧照相关性（多模态）
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.text_model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
    
    async def understand_scene(self, query: str) -> Dict:
        """
        理解场景描述，提取关键要素
        
        Args:
            query: 用户场景描述，如"雨夜追车"
            
        Returns:
            {
                "scene_elements": ["雨夜", "追车", "紧张"],
                "keywords_zh": ["雨夜 追车 电影", ...],
                "keywords_en": ["rainy night car chase", ...],
                "mood": "紧张刺激",
                "visual_style": "暗调、霓虹反光、高速运动",
                "similar_movies": ["《盗梦空间》", "《亡命驾驶》"],
                "shot_suggestions": ["广角镜头", "车内特写", "雨滴特写"]
            }
        """
        prompt = f"""
你是一位资深影视导演，擅长分析场景描述并提取关键要素。

用户场景描述: "{query}"

请详细分析并输出JSON格式:
{{
    "scene_elements": ["提取的核心视觉元素，如地点、动作、氛围"],
    "keywords_zh": ["3-5个中文搜索关键词，用于搜影视片段"],
    "keywords_en": ["3-5个英文搜索关键词，扩大搜索范围"],
    "mood": "场景的情绪基调（如紧张、浪漫、悬疑）",
    "visual_style": "视觉风格建议（光线、色调、摄影风格）",
    "similar_movies": ["3-5部有相似场景的著名电影，中文片名"],
    "shot_suggestions": ["建议的镜头类型（如广角、特写、跟拍）"]
}}

只输出JSON，不要有其他文字。
"""
        
        try:
            response = await self.text_model.generate_content_async(prompt)
            content = response.text
            
            # 清理可能的Markdown代码块
            content = re.sub(r'```json\n?', '', content)
            content = re.sub(r'\n?```', '', content)
            
            return json.loads(content)
        except Exception as e:
            print(f"Gemini解析失败: {e}")
            # 降级返回基础结构
            return {
                "scene_elements": [query],
                "keywords_zh": [f"{query} 电影", f"{query} 片段"],
                "keywords_en": [query.replace(" ", " ")],
                "mood": "未知",
                "visual_style": "待分析",
                "similar_movies": [],
                "shot_suggestions": []
            }
    
    async def rank_scenes(
        self, 
        query: str, 
        candidates: List[Dict],
        top_k: int = 10
    ) -> List[Dict]:
        """
        AI智能排序候选结果
        
        Args:
            query: 原始查询
            candidates: 候选结果列表
            top_k: 返回前K个
            
        Returns:
            按相关性排序的结果，每个带score和explanation
        """
        if not candidates:
            return []
        
        # 构建评估prompt
        candidates_text = "\n\n".join([
            f"[{i+1}] {c.get('title', '未知')} ({c.get('year', '未知')})\n"
            f"    简介: {c.get('summary', '无')[:100]}..."
            for i, c in enumerate(candidates[:20])  # 最多评估20个
        ])
        
        prompt = f"""
用户想找的场景: "{query}"

候选影片:
{candidates_text}

请评估每个候选与用户场景的匹配度，输出JSON数组:
[
    {{
        "index": 1,
        "relevance_score": 85,
        "explanation": "为什么匹配，如'都有雨夜追车的紧张氛围'",
        "scene_match": "具体匹配的 scene 描述"
    }},
    ...
]

评分标准:
- 90-100: 完美匹配，强烈推荐
- 70-89: 高度相关，值得参考
- 50-69: 有一定参考价值
- <50: 不太相关

只输出JSON数组。
"""
        
        try:
            response = await self.text_model.generate_content_async(prompt)
            content = response.text
            content = re.sub(r'```json\n?', '', content)
            content = re.sub(r'\n?```', '', content)
            
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
```

---

### Day 3: 多源搜索聚合

```python
# app/services/search_aggregator.py

import httpx
import asyncio
from typing import List, Dict, Optional

class DoubanSearchService:
    """豆瓣电影搜索服务"""
    
    async def search(
        self, 
        keywords: List[str], 
        limit: int = 10
    ) -> List[Dict]:
        """
        搜索豆瓣电影
        
        注意：使用豆瓣公开API，有频率限制
        """
        results = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for keyword in keywords[:3]:  # 最多3个关键词
                try:
                    # 豆瓣搜索API（公开）
                    url = f"https://api.douban.com/v2/movie/search"
                    params = {
                        "q": keyword,
                        "count": limit
                    }
                    
                    response = await client.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for movie in data.get("subjects", []):
                            results.append({
                                "source": "douban",
                                "title": movie.get("title", ""),
                                "original_title": movie.get("original_title", ""),
                                "year": movie.get("year", ""),
                                "rating": movie.get("rating", {}).get("average", 0),
                                "images": movie.get("images", {}),
                                "summary": movie.get("summary", "")[:200],
                                "url": movie.get("alt", ""),
                                "type": "movie"
                            })
                            
                except Exception as e:
                    print(f"豆瓣搜索失败 '{keyword}': {e}")
                    continue
        
        return results


class SearchAggregator:
    """搜索聚合服务"""
    
    def __init__(self):
        self.douban = DoubanSearchService()
        # 可以扩展更多源：IMDb, TMDB等
    
    async def search_all(
        self, 
        keywords_zh: List[str],
        keywords_en: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        并行搜索多个数据源
        
        Returns:
            合并去重后的结果列表
        """
        # 并行发起搜索
        tasks = [
            self.douban.search(keywords_zh, limit),
            # self.tmdb.search(keywords_en or keywords_zh, limit),
            # self.imdb.search(keywords_en or [], limit),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        all_results = []
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
        
        # 去重（基于片名+年份）
        seen = set()
        unique_results = []
        for item in all_results:
            key = f"{item.get('title', '')}_{item.get('year', '')}"
            if key not in seen and key != "_":
                seen.add(key)
                unique_results.append(item)
        
        return unique_results
```

---

### Day 4: FastAPI接口开发

```python
# app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time

from app.config import settings
from app.services.gemini_scene_service import GeminiSceneService
from app.services.search_aggregator import SearchAggregator

app = FastAPI(
    title="Day One Film AI - Scene Search API",
    description="影视场景参考搜索API（AI Studio快速验证版）",
    version="0.1.0"
)

# CORS配置（允许扣子调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
gemini_service = GeminiSceneService(settings.GEMINI_API_KEY)
search_aggregator = SearchAggregator()


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    year_from: Optional[int] = None
    year_to: Optional[int] = None


class SceneResult(BaseModel):
    title: str
    original_title: Optional[str]
    year: Optional[str]
    rating: float
    images: Dict
    relevance_score: int
    explanation: Optional[str]
    source: str
    url: Optional[str]


class SearchResponse(BaseModel):
    query: str
    ai_understanding: Dict
    results: List[SceneResult]
    total_found: int
    search_time: float
    ai_model: str = "gemini-pro"


@app.post("/api/search", response_model=SearchResponse)
async def search_scenes(request: SearchRequest):
    """
    搜索影视场景参考（AI Studio版）
    
    **工作流程**:
    1. Gemini深度理解场景描述
    2. 生成中英文搜索关键词
    3. 多源搜索（豆瓣等）
    4. AI智能排序结果
    5. 返回结构化参考
    
    **示例**:
    ```json
    {
        "query": "雨夜追车",
        "limit": 10
    }
    ```
    
    **返回**:
    - ai_understanding: AI对场景的理解分析
    - results: 排序后的参考场景列表
    - relevance_score: AI匹配的置信度(0-100)
    """
    start_time = time.time()
    
    try:
        # 1. AI理解场景
        understanding = await gemini_service.understand_scene(request.query)
        
        # 2. 多源搜索
        raw_results = await search_aggregator.search_all(
            keywords_zh=understanding.get("keywords_zh", [request.query]),
            keywords_en=understanding.get("keywords_en", []),
            limit=20
        )
        
        # 3. AI排序
        ranked_results = await gemini_service.rank_scenes(
            query=request.query,
            candidates=raw_results,
            top_k=request.limit
        )
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            query=request.query,
            ai_understanding=understanding,
            results=ranked_results,
            total_found=len(raw_results),
            search_time=round(search_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "0.1.0", "ai_model": "gemini-pro"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Day 5-7: 扣子Agent配置 + 测试

#### 扣子工作流配置

**组件1: 用户输入**
```
输入字段:
- scene_description (必填): 场景描述
- limit (可选): 返回数量，默认10
```

**组件2: HTTP调用后端**
```yaml
URL: https://your-server.com/api/search
Method: POST
Headers:
  Content-Type: application/json
Body:
  query: "{{scene_description}}"
  limit: {{limit}}
```

**组件3: 结果展示Prompt**
```
根据搜索结果，为用户展示影视参考：

场景理解: {{ai_understanding.mood}}
视觉风格: {{ai_understanding.visual_style}}
推荐影片: {{ai_understanding.similar_movies}}

找到 {{results.length}} 个参考场景：

{{#each results}}
🎬 {{title}} ({{year}})
⭐ 评分: {{rating}} | 🎯 AI匹配度: {{relevance_score}}%
💡 匹配理由: {{explanation}}
📸 {{#if images.large}}有剧照{{else}}无图片{{/if}}
🔗 [查看详情]({{url}})

{{/each}}

需要查看更多场景，还是筛选特定条件？
```

---

## 📋 迁移计划（第3周）

### 迁移到国产大模型

**步骤1: 抽象AI接口层**
```python
# app/services/ai_interface.py
from abc import ABC, abstractmethod

class AISceneProvider(ABC):
    """AI场景理解抽象接口"""
    
    @abstractmethod
    async def understand_scene(self, query: str) -> Dict:
        pass
    
    @abstractmethod
    async def rank_scenes(self, query: str, candidates: List[Dict]) -> List[Dict]:
        pass


# Gemini实现（已存在）
class GeminiProvider(AISceneProvider):
    ...

# 豆包实现（新增）
class DoubaoProvider(AISceneProvider):
    ...

# 通义实现（新增）
class QwenProvider(AISceneProvider):
    ...
```

**步骤2: 配置切换**
```python
# 通过环境变量切换
AI_PROVIDER=gemini  # 或 doubao / qwen
```

---

## 🎯 本周交付目标

### Week 1结束检查清单
- [ ] AI Studio API Key配置完成
- [ ] `/api/search` 接口可用
- [ ] 扣子Agent能搜索并显示结果
- [ ] 响应时间 < 5秒
- [ ] 用户测试通过（至少5人）

### 成功标准
✅ 输入"雨夜追车"能返回10个相关影视参考  
✅ 每个结果有AI匹配度评分  
✅ 能在豆包里直接使用  

---

## 🚀 立即开始？

**需要我现在就帮您**：

**A) 初始化项目代码** → 我立即创建完整项目结构  
**B) 申请AI Studio Key** → 我出详细步骤  
**C) 部署到服务器** → 我出部署脚本

**建议选A，边写代码边申请Key！**  
**确认后我立即开始Day 1！** 🎬