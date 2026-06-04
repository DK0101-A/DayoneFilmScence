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
from app.services.timestamp_service import get_timestamp_service

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
    content_type: Optional[str] = Field(
        default=None,
        description="内容类型：movie(电影)/tv(电视剧)/any(不限)",
        examples=["movie", "tv", "any"],
    )
    region: Optional[str] = Field(
        default=None,
        description="地区筛选：韩剧/日剧/国产/美剧",
        examples=["韩剧", "日剧", "国产", "美剧"],
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
    content_type: Optional[str] = Field(None, description="内容类型: movie/tv")


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
        provider_name = settings.AI_PROVIDER
        api_key = None
        model = settings.AI_MODEL

        # 处理不同提供商的API Key
        if provider_name == "apiyi":
            api_key = settings.OPENAI_API_KEY or settings.APIYI_API_KEY
            model = settings.AI_MODEL  # 使用配置中的模型
        else:
            api_key = getattr(settings, f"{provider_name.upper()}_API_KEY", None)

        # 2. 智能关键词提取（从场景描述中提取关键词）
        query = request.query

        # 简单的关键词提取（不调用AI）
        zh_keywords = [query]
        en_keywords = [query]

        # 中文场景词映射到电影/视频关键词（更精准）
        scene_to_genre = {
            "飙车": ["速度与激情", "飙车", "赛车", "飞车"],
            "追车": ["速度与激情", "追车", "飙车", "赛车"],
            "浪漫": ["爱情", "浪漫", "表白"],
            "表白": ["爱情", "表白", "告白"],
            "吻戏": ["接吻", "吻戏", "爱情"],
            "战斗": ["动作", "战斗", "打架"],
            "科幻": ["科幻", "科幻片"],
            "恐怖": ["恐怖", "惊悚"],
            "搞笑": ["喜剧", "搞笑"],
            "雨夜": ["速度与激情", "飙车", "雨夜"],
            "赛车": ["速度与激情", "赛车", "赛车电影"],
            "追逐": ["追逐", "飙车", "追车"],
            "动作": ["动作", "打斗"],
            "爱情": ["爱情", "爱情片"],
        }

        # 添加相关关键词
        for key, values in scene_to_genre.items():
            if key in query:
                zh_keywords.extend(values)

        # 翻译常用词
        en_translate = {
            "飙车": "car chase",
            "追车": "car chase",
            "浪漫": "romance",
            "表白": "confession love",
            "吻戏": "kissing scene",
            "战斗": "action battle",
            "科幻": "sci-fi",
            "恐怖": "horror",
            "搞笑": "comedy funny",
            "雨夜": "rainy night",
            "赛车": "racing car",
            "追逐": "chase action",
        }

        for key, value in en_translate.items():
            if key in query:
                en_keywords.append(value)

        # 去重
        zh_keywords = list(set(zh_keywords))[:5]
        en_keywords = list(set(en_keywords))[:5]

        understanding = {
            "keywords": {"zh": zh_keywords, "en": en_keywords},
            "mood": "分析中",
            "scene_elements": [],
            "similar_movies": [],
            "visual_style": "",
        }
        keywords_zh = zh_keywords
        keywords_en = en_keywords

        # 3. 多源搜索（全球）
        aggregator = SearchAggregator(
            use_douban=True,
            use_tmdb=True,
            use_bilibili=True,  # B站已集成
            use_youtube=True,
            use_uuuka=True,  # Uuuka短剧API
            use_mock=False,
            douban_api_key=settings.DOUBAN_API_KEY,
            tmdb_api_key=settings.TMDB_API_KEY,
            youtube_api_key=settings.YOUTUBE_API_KEY,
            content_type=request.content_type,  # 电影/电视剧/不限
            region=request.region,  # 韩剧/日剧/国产
        )

        raw_results = await aggregator.search_all(
            keywords_zh=keywords_zh,
            keywords_en=keywords_en,
            limit=request.limit * 2,
        )

        # Debug: print sources
        print(f"API收到结果数: {len(raw_results)}")
        sources_debug = {}
        for r in raw_results:
            src = r.get("source", "unknown")
            sources_debug[src] = sources_debug.get(src, 0) + 1
        print(f"原始结果来源: {sources_debug}")

        # Check first few results
        for i, r in enumerate(raw_results[:3]):
            print(f"  Result {i}: [{r.get('source')}] {r.get('title', '')[:30]}")

        # 4. 直接使用原始结果（跳过AI排序）
        ranked_results = raw_results[: request.limit]

        print(f"返回结果数: {len(ranked_results)}")

        # 5. 为每个结果添加时间戳信息
        ts_service = get_timestamp_service()
        for r in ranked_results:
            title = r.get("title", "")
            source = r.get("source", "")
            url = r.get("url", "")

            # 查询已有时间戳
            best_ts = await ts_service.get_best_timestamp(
                title=title, source=source, url=url, scene_keyword=request.query
            )

            if best_ts:
                r["timestamp"] = best_ts.get("time", "")
                r["timestamp_note"] = best_ts.get("description", "")
                r["timestamp_type"] = best_ts.get("type", "")
                r["timestamp_votes"] = best_ts.get("votes", 0)
            else:
                # AI推断时间戳（仅对电影/电视剧）
                if source in ["tmdb", "douban"]:
                    ai_ts = await ts_service.add_ai_timestamp(
                        title=title,
                        source=source,
                        url=url,
                        scene_description=request.query,
                    )
                    if ai_ts:
                        r["timestamp"] = ai_ts.get("time", "")
                        r["timestamp_note"] = ai_ts.get("description", "")
                        r["timestamp_type"] = "ai"
                        r["timestamp_votes"] = 0

        # 6. 构建响应
        search_time = time.time() - start_time

        # 获取实际使用的模型名
        ai_model = settings.AI_MODEL

        return SearchResponse(
            query=request.query,
            ai_understanding=understanding,
            results=ranked_results,
            total_found=len(raw_results),
            search_time=round(search_time, 2),
            ai_provider="apiyi",
            ai_model=ai_model,
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


# ============== 时间戳API ==============


class TimestampRequest(BaseModel):
    """时间戳标注请求"""

    title: str = Field(..., description="影视名称")
    source: str = Field(..., description="数据来源 (tmdb/douban/youtube)")
    url: str = Field(default="", description="详情链接")
    time: str = Field(..., description="时间戳 (如 45:30 或 00:45:30)")
    description: str = Field(..., description="场景描述")
    user_id: str = Field(default="anonymous", description="用户ID")


class TimestampResponse(BaseModel):
    """时间戳响应"""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post(
    "/timestamp",
    response_model=TimestampResponse,
    summary="添加时间戳标注",
    description="用户为影视场景添加时间戳标注",
)
async def add_timestamp(request: TimestampRequest):
    """
    添加时间戳标注

    用户可以标注影视中特定场景的时间点
    """
    try:
        ts_service = get_timestamp_service()
        result = await ts_service.add_timestamp(
            title=request.title,
            source=request.source,
            url=request.url,
            time_str=request.time,
            description=request.description,
            user_id=request.user_id,
            timestamp_type="user",
        )
        return TimestampResponse(
            success=True,
            message="时间戳添加成功",
            data=result,
        )
    except Exception as e:
        return TimestampResponse(
            success=False,
            message=f"添加失败: {str(e)}",
        )


@router.get(
    "/timestamp",
    summary="获取时间戳列表",
    description="获取指定影视的所有时间戳标注",
)
async def get_timestamps(
    title: str = Query(..., description="影视名称"),
    source: str = Query(..., description="数据来源"),
    url: str = Query(default="", description="详情链接"),
):
    """
    获取时间戳列表

    返回该影视的所有时间戳标注（按投票数排序）
    """
    ts_service = get_timestamp_service()
    timestamps = await ts_service.get_timestamps(title, source, url)
    return {
        "success": True,
        "title": title,
        "source": source,
        "timestamps": timestamps,
        "total": len(timestamps),
    }


@router.post(
    "/timestamp/vote",
    summary="为时间戳投票",
    description="为时间戳点赞或踩",
)
async def vote_timestamp(
    title: str = Query(..., description="影视名称"),
    source: str = Query(..., description="数据来源"),
    url: str = Query(default="", description="详情链接"),
    timestamp_id: str = Query(..., description="时间戳ID"),
    vote: int = Query(default=1, description="投票值 (+1 或 -1)"),
):
    """
    为时间戳投票

    用户可以为自己认为准确的时间戳点赞
    """
    ts_service = get_timestamp_service()
    success = await ts_service.vote_timestamp(title, source, url, timestamp_id, vote)

    if success:
        return {"success": True, "message": "投票成功"}
    else:
        return {"success": False, "message": "时间戳不存在"}
