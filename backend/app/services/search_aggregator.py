"""
多源搜索聚合服务 - 豆瓣、TMDB、B站、YouTube、Uuuka短剧
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional


class UuukaService:
    """Uuuka 短剧/影视搜索 - https://api.uuuka.com"""

    BASE_URL = "https://api.uuuka.com"

    # 支持的内容类型映射
    CONTENT_TYPES = {
        "post": "短剧",
        "dongman": "动漫",
        "movie": "电影",
        "tv": "电视剧",
        "xuexi": "学习资源",
        "baidu": "百度短剧",
    }

    async def search(
        self, keywords: List[str], limit: int = 10, content_type: str = None
    ) -> List[Dict[str, Any]]:
        """搜索短剧/影视内容"""
        results = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            for kw in keywords[:3]:
                try:
                    # 构建搜索请求
                    params = {
                        "keyword": kw,
                        "page": 1,
                        "limit": limit,
                    }
                    if content_type:
                        params["content_type"] = content_type

                    resp = await client.get(
                        f"{self.BASE_URL}/api/search", params=params
                    )

                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("success"):
                            for item in data.get("data", {}).get("items", []):
                                results.append(
                                    {
                                        "title": item.get("title", ""),
                                        "original_title": item.get("title", ""),
                                        "year": (item.get("update_time") or "")[:4],
                                        "rating": 0,
                                        "images": {"large": ""},
                                        "summary": f"类型: {self.CONTENT_TYPES.get(item.get('type'), item.get('type', '未知'))}",
                                        "source": "uuuka",
                                        "url": item.get("source_link", ""),
                                        "type": item.get("type", "post"),
                                        "update_time": item.get("update_time", ""),
                                    }
                                )
                except Exception as e:
                    print(f"Uuuka 搜索失败: {e}")

        return results

    async def get_today_updates(
        self, content_type: str = "post", limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取今日更新的内容"""
        results = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/api/contents/{content_type}",
                    params={"today": "today", "page": 1, "limit": limit},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        for item in data.get("data", {}).get("items", []):
                            results.append(
                                {
                                    "title": item.get("title", ""),
                                    "source": "uuuka",
                                    "url": item.get("source_link", ""),
                                    "type": item.get("type", "post"),
                                    "update_time": item.get("update_time", ""),
                                }
                            )
            except Exception as e:
                print(f"Uuuka 今日更新获取失败: {e}")

        return results


class TMDBService:
    """TMDB 全球影视搜索"""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or "f672ffda3674c8b94c955ab9804ca4b1"
        self.image_base = "https://image.tmdb.org/t/p/w500"

    async def search(
        self, keywords: List[str], limit: int = 10, region: str = None
    ) -> List[Dict[str, Any]]:
        results = []
        region_map = {
            "韩剧": "KR",
            "韩": "KR",
            "日剧": "JP",
            "日": "JP",
            "国产": "CN",
            "美剧": "US",
        }
        region_code = region_map.get(region, region) if region else None

        async with httpx.AsyncClient(timeout=15.0) as client:
            for kw in keywords[:2]:
                # 电影
                try:
                    params = {"api_key": self.api_key, "query": kw, "language": "zh-CN"}
                    if region_code:
                        params["region"] = region_code
                    resp = await client.get(
                        f"{self.BASE_URL}/search/movie", params=params
                    )
                    if resp.status_code == 200:
                        for m in resp.json().get("results", [])[:limit]:
                            results.append(
                                {
                                    "title": m.get("title", ""),
                                    "original_title": m.get("original_title", ""),
                                    "year": (m.get("release_date") or "")[:4],
                                    "rating": m.get("vote_average", 0),
                                    "images": {
                                        "large": f"{self.image_base}{m.get('poster_path')}"
                                        if m.get("poster_path")
                                        else ""
                                    },
                                    "summary": m.get("overview", "")[:200],
                                    "source": "tmdb",
                                    "url": f"https://www.themoviedb.org/movie/{m.get('id')}",
                                    "type": "movie",
                                }
                            )
                except:
                    pass

                # 电视剧
                try:
                    params = {"api_key": self.api_key, "query": kw, "language": "zh-CN"}
                    if region_code:
                        params["region"] = region_code
                    resp = await client.get(f"{self.BASE_URL}/search/tv", params=params)
                    if resp.status_code == 200:
                        for t in resp.json().get("results", [])[:limit]:
                            results.append(
                                {
                                    "title": t.get("name", ""),
                                    "original_title": t.get("original_name", ""),
                                    "year": (t.get("first_air_date") or "")[:4],
                                    "rating": t.get("vote_average", 0),
                                    "images": {
                                        "large": f"{self.image_base}{t.get('poster_path')}"
                                        if t.get("poster_path")
                                        else ""
                                    },
                                    "summary": t.get("overview", "")[:200],
                                    "source": "tmdb",
                                    "url": f"https://www.themoviedb.org/tv/{t.get('id')}",
                                    "type": "tv",
                                }
                            )
                except:
                    pass
        return results


class DoubanService:
    """豆瓣电影搜索 - 使用网页爬取"""

    BASE_URL = "https://movie.douban.com"

    async def search(
        self, keywords: List[str], limit: int = 10, api_key: str = None
    ) -> List[Dict[str, Any]]:
        results = []

        async with httpx.AsyncClient(
            timeout=15.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://movie.douban.com/",
                "Accept": "application/json",
            },
        ) as client:
            for kw in keywords[:2]:
                try:
                    # 使用网页搜索接口
                    print(f"豆瓣搜索: kw={kw}, limit={limit}")
                    resp = await client.get(
                        f"{self.BASE_URL}/j/search_subjects",
                        params={
                            "tag": kw,
                            "type": "movie",
                            "page_limit": limit,
                            "page": 1,
                        },
                    )
                    print(f"豆瓣响应状态: {resp.status_code}")
                    if resp.status_code == 200:
                        data = resp.json()
                        print(f"豆瓣返回: {len(data.get('subjects', []))} 条")
                        for m in data.get("subjects", []):
                            results.append(
                                {
                                    "title": m.get("title", ""),
                                    "original_title": m.get("title", ""),
                                    "year": m.get("year", ""),
                                    "rating": float(m.get("rate") or 0)
                                    if m.get("rate")
                                    else 0.0,
                                    "images": {"large": m.get("cover", "")},
                                    "summary": "",
                                    "source": "douban",
                                    "url": m.get("url", ""),
                                    "type": "movie",
                                }
                            )
                except Exception as e:
                    print(f"豆瓣搜索失败: {e}")
        return results


class BilibiliService:
    """B站视频搜索"""

    def __init__(self):
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://www.bilibili.com",
        }
        import random

        self.base_cookies = {
            "buvid3": f"{random.randint(10000000, 99999999)}infoc",
            "b_nut": "1700000000",
        }

    async def search(self, keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        results = []
        exclude_kw = [
            "白噪音",
            "放松",
            "睡眠",
            "助眠",
            "asmr",
            "疗愈",
            "雨声",
            "大自然",
            "背景音",
            "轻音乐",
            "纯音乐",
            "钢琴",
            "舒缓",
        ]

        # 每次请求创建新 session（避免 cookies 失效）
        import random

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://www.bilibili.com",
        }
        cookies = {
            "buvid3": f"{random.randint(10000000, 99999999)}infoc",
        }

        async with httpx.AsyncClient(
            timeout=15.0, headers=headers, cookies=cookies
        ) as client:
            # 先访问首页获取 cookies
            try:
                await client.get("https://www.bilibili.com")
                await asyncio.sleep(0.3)
            except:
                pass

            for kw in keywords[:3]:
                try:
                    await asyncio.sleep(0.5)  # 请求间隔
                    resp = await client.get(
                        "https://api.bilibili.com/x/web-interface/search/type",
                        params={
                            "search_type": "video",
                            "keyword": kw,
                            "page_size": limit * 4,
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("code") != 0:
                            print(f"B站API错误: {data.get('message')}")
                            continue
                        for v in data.get("data", {}).get("result", []):
                            title = v.get("title", "")
                            if any(k in title for k in exclude_kw):
                                continue
                            results.append(
                                {
                                    "title": title.replace(
                                        '<em class="keyword">', ""
                                    ).replace("</em>", ""),
                                    "original_title": v.get("author", ""),
                                    "year": "",
                                    "rating": 0,
                                    "images": {
                                        "large": v.get("pic", "").replace(
                                            "http:", "https:"
                                        )
                                    },
                                    "summary": v.get("description", ""),
                                    "source": "bilibili",
                                    "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}",
                                    "type": "video",
                                }
                            )
                except Exception as e:
                    print(f"B站搜索失败: {e}")
                    # 失败后重试一次
                    await asyncio.sleep(2)
                    try:
                        resp = await client.get(
                            "https://api.bilibili.com/x/web-interface/search/type",
                            params={
                                "search_type": "video",
                                "keyword": kw,
                                "page_size": limit * 2,
                            },
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            if data.get("code") == 0:
                                for v in data.get("data", {}).get("result", [])[:limit]:
                                    results.append(
                                        {
                                            "title": v.get("title", "")
                                            .replace('<em class="keyword">', "")
                                            .replace("</em>", ""),
                                            "original_title": v.get("author", ""),
                                            "year": "",
                                            "rating": 0,
                                            "images": {
                                                "large": v.get("pic", "").replace(
                                                    "http:", "https:"
                                                )
                                            },
                                            "summary": v.get("description", ""),
                                            "source": "bilibili",
                                            "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}",
                                            "type": "video",
                                        }
                                    )
                    except:
                        pass
        return results


class YouTubeService:
    """YouTube视频搜索 - 使用 YouTube Data API v3"""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    async def search(self, keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        results = []

        if not self.api_key:
            # 如果没有 API Key，尝试使用非官方方案（Piped/Invidious）
            return await self._search_fallback(keywords, limit)

        async with httpx.AsyncClient(timeout=15.0) as client:
            for kw in keywords[:2]:
                try:
                    resp = await client.get(
                        f"{self.BASE_URL}/search",
                        params={
                            "part": "snippet",
                            "q": kw,
                            "type": "video",
                            "maxResults": min(limit, 10),
                            "key": self.api_key,
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for item in data.get("items", []):
                            snippet = item.get("snippet", {})
                            results.append(
                                {
                                    "title": snippet.get("title", ""),
                                    "original_title": snippet.get("channelTitle", ""),
                                    "year": "",
                                    "rating": 0,
                                    "images": {
                                        "large": snippet.get("thumbnails", {})
                                        .get("high", {})
                                        .get("url", "")
                                    },
                                    "summary": snippet.get("description", "")[:200],
                                    "source": "youtube",
                                    "url": f"https://youtube.com/watch?v={item.get('id', {}).get('videoId', '')}",
                                    "type": "video",
                                }
                            )
                except Exception as e:
                    print(f"YouTube API 搜索失败: {e}")

        return results

    async def _search_fallback(
        self, keywords: List[str], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """备用方案：使用 Piped/Invidious（需要代理）"""
        results = []
        # Piped instances - 这些在有代理时可正常工作
        instances = ["https://pipedapi.kavin.rocks", "https://api.piped.yt"]

        async with httpx.AsyncClient(timeout=15.0) as client:
            for kw in keywords[:2]:
                for inst in instances:
                    try:
                        resp = await client.get(
                            f"{inst}/search",
                            params={"q": kw, "type": "video", "limit": limit},
                        )
                        if resp.status_code == 200:
                            videos = resp.json()
                            if isinstance(videos, list):
                                for v in videos:
                                    vid = v.get("url", "")
                                    if "v=" in str(vid):
                                        vid = vid.split("v=")[-1]
                                    desc = v.get("description", "")
                                    if desc:
                                        desc = desc[:200]
                                    results.append(
                                        {
                                            "title": v.get("title", ""),
                                            "original_title": v.get("uploaderName", ""),
                                            "year": "",
                                            "rating": 0,
                                            "images": {"large": v.get("thumbnail", "")},
                                            "summary": desc,
                                            "source": "youtube",
                                            "url": f"https://youtube.com/watch?v={vid}",
                                            "type": "video",
                                        }
                                    )
                            break
                    except:
                        continue
        return results


class SearchAggregator:
    """搜索聚合器"""

    def __init__(
        self,
        use_douban: bool = True,
        use_tmdb: bool = True,
        use_bilibili: bool = True,
        use_youtube: bool = True,
        use_uuuka: bool = True,
        use_mock: bool = False,
        douban_api_key: str = None,
        tmdb_api_key: str = None,
        youtube_api_key: str = None,
        content_type: str = None,
        region: str = None,
    ):
        self.douban = DoubanService() if use_douban else None
        self.tmdb = TMDBService(tmdb_api_key) if use_tmdb else None
        self.bilibili = BilibiliService() if use_bilibili else None
        self.youtube = YouTubeService(youtube_api_key) if use_youtube else None
        self.uuuka = UuukaService() if use_uuuka else None
        self.mock = use_mock
        self.douban_api_key = douban_api_key
        self.content_type = content_type
        self.region = region

    async def search_all(
        self,
        keywords_zh: List[str],
        keywords_en: List[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        tasks = []

        if self.douban:
            tasks.append(self.douban.search(keywords_zh, limit))
        if self.tmdb:
            tasks.append(self.tmdb.search(keywords_zh, limit, self.region))

        # Uuuka 短剧搜索（新增）
        if self.uuuka:
            tasks.append(self.uuuka.search(keywords_zh, limit))

        # B站需要单独处理（避免并发触发反爬）- 目前禁用，等API申请
        bilibili_task = None
        if self.bilibili:
            bilibili_task = self.bilibili.search(keywords_zh, limit)

        if self.youtube and keywords_en:
            tasks.append(self.youtube.search(keywords_en, limit))

        # 先执行其他任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Debug
        print(f"Tasks returned: {len(results)}")
        for i, r in enumerate(results):
            if isinstance(r, list):
                print(f"  Task {i}: {len(r)} results")
            else:
                print(f"  Task {i}: ERROR - {r}")

        # 等待后执行 B站（避免并发）- 目前禁用
        bilibili_results = []
        if self.bilibili and bilibili_task:
            await asyncio.sleep(1)  # 等待其他请求完成
            try:
                bilibili_results = await bilibili_task
            except Exception as e:
                print(f"B站搜索异常: {e}")

        # 合并 B站结果
        all_results = []
        for r in results:
            if isinstance(r, list):
                all_results.extend(r)

        print(f"合并后总数: {len(all_results)}")

        # Debug sources
        srcs = {}
        for it in all_results:
            s = it.get("source", "unknown")
            srcs[s] = srcs.get(s, 0) + 1
        print(f"合并后来源: {srcs}")

        # 添加 B站结果
        if bilibili_results:
            all_results.extend(bilibili_results)

        # 不排序，保留所有来源结果
        # 去重
        seen = {}
        unique = []
        for item in all_results:
            key = (
                item.get("url", "") or f"{item.get('title', '')}_{item.get('year', '')}"
            )
            if key:
                if key not in seen:
                    seen[key] = item.get("source", "unknown")
                    unique.append(item)
                else:
                    print(
                        f"去重: {key[:30]}... 来源: {item.get('source')} vs {seen[key]}"
                    )

        print(f"去重后: {len(unique)} 条")
        srcs2 = {}
        for it in unique:
            s = it.get("source", "unknown")
            srcs2[s] = srcs2.get(s, 0) + 1
        print(f"去重后来源: {srcs2}")

        # 按来源交错排列（轮播），让不同来源均匀展示
        from collections import defaultdict

        by_source = defaultdict(list)
        for item in unique:
            by_source[item.get("source", "unknown")].append(item)

        # 轮播取数
        interleaved = []
        max_len = max(len(v) for v in by_source.values()) if by_source else 0
        for i in range(max_len):
            for source, items in by_source.items():
                if i < len(items):
                    interleaved.append(items[i])

        # 计算匹配度
        final_results = self._calculate_relevance(interleaved, keywords_zh, keywords_en)

        return final_results[:limit]

    def _calculate_relevance(self, results, keywords_zh, keywords_en):
        """智能匹配度计算"""
        all_keywords = [k.lower() for k in (keywords_zh or []) + (keywords_en or [])]

        for item in results:
            score = 0
            title = (item.get("title") or "").lower()
            summary = (item.get("summary") or "").lower()
            source = item.get("source", "")

            for kw in all_keywords:
                # 标题完全匹配 - 最高分
                if kw == title:
                    score += 100
                # 标题包含关键词 - 高分
                elif kw in title:
                    score += 60
                # 摘要包含关键词 - 中等分数
                if kw in summary:
                    score += 25

            # 来源权重：电影/电视剧数据库优先
            source_bonus = {
                "tmdb": 15,  # TMDB 专业影视数据
                "douban": 15,  # 豆瓣专业影视数据
                "uuuka": 5,  # Uuuka 短剧资源
                "youtube": 0,  # YouTube 视频片段
                "bilibili": 5,  # B站视频
            }
            score += source_bonus.get(source, 0)

            # 评分加成
            rating = item.get("rating", 0)
            if rating >= 8:
                score += 10
            elif rating >= 7:
                score += 5

            # 限制在 0-100
            item["relevance_score"] = min(100, max(0, score))

        # 按匹配度降序排序
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return results
