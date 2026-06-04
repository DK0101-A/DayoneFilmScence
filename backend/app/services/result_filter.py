"""
搜索结果筛选器
根据年代、地区、类型筛选搜索结果
"""

from typing import List, Dict, Any, Optional


class ResultFilter:
    """
    搜索结果筛选器
    """

    @staticmethod
    def filter_results(
        results: List[Dict[str, Any]],
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        region: Optional[str] = None,
        genre: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        筛选搜索结果

        Args:
            results: 原始搜索结果
            year_from: 起始年份
            year_to: 结束年份
            region: 地区（华语/欧美/日韩）
            genre: 类型（动作/爱情/悬疑）

        Returns:
            筛选后的结果
        """
        filtered = results

        # 年代筛选
        if year_from or year_to:
            filtered = [
                r
                for r in filtered
                if ResultFilter._match_year(r.get("year"), year_from, year_to)
            ]

        # 地区筛选（简单规则）
        if region:
            filtered = [r for r in filtered if ResultFilter._match_region(r, region)]

        # 类型筛选（需要更多信息，暂时简单处理）
        if genre:
            filtered = [r for r in filtered if ResultFilter._match_genre(r, genre)]

        return filtered

    @staticmethod
    def _match_year(
        year_str: Optional[str], year_from: Optional[int], year_to: Optional[int]
    ) -> bool:
        """匹配年份"""
        if not year_str:
            return True

        try:
            year = int(str(year_str)[:4])  # 提取前4位作为年份

            if year_from and year < year_from:
                return False
            if year_to and year > year_to:
                return False

            return True
        except:
            return True

    @staticmethod
    def _match_region(result: Dict[str, Any], region: str) -> bool:
        """匹配地区（简化版）"""
        title = result.get("title", "")
        original_title = result.get("original_title", "")

        # 华语特征
        chinese_indicators = ["华语", "中国", "香港", "台湾", ""]
        # 欧美特征
        western_indicators = []
        # 日韩特征
        asian_indicators = []

        # 简单的中文检测
        has_chinese = any("\u4e00" <= char <= "\u9fff" for char in title)

        if region == "华语":
            return has_chinese
        elif region == "欧美":
            return not has_chinese and original_title  # 有英文原名
        elif region == "日韩":
            # 简化处理
            return not has_chinese

        return True

    @staticmethod
    def _match_genre(result: Dict[str, Any], genre: str) -> bool:
        """匹配类型（简化版，依赖genres字段）"""
        genres = result.get("genres", [])

        if not genres:
            # 如果没有类型信息，默认保留
            return True

        # 类型映射
        genre_mapping = {
            "动作": ["动作", "Action", "冒险"],
            "爱情": ["爱情", "Romance", "剧情"],
            "悬疑": ["悬疑", "Thriller", "犯罪", "Thriller"],
            "喜剧": ["喜剧", "Comedy"],
            "科幻": ["科幻", "Sci-Fi", "Science Fiction"],
        }

        keywords = genre_mapping.get(genre, [genre])

        return any(keyword in str(g) for keyword in keywords for g in genres)
