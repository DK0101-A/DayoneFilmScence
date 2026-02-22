"""
第三方影视API服务 - 聚合多个API源
用于补充主流数据源（豆瓣、TMDB、YouTube）
"""

import httpx
from typing import List, Dict, Any, Optional


class ThirdPartyAPIService:
    """
    第三方影视API服务

    注意：这些API大多不稳定，可能随时失效
    仅作为补充数据源使用
    """

    # API配置列表
    API_SOURCES = [
        {
            "name": "jkyapi",
            "base_url": "https://jkyapi.top/API",
            "search_endpoint": "/rmdjss.php",
            "params": {"name": "{keyword}"},
            "enabled": True,
        },
        {
            "name": "duanju",
            "base_url": "https://www.duanju.click/api/short",
            "search_endpoint": "/quark",
            "params": {"text": "{keyword}"},
            "enabled": False,  # 当前不可用
        },
        {
            "name": "longzhu",
            "base_url": "https://www.hhlqilongzhu.cn/api",
            "search_endpoint": "/ziyuan_nanfeng.php",
            "params": {"keysearch": "{keyword}"},
            "enabled": False,  # 当前不可用
        },
    ]

    async def search(
        self, keywords: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索第三方资源"""
        results = []

        for kw in keywords[:2]:
            # 尝试每个启用的API
            for api in self.API_SOURCES:
                if not api.get("enabled", False):
                    continue

                try:
                    api_results = await self._search_single_api(api, kw, limit)
                    results.extend(api_results)
                    print(f"第三方API [{api['name']}] 返回 {len(api_results)} 条")
                except Exception as e:
                    print(f"第三方API [{api['name']}] 失败: {e}")

        return results

    async def _search_single_api(
        self, api: Dict, keyword: str, limit: int
    ) -> List[Dict[str, Any]]:
        """调用单个API"""
        results = []

        # 构建URL
        base_url = api["base_url"]
        endpoint = api["search_endpoint"]
        url = f"{base_url}{endpoint}"

        # 构建参数
        params = {}
        for k, v in api.get("params", {}).items():
            params[k] = v.replace("{keyword}", keyword)
        params["page"] = 1
        params["limit"] = limit

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    results = self._parse_response(api["name"], data)
                except:
                    pass

        return results

    def _parse_response(self, api_name: str, data: Any) -> List[Dict[str, Any]]:
        """解析不同API的响应格式"""
        results = []

        if api_name == "jkyapi":
            # 热门短剧API格式
            if isinstance(data, list):
                for item in data:
                    results.append(
                        {
                            "title": item.get("name", ""),
                            "original_title": item.get("name", ""),
                            "year": "",
                            "rating": 0,
                            "images": {"large": ""},
                            "summary": f"来源: 夸克网盘",
                            "source": "jkyapi",
                            "url": item.get("connection_url", ""),
                            "type": "short_drama",
                        }
                    )

        return results


# 全局实例
third_party_service = ThirdPartyAPIService()
