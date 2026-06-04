"""
时间戳服务（开发期版本）
使用JSON文件存储用户标注和AI推断的时间戳

功能：
- 用户标注时间戳
- AI推断时间戳
- 弹幕挖掘时间戳
- 时间戳查询
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib


class TimestampService:
    """
    时间戳服务

    存储结构：
    {
        "scenes": {
            "<scene_hash>": {
                "title": "速度与激情7",
                "source": "tmdb",
                "url": "...",
                "timestamps": [
                    {
                        "id": "xxx",
                        "time": "00:45:30",
                        "time_seconds": 2730,
                        "description": "雨夜追车场景",
                        "type": "user|ai|danmaku",
                        "user_id": "xxx",
                        "votes": 5,
                        "created_at": "..."
                    }
                ]
            }
        }
    }
    """

    def __init__(self, storage_path: str = "./data/timestamps.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        """确保存储文件存在"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            self._save_data({"scenes": {}})

    def _load_data(self) -> Dict:
        """加载数据"""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"scenes": {}}

    def _save_data(self, data: Dict):
        """保存数据"""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _generate_scene_key(self, title: str, source: str, url: str = "") -> str:
        """生成场景唯一标识"""
        key = f"{source}:{title}:{url}"
        return hashlib.md5(key.encode()).hexdigest()[:12]

    def _parse_time_to_seconds(self, time_str: str) -> int:
        """将时间字符串转换为秒数"""
        try:
            parts = time_str.split(":")
            if len(parts) == 3:
                h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
                return h * 3600 + m * 60 + s
            elif len(parts) == 2:
                m, s = int(parts[0]), int(parts[1])
                return m * 60 + s
            else:
                return int(time_str)
        except:
            return 0

    def _seconds_to_time(self, seconds: int) -> str:
        """将秒数转换为时间字符串"""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"

    async def add_timestamp(
        self,
        title: str,
        source: str,
        url: str,
        time_str: str,
        description: str,
        user_id: str = "anonymous",
        timestamp_type: str = "user",
    ) -> Dict[str, Any]:
        """
        添加时间戳标注

        Args:
            title: 影视名称
            source: 数据来源 (tmdb/douban/youtube等)
            url: 详情链接
            time_str: 时间戳 (如 "45:30" 或 "00:45:30")
            description: 场景描述
            user_id: 用户ID
            timestamp_type: 类型 (user/ai/danmaku)

        Returns:
            添加的时间戳信息
        """
        data = self._load_data()
        scene_key = self._generate_scene_key(title, source, url)

        # 确保场景存在
        if scene_key not in data["scenes"]:
            data["scenes"][scene_key] = {
                "title": title,
                "source": source,
                "url": url,
                "timestamps": [],
            }

        # 生成时间戳ID
        ts_id = str(uuid.uuid4())[:8]
        time_seconds = self._parse_time_to_seconds(time_str)

        timestamp_item = {
            "id": ts_id,
            "time": time_str,
            "time_seconds": time_seconds,
            "description": description,
            "type": timestamp_type,
            "user_id": user_id,
            "votes": 1 if timestamp_type == "user" else 0,
            "created_at": datetime.now().isoformat(),
        }

        data["scenes"][scene_key]["timestamps"].append(timestamp_item)
        self._save_data(data)

        return timestamp_item

    async def get_timestamps(
        self, title: str, source: str, url: str = ""
    ) -> List[Dict[str, Any]]:
        """
        获取场景的时间戳列表

        Args:
            title: 影视名称
            source: 数据来源
            url: 详情链接

        Returns:
            时间戳列表（按时间排序，按投票数排序）
        """
        data = self._load_data()
        scene_key = self._generate_scene_key(title, source, url)

        if scene_key not in data["scenes"]:
            return []

        timestamps = data["scenes"][scene_key].get("timestamps", [])

        # 按投票数排序，同票数按时间排序
        timestamps.sort(key=lambda x: (-x.get("votes", 0), x.get("time_seconds", 0)))

        return timestamps

    async def get_best_timestamp(
        self, title: str, source: str, url: str = "", scene_keyword: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        获取最佳匹配的时间戳

        Args:
            title: 影视名称
            source: 数据来源
            url: 详情链接
            scene_keyword: 场景关键词（用于匹配描述）

        Returns:
            最佳时间戳或None
        """
        timestamps = await self.get_timestamps(title, source, url)

        if not timestamps:
            return None

        if scene_keyword:
            # 尝试匹配场景描述
            scene_keyword = scene_keyword.lower()
            for ts in timestamps:
                desc = (ts.get("description") or "").lower()
                if scene_keyword in desc:
                    return ts

        # 返回投票最多的
        return timestamps[0]

    async def vote_timestamp(
        self, title: str, source: str, url: str, timestamp_id: str, vote: int = 1
    ) -> bool:
        """
        为时间戳投票

        Args:
            title: 影视名称
            source: 数据来源
            url: 详情链接
            timestamp_id: 时间戳ID
            vote: 投票值 (+1 或 -1)

        Returns:
            是否成功
        """
        data = self._load_data()
        scene_key = self._generate_scene_key(title, source, url)

        if scene_key not in data["scenes"]:
            return False

        timestamps = data["scenes"][scene_key].get("timestamps", [])

        for ts in timestamps:
            if ts.get("id") == timestamp_id:
                ts["votes"] = ts.get("votes", 0) + vote
                self._save_data(data)
                return True

        return False

    async def search_by_keyword(
        self, keyword: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        按关键词搜索时间戳

        Args:
            keyword: 搜索关键词
            limit: 返回数量

        Returns:
            匹配的场景和时间戳列表
        """
        data = self._load_data()
        results = []
        keyword = keyword.lower()

        for scene_key, scene in data["scenes"].items():
            # 匹配片名
            if keyword in scene.get("title", "").lower():
                for ts in scene.get("timestamps", []):
                    results.append(
                        {
                            "scene": scene,
                            "timestamp": ts,
                        }
                    )
            # 匹配场景描述
            else:
                for ts in scene.get("timestamps", []):
                    if keyword in (ts.get("description") or "").lower():
                        results.append(
                            {
                                "scene": scene,
                                "timestamp": ts,
                            }
                        )

        # 按投票数排序
        results.sort(key=lambda x: -x["timestamp"].get("votes", 0))

        return results[:limit]

    async def add_ai_timestamp(
        self, title: str, source: str, url: str, scene_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        AI推断时间戳（占位，实际需要调用AI服务）

        Args:
            title: 影视名称
            source: 数据来源
            url: 详情链接
            scene_description: 用户描述的场景

        Returns:
            AI推断的时间戳或None
        """
        # TODO: 调用AI服务分析场景，推断时间点
        # 这里先用占位逻辑
        common_scenes = {
            "开场": "00:05:00",
            "开头": "00:05:00",
            "结尾": "01:30:00",
            "高潮": "01:00:00",
            "追车": "00:45:00",
            "飙车": "00:45:00",
            "吻戏": "00:35:00",
            "表白": "00:40:00",
            "战斗": "00:50:00",
            "雨夜": "00:30:00",
        }

        for keyword, time_str in common_scenes.items():
            if keyword in scene_description:
                return await self.add_timestamp(
                    title=title,
                    source=source,
                    url=url,
                    time_str=time_str,
                    description=f"AI推断: {keyword}场景",
                    user_id="ai",
                    timestamp_type="ai",
                )

        return None


# 单例
_timestamp_service = None


def get_timestamp_service() -> TimestampService:
    """获取时间戳服务实例"""
    global _timestamp_service
    if _timestamp_service is None:
        _timestamp_service = TimestampService()
    return _timestamp_service
