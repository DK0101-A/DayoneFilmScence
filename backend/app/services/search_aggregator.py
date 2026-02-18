"""
多源搜索聚合服务
聚合豆瓣、百度等多个数据源的搜索结果

设计理念：
- 并行搜索提高效率
- 统一数据格式便于处理
- 可插拔的数据源架构
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """统一搜索结果格式"""

    title: str
    original_title: Optional[str]
    year: Optional[str]
    rating: float
    images: Dict[str, str]
    summary: str
    source: str  # douban, baidu, tmdb等
    url: Optional[str]
    metadata: Dict[str, Any]  # 额外元数据


class DoubanSearchService:
    """
    豆瓣电影搜索服务

    数据源：豆瓣公开API
    特点：华语影视数据丰富，有评分和简介
    限制：有频率限制，需要控制调用频率
    """

    BASE_URL = "https://api.douban.com/v2/movie"

    async def search(
        self, keywords: List[str], limit: int = 10, api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索豆瓣电影

        Args:
            keywords: 搜索关键词列表
            limit: 每个关键词返回数量
            api_key: 豆瓣API Key（可选，公开API有限额）

        Returns:
            搜索结果列表
        """
        results = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            for keyword in keywords[:3]:  # 最多3个关键词，控制API调用
                try:
                    params = {
                        "q": keyword,
                        "count": min(limit, 10),  # 豆瓣限制
                    }

                    if api_key:
                        params["apikey"] = api_key

                    response = await client.get(
                        f"{self.BASE_URL}/search", params=params
                    )

                    if response.status_code == 200:
                        data = response.json()

                        for movie in data.get("subjects", []):
                            results.append(
                                {
                                    "title": movie.get("title", ""),
                                    "original_title": movie.get("original_title", ""),
                                    "year": movie.get("year", ""),
                                    "rating": movie.get("rating", {}).get("average", 0),
                                    "images": movie.get("images", {}),
                                    "summary": movie.get("summary", "")[:300],
                                    "source": "douban",
                                    "url": movie.get("alt", ""),
                                    "type": movie.get("subtype", "movie"),
                                    "genres": movie.get("genres", []),
                                    "casts": movie.get("casts", []),
                                    "directors": movie.get("directors", []),
                                }
                            )
                    elif response.status_code == 403:
                        print(f"豆瓣API限频或需要认证: {response.text}")
                        break
                    else:
                        print(f"豆瓣API错误: {response.status_code}")

                except httpx.TimeoutException:
                    print(f"豆瓣搜索超时: {keyword}")
                    continue
                except Exception as e:
                    print(f"豆瓣搜索失败 '{keyword}': {e}")
                    continue

                # 短暂延迟，避免触发限频
                await asyncio.sleep(0.5)

        return results


class MockSearchService:
    """
    模拟搜索服务（用于测试）

    当真实API不可用时，返回模拟数据
    """

    MOCK_DATA = [
        {
            "title": "盗梦空间",
            "original_title": "Inception",
            "year": "2010",
            "rating": 9.3,
            "images": {
                "large": "https://img9.doubanio.com/view/photo/s_ratio_poster/public/p513344864.jpg"
            },
            "summary": "道姆·柯布是一位经验老道的窃贼...",
            "source": "mock",
            "url": "https://movie.douban.com/subject/3541415/",
        },
        {
            "title": "银翼杀手2049",
            "original_title": "Blade Runner 2049",
            "year": "2017",
            "rating": 8.3,
            "images": {
                "large": "https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2614988097.jpg"
            },
            "summary": "故事发生在大断电30年后...",
            "source": "mock",
            "url": "https://movie.douban.com/subject/10512661/",
        },
        {
            "title": "亡命驾驶",
            "original_title": "Drive",
            "year": "2011",
            "rating": 7.4,
            "images": {},
            "summary": "黑夜里，他协助黑帮分子抢劫...",
            "source": "mock",
            "url": "https://movie.douban.com/subject/3731580/",
        },
    ]

    async def search(
        self, keywords: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """返回模拟数据"""
        import random

        # 随机打乱，模拟不同结果
        results = self.MOCK_DATA.copy()
        random.shuffle(results)
        return results[:limit]


class SearchAggregator:
    """
    搜索聚合器

    聚合多个数据源的搜索结果，去重，统一格式
    """

    def __init__(
        self,
        use_douban: bool = True,
        use_mock: bool = False,
        douban_api_key: Optional[str] = None,
    ):
        """
        初始化搜索聚合器

        Args:
            use_douban: 是否使用豆瓣搜索
            use_mock: 是否使用模拟数据（测试用）
            douban_api_key: 豆瓣API Key
        """
        self.douban = DoubanSearchService() if use_douban else None
        self.mock = MockSearchService() if use_mock else None
        self.douban_api_key = douban_api_key

    async def search_all(
        self,
        keywords_zh: List[str],
        keywords_en: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        并行搜索多个数据源

        Args:
            keywords_zh: 中文关键词
            keywords_en: 英文关键词（可选）
            limit: 总返回数量限制

        Returns:
            合并去重后的搜索结果
        """
        tasks = []

        # 豆瓣搜索（中文）
        if self.douban:
            tasks.append(
                self.douban.search(
                    keywords_zh, limit=limit, api_key=self.douban_api_key
                )
            )

        # 模拟数据（测试用）
        if self.mock:
            tasks.append(self.mock.search(keywords_zh, limit))

        # 并行执行
        if not tasks:
            return []

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        all_results = []
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
            elif isinstance(result, Exception):
                print(f"搜索任务失败: {result}")

        # 去重（基于片名+年份）
        seen = set()
        unique_results = []
        for item in all_results:
            key = f"{item.get('title', '')}_{item.get('year', '')}"
            if key not in seen and key != "_":
                seen.add(key)
                unique_results.append(item)

        return unique_results
