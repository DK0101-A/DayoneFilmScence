# 🎬 Day One Film AI - 第一阶段实施计划（修订版）

> **核心调整**: B模块不建数据库，改用AI实时全网搜索  
> **优势**: 零数据成本、快速启动、全网覆盖  
> **时间**: 2周完成B模块 → 1周A模块 → 1周合并

---

## 🎯 B模块新架构：AI驱动实时搜索

### 为什么不自建数据库？

| 维度 | 自建数据库 | AI实时搜索 |
|------|-----------|-----------|
| **启动时间** | 1-2月数据准备 | 1周即可上线 |
| **数据覆盖** | 有限（需手动录入） | 全网实时 |
| **维护成本** | 高（持续更新） | 低（AI自动） |
| **精准度** | 高（结构化数据） | 中（依赖AI理解） |
| **成本** | 服务器+人力 | API调用费 |

**MVP阶段选择AI实时搜索，验证需求后再考虑自建库优化**

---

## 🔍 B模块技术方案

### 核心流程
```
用户输入场景描述
    ↓
[AI理解层] - 豆包大模型
  ├── 提取核心场景要素
  ├── 生成多语言搜索关键词
  └── 判断场景类型（动作/对话/氛围）
    ↓
[多源搜索层] - 并行API调用
  ├── 豆瓣API - 搜剧情/片名
  ├── 百度搜索 - 搜剧照/图片
  ├── YouTube API - 搜视频片段
  └── Bing搜索 - 补充结果
    ↓
[AI筛选层] - 智能排序
  ├── 相关性评分
  ├── 去重处理
  └── 格式标准化
    ↓
[结果输出]
  ├── 剧照/截图
  ├── 片名 + 年份
  ├── 场景描述匹配度
  └── 视频链接（如有）
```

### AI提示词设计

#### 1. 场景理解Prompt
```python
SCENE_UNDERSTANDING_PROMPT = """
你是一位资深影视导演，擅长理解场景描述并提取关键要素。

用户场景描述: {user_query}

请分析并输出:
1. 核心场景要素（地点、动作、情绪）
2. 推荐搜索关键词（中文3个 + 英文3个）
3. 场景类型标签（动作/对话/氛围/特效）
4. 相似影片推荐（用于参考）

输出JSON格式:
{
    "core_elements": ["雨夜", "追车", "紧张"],
    "search_keywords": {
        "zh": ["雨夜 追车 电影", "雨天 汽车追逐 片段", "夜间 追车 影视"],
        "en": ["rainy night car chase scene", "night chase movie clip", "rain car pursuit film"]
    },
    "scene_type": "action",
    "similar_films": ["《盗梦空间》", "《疾速追杀》"]
}
"""
```

#### 2. 结果筛选Prompt
```python
RESULT_RANKING_PROMPT = """
你是一位影视选景专家，需要判断搜索结果与用户场景的匹配度。

用户场景: {user_query}

候选结果:
{search_results}

请对每个结果评分（0-100），并说明理由。
重点关注:
- 场景相似度（40分）
- 视觉氛围（30分）
- 影片知名度（20分）
- 可获取性（10分）

输出JSON数组，按分数降序排列。
"""
```

---

## 🛠️ Week 1: B模块核心开发（AI实时搜索版）

### Day 1: 项目初始化
```bash
# 创建项目结构
mkdir -p /backend/app/{api,services,models,utils}
mkdir -p /backend/tests

# 核心依赖（精简版）
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2  # 异步HTTP请求
python-dotenv==1.0.0
pydantic==2.5.0
```

**依赖说明**:
- 不需要SQLAlchemy（无数据库）
- 不需要Milvus（无向量库）
- 只需要HTTP客户端调用API

---

### Day 2: AI服务层开发

#### 核心服务: AI理解服务
```python
# app/services/ai_understanding.py

import httpx
from typing import List, Dict
import json

class AISceneUnderstanding:
    """AI场景理解服务 - 使用豆包API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.doubao.com/v1"
    
    async def understand_scene(self, query: str) -> Dict:
        """
        理解用户场景描述
        
        Returns:
            {
                "core_elements": [...],
                "search_keywords": {"zh": [...], "en": [...]},
                "scene_type": "...",
                "similar_films": [...]
            }
        """
        prompt = f"""
        分析影视场景: {query}
        
        输出JSON格式:
        {{
            "core_elements": ["关键词1", "关键词2"],
            "search_keywords": {{
                "zh": ["中文搜索词1", "中文搜索词2"],
                "en": ["english keyword1", "english keyword2"]
            }},
            "scene_type": "action/dialogue/atmosphere",
            "similar_films": ["《影片名1》", "《影片名2》"]
        }}
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "doubao-lite",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 解析JSON
            try:
                return json.loads(content)
            except:
                return self._parse_with_fallback(content)
```

#### 核心服务: 搜索聚合服务
```python
# app/services/search_aggregator.py

import asyncio
import httpx
from typing import List, Dict

class SearchAggregator:
    """多源搜索聚合服务"""
    
    def __init__(self):
        self.douban_api = DoubanSearchService()
        self.baidu_api = BaiduSearchService()
        self.youtube_api = YouTubeSearchService()
    
    async def search_all(
        self, 
        keywords: Dict[str, List[str]],
        filters: Dict
    ) -> List[Dict]:
        """
        并行搜索多个数据源
        
        Args:
            keywords: {"zh": [...], "en": [...]}
            filters: {"year": ..., "region": ..., "genre": ...}
        """
        # 并行发起搜索
        tasks = [
            self.douban_api.search(keywords["zh"], filters),
            self.baidu_api.search_images(keywords["zh"]),
            # YouTube暂时注释，需要翻墙
            # self.youtube_api.search(keywords["en"]),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        all_results = []
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
        
        return all_results
```

#### 数据源适配器
```python
# app/services/douban_service.py

class DoubanSearchService:
    """豆瓣电影搜索"""
    
    async def search(self, keywords: List[str], filters: Dict) -> List[Dict]:
        """
        搜索豆瓣电影
        
        注意: 豆瓣API有频率限制，需要缓存
        """
        results = []
        
        for keyword in keywords[:2]:  # 限制搜索次数
            try:
                # 使用豆瓣公开API或网页抓取
                url = f"https://api.douban.com/v2/movie/search?q={keyword}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=10.0)
                    data = response.json()
                    
                    for movie in data.get("subjects", [])[:5]:
                        results.append({
                            "source": "douban",
                            "title": movie["title"],
                            "original_title": movie.get("original_title", ""),
                            "year": movie.get("year", ""),
                            "rating": movie.get("rating", {}).get("average", 0),
                            "images": movie.get("images", {}),
                            "url": movie.get("alt", ""),
                            "type": "movie"
                        })
            except Exception as e:
                print(f"豆瓣搜索失败: {e}")
                continue
        
        return results


class BaiduSearchService:
    """百度搜索（图片）"""
    
    async def search_images(self, keywords: List[str]) -> List[Dict]:
        """搜索相关图片"""
        # 使用百度搜索API或第三方服务
        # 这里需要接入百度API
        pass
```

---

### Day 3: AI筛选和排序

```python
# app/services/ai_ranking.py

class AIRankingService:
    """AI结果排序服务"""
    
    def __init__(self, ai_service: AISceneUnderstanding):
        self.ai = ai_service
    
    async def rank_results(
        self, 
        user_query: str, 
        candidates: List[Dict]
    ) -> List[Dict]:
        """
        AI智能排序候选结果
        
        策略:
        1. 去除明显不相关的结果
        2. 按场景相似度评分
        3. 返回Top 10-15
        """
        if not candidates:
            return []
        
        # 去重（基于片名）
        seen = set()
        unique = []
        for item in candidates:
            key = item.get("title", "") + str(item.get("year", ""))
            if key not in seen:
                seen.add(key)
                unique.append(item)
        
        # AI评分（批量处理，减少API调用）
        scored = []
        for item in unique[:20]:  # 只评分前20个
            score = await self._calculate_relevance(user_query, item)
            item["relevance_score"] = score
            scored.append(item)
        
        # 按分数排序
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored[:15]  # 返回Top 15
    
    async def _calculate_relevance(self, query: str, item: Dict) -> int:
        """计算单个结果的相关性分数"""
        # 简单规则评分（减少API调用成本）
        score = 50  # 基础分
        
        # 如果有剧照加分
        if item.get("images"):
            score += 20
        
        # 如果有评分加分
        rating = item.get("rating", 0)
        if rating > 8.0:
            score += 15
        elif rating > 7.0:
            score += 10
        
        # 年份越近加分（假设用户想要现代参考）
        year = item.get("year", "")
        if year and int(year) > 2015:
            score += 10
        
        return min(score, 100)
```

---

### Day 4: FastAPI接口开发

```python
# app/api/search.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api", tags=["search"])

class SearchRequest(BaseModel):
    query: str  # 场景描述，如"雨夜追车"
    year_range: Optional[str] = None  # "2010-2020"
    region: Optional[str] = None  # "华语", "欧美", "日韩"
    genre: Optional[str] = None  # "动作", "悬疑"
    limit: int = 10  # 返回结果数量

class SearchResult(BaseModel):
    title: str
    original_title: Optional[str]
    year: Optional[str]
    rating: float
    images: Dict
    scene_description: Optional[str]  # AI生成的场景匹配描述
    relevance_score: int
    source: str  # "douban", "baidu", "youtube"
    url: Optional[str]

class SearchResponse(BaseModel):
    query: str
    ai_understanding: Dict  # AI对场景的理解
    results: List[SearchResult]
    search_time: float  # 搜索耗时


@router.post("/search", response_model=SearchResponse)
async def search_scenes(request: SearchRequest):
    """
    搜索影视场景参考（AI实时搜索版）
    
    **工作流程**:
    1. AI理解用户场景描述
    2. 生成多语言搜索关键词
    3. 并行搜索多个数据源（豆瓣、百度等）
    4. AI筛选和排序结果
    5. 返回结构化的参考列表
    
    **示例**:
    ```json
    {
        "query": "雨夜追车",
        "year_range": "2010-2023",
        "region": "欧美",
        "limit": 10
    }
    ```
    """
    import time
    start_time = time.time()
    
    # 1. AI理解场景
    ai_service = AISceneUnderstanding(api_key=settings.DOUBAO_API_KEY)
    understanding = await ai_service.understand_scene(request.query)
    
    # 2. 多源搜索
    aggregator = SearchAggregator()
    raw_results = await aggregator.search_all(
        keywords=understanding["search_keywords"],
        filters={
            "year": request.year_range,
            "region": request.region,
            "genre": request.genre
        }
    )
    
    # 3. AI排序
    ranking_service = AIRankingService(ai_service)
    ranked_results = await ranking_service.rank_results(
        request.query, 
        raw_results
    )
    
    # 4. 格式化输出
    search_time = time.time() - start_time
    
    return SearchResponse(
        query=request.query,
        ai_understanding=understanding,
        results=ranked_results[:request.limit],
        search_time=round(search_time, 2)
    )
```

---

### Day 5: 扣子Agent配置

**扣子工作流配置**:

1. **用户输入组件**
   - 接收场景描述
   - 可选：年代、地区、类型

2. **HTTP调用组件**
   ```
   URL: https://your-api.com/api/search
   Method: POST
   Body: {
       "query": "{{用户输入}}",
       "limit": 10
   }
   ```

3. **结果展示组件**
   - 显示剧照
   - 显示片名、年份、评分
   - 显示AI匹配说明
   - 提供收藏按钮

4. **提示词模板**:
```
用户说: {{query}}

调用API搜索相关影视场景...

找到 {{results.length}} 个参考场景：

{{#each results}}
🎬 {{title}} ({{year}})
⭐ 评分: {{rating}} | 🎯 匹配度: {{relevance_score}}%
📸 [显示剧照]
{{/each}}

需要查看更多或筛选特定条件吗？
```

---

### Day 6-7: 测试优化

**测试项**:
- [ ] 搜索响应时间 < 5秒
- [ ] AI理解准确性
- [ ] 结果相关性
- [ ] 错误处理（API失败降级）

**优化策略**:
1. **缓存AI理解结果** - 相同查询缓存30分钟
2. **搜索结果缓存** - 缓存1小时
3. **失败降级** - 豆瓣API失败时，只显示百度图片结果
4. **限流保护** - 每秒最多5次搜索

---

## 💰 成本控制

### API费用估算（月度）

| 项目 | 单价 | 月用量 | 月费用 |
|------|------|--------|--------|
| 豆包AI理解 | ¥0.003/次 | 1000次 | ¥3 |
| 豆包结果排序 | ¥0.003/次 | 1000次 | ¥3 |
| 豆瓣API | 免费（有限额） | - | ¥0 |
| 百度图片搜索 | ¥0.001/次 | 2000次 | ¥2 |
| **总计** | - | - | **¥8/月** |

**说明**: 
- 初期用户少，成本极低
- 免费额度足够测试期使用
- 用户增长后可考虑自建数据库优化成本

---

## 🚀 下一步行动

1. **确认方案** - 您review AI实时搜索方案
2. **申请API密钥**:
   - [ ] 豆包大模型API
   - [ ] 豆瓣API（申请开发者权限）
   - [ ] 百度搜索API（可选）
3. **开始Day 1** - 项目初始化

**确认后我们立即开始B模块开发！** 🎬
