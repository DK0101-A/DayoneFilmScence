"""
搜索API路由
核心功能：影视场景参考搜索
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time

from app.config import settings
from app.services.ai_interface import AIProviderFactory
from app.services.search_aggregator import SearchAggregator

router = APIRouter(tags=["搜索"])


# ============== 请求/响应模型 ==============


class SearchRequest(BaseModel):
    """搜索请求模型"""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="场景描述，如'雨夜追车'、'办公室争吵'",
        examples=["雨夜追车", "办公室争吵", "医院离别"],
    )
    limit: int = Field(default=10, ge=1, le=20, description="返回结果数量")
    year_from: Optional[int] = Field(
        default=None, ge=1900, le=2030, description="起始年份"
    )
    year_to: Optional[int] = Field(
        default=None, ge=1900, le=2030, description="结束年份"
    )
    region: Optional[str] = Field(
        default=None,
        description="地区筛选：华语/欧美/日韩",
        examples=["华语", "欧美", "日韩"],
    )
    genre: Optional[str] = Field(
        default=None,
        description="类型筛选：动作/爱情/悬疑",
        examples=["动作", "爱情", "悬疑"],
    )


class SceneResult(BaseModel):
    """场景结果模型"""

    title: str = Field(..., description="片名")
    original_title: Optional[str] = Field(None, description="原名")
    year: Optional[str] = Field(None, description="年份")
    rating: float = Field(0.0, description="评分")
    images: Dict[str, Any] = Field(default_factory=dict, description="剧照")
    relevance_score: int = Field(0, description="AI匹配度(0-100)")
    explanation: Optional[str] = Field(None, description="匹配理由")
    scene_match: Optional[str] = Field(None, description="具体匹配场景")
    timestamp: Optional[str] = Field(
        None, description="场景时间戳，如'00:45:30'或'第45分钟'"
    )
    timestamp_note: Optional[str] = Field(
        None, description="时间戳说明，如'开场15分钟'"
    )
    source: str = Field("unknown", description="数据来源")
    url: Optional[str] = Field(None, description="详情链接")


class SearchResponse(BaseModel):
    """搜索响应模型"""

    query: str = Field(..., description="原始查询")
    ai_understanding: Dict[str, Any] = Field(..., description="AI对场景的理解")
    results: List[SceneResult] = Field(..., description="搜索结果")
    total_found: int = Field(0, description="找到的总数")
    search_time: float = Field(0.0, description="搜索耗时(秒)")
    ai_provider: str = Field(..., description="使用的AI提供商")
    ai_model: str = Field(..., description="使用的AI模型")


# ============== API端点 ==============


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="搜索影视场景参考",
    description="""
    搜索与场景描述相似的影视参考片段。
    
    **工作流程**:
    1. AI深度理解场景描述
    2. 生成中英文搜索关键词
    3. 多源搜索（豆瓣等）
    4. AI智能排序结果
    5. 返回结构化的参考列表
    
    **示例**:
    ```json
    {
        "query": "雨夜追车",
        "limit": 10,
        "year_from": 2010,
        "year_to": 2023
    }
    ```
    """,
)
async def search_scenes(request: SearchRequest):
    """
    搜索影视场景参考
    """
    start_time = time.time()

    try:
        # 1. 获取AI提供商
        ai_provider = AIProviderFactory.create(
            settings.AI_PROVIDER,
            api_key=getattr(settings, f"{settings.AI_PROVIDER.upper()}_API_KEY"),
        )

        # 2. AI理解场景
        understanding = await ai_provider.understand_scene(request.query)

        # 3. 多源搜索
        aggregator = SearchAggregator(
            use_douban=True,
            use_mock=True,  # 开发期使用模拟数据
            douban_api_key=settings.DOUBAN_API_KEY,
        )

        raw_results = await aggregator.search_all(
            keywords_zh=understanding.get("keywords_zh", [request.query]),
            keywords_en=understanding.get("keywords_en", []),
            limit=request.limit * 2,  # 多搜一些用于排序
        )

        # 4. AI排序
        ranked_results = await ai_provider.rank_scenes(
            query=request.query, candidates=raw_results, top_k=request.limit
        )

        # 5. 构建响应
        search_time = time.time() - start_time

        return SearchResponse(
            query=request.query,
            ai_understanding=understanding,
            results=ranked_results,
            total_found=len(raw_results),
            search_time=round(search_time, 2),
            ai_provider=ai_provider.provider_name,
            ai_model=settings.GEMINI_MODEL
            if settings.AI_PROVIDER == "gemini"
            else settings.DOUBAO_MODEL,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get(
    "/search/simple",
    summary="简单搜索（GET版本）",
    description="适合扣子直接调用的简单搜索接口",
)
async def search_scenes_simple(
    query: str = Query(..., min_length=1, description="场景描述"),
    limit: int = Query(default=10, ge=1, le=20),
):
    """
    简单搜索接口（GET版本）

    方便扣子Agent直接通过URL参数调用
    """
    request = SearchRequest(query=query, limit=limit)
    return await search_scenes(request)


@router.post(
    "/search/search_scenes",
    response_model=SearchResponse,
    summary="扣子兼容接口",
    description="兼容扣子自动追加工具名的调用方式",
)
async def search_scenes_coze(request: SearchRequest):
    """
    扣子兼容接口

    扣子会自动在URL后追加工具名，此接口兼容该调用方式
    """
    return await search_scenes(request)


@router.get(
    "/search/simple/search_scenes",
    summary="扣子GET兼容接口",
    description="兼容扣子自动追加工具名的GET调用方式",
)
async def search_scenes_simple_coze(
    scene_description: str = Query(..., min_length=1, description="场景描述"),
    limit: int = Query(default=10, ge=1, le=20),
    year_from: Optional[int] = Query(None, description="起始年份"),
    year_to: Optional[int] = Query(None, description="结束年份"),
    region: Optional[str] = Query(None, description="地区：华语/欧美/日韩"),
    genre: Optional[str] = Query(None, description="类型：动作/爱情/悬疑"),
):
    """
    扣子GET兼容接口（支持筛选）

    扣子会自动在URL后追加工具名，此接口兼容该调用方式
    """
    request = SearchRequest(
        query=scene_description,
        limit=limit,
        year_from=year_from,
        year_to=year_to,
        region=region,
        genre=genre,
    )
    return await search_scenes(request)


@router.get(
    "/search/filter",
    summary="带筛选的搜索",
    description="支持年代、地区、类型筛选的高级搜索",
)
async def search_with_filter(
    query: str = Query(..., min_length=1, description="场景描述"),
    limit: int = Query(default=10, ge=1, le=20),
    year_from: Optional[int] = Query(None, ge=1900, le=2030, description="起始年份"),
    year_to: Optional[int] = Query(None, ge=1900, le=2030, description="结束年份"),
    region: Optional[str] = Query(None, description="地区：华语/欧美/日韩/其他"),
    genre: Optional[str] = Query(None, description="类型：动作/爱情/悬疑/喜剧/科幻"),
):
    """
    带筛选的影视场景搜索

    **参数说明**：
    - query: 场景描述（必填）
    - year_from/year_to: 年份范围筛选，如2010-2020
    - region: 地区筛选，可选：华语、欧美、日韩、其他
    - genre: 类型筛选，可选：动作、爱情、悬疑、喜剧、科幻

    **示例**：
    ```
    GET /api/search/filter?query=雨夜追车&year_from=2010&year_to=2020&region=欧美&genre=动作
    ```
    """
    request = SearchRequest(
        query=query,
        limit=limit,
        year_from=year_from,
        year_to=year_to,
        region=region,
        genre=genre,
    )
    return await search_scenes(request)


@router.get(
    "/providers", summary="获取可用AI提供商", description="查看系统支持的所有AI提供商"
)
async def list_providers():
    """列出所有可用的AI提供商"""
    providers = AIProviderFactory.list_providers()
    return {
        "providers": providers,
        "current": settings.AI_PROVIDER,
        "available": [
            {
                "name": "gemini",
                "description": "Google Gemini (开发期推荐)",
                "capabilities": ["text", "image", "multilingual"],
            },
            {
                "name": "doubao",
                "description": "字节豆包 (生产环境)",
                "capabilities": ["text", "chinese"],
            },
        ],
    }
