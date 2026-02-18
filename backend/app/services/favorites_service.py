"""
收藏服务（开发期版本）
使用JSON文件存储，后期迁移到数据库

功能：
- 添加收藏
- 获取收藏列表
- 取消收藏
- 按用户分类
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class FavoritesService:
    """
    收藏服务

    开发期使用JSON文件存储
    生产期迁移到PostgreSQL
    """

    def __init__(self, storage_path: str = "./data/favorites.json"):
        """
        初始化收藏服务

        Args:
            storage_path: JSON文件存储路径
        """
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        """确保存储文件存在"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            self._save_data({"users": {}})

    def _load_data(self) -> Dict:
        """加载数据"""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"users": {}}

    def _save_data(self, data: Dict):
        """保存数据"""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def add_favorite(
        self, user_id: str, scene_data: Dict[str, Any], folder: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        添加收藏

        Args:
            user_id: 用户ID
            scene_data: 场景数据
            folder: 文件夹名称（可选）

        Returns:
            收藏的详细信息
        """
        data = self._load_data()

        # 确保用户存在
        if user_id not in data["users"]:
            data["users"][user_id] = {"favorites": [], "folders": ["默认收藏夹"]}

        # 生成收藏ID
        favorite_id = str(uuid.uuid4())[:8]

        # 构建收藏项
        favorite_item = {
            "id": favorite_id,
            "scene_data": scene_data,
            "folder": folder or "默认收藏夹",
            "created_at": datetime.now().isoformat(),
            "tags": [],
        }

        # 添加到收藏列表
        data["users"][user_id]["favorites"].append(favorite_item)

        # 如果是新文件夹，添加到文件夹列表
        if folder and folder not in data["users"][user_id]["folders"]:
            data["users"][user_id]["folders"].append(folder)

        self._save_data(data)

        return favorite_item

    async def get_favorites(
        self,
        user_id: str,
        folder: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        获取收藏列表

        Args:
            user_id: 用户ID
            folder: 筛选文件夹（可选）
            limit: 返回数量
            offset: 偏移量

        Returns:
            收藏列表和统计信息
        """
        data = self._load_data()

        if user_id not in data["users"]:
            return {
                "favorites": [],
                "total": 0,
                "folders": [],
                "limit": limit,
                "offset": offset,
            }

        user_data = data["users"][user_id]
        favorites = user_data.get("favorites", [])

        # 按文件夹筛选
        if folder:
            favorites = [f for f in favorites if f.get("folder") == folder]

        # 按时间倒序
        favorites = sorted(
            favorites, key=lambda x: x.get("created_at", ""), reverse=True
        )

        total = len(favorites)

        # 分页
        favorites = favorites[offset : offset + limit]

        return {
            "favorites": favorites,
            "total": total,
            "folders": user_data.get("folders", []),
            "limit": limit,
            "offset": offset,
        }

    async def remove_favorite(self, user_id: str, favorite_id: str) -> bool:
        """
        取消收藏

        Args:
            user_id: 用户ID
            favorite_id: 收藏项ID

        Returns:
            是否成功删除
        """
        data = self._load_data()

        if user_id not in data["users"]:
            return False

        favorites = data["users"][user_id].get("favorites", [])

        # 查找并删除
        original_len = len(favorites)
        data["users"][user_id]["favorites"] = [
            f for f in favorites if f.get("id") != favorite_id
        ]

        if len(data["users"][user_id]["favorites"]) < original_len:
            self._save_data(data)
            return True

        return False

    async def get_favorite_by_id(
        self, user_id: str, favorite_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取单个收藏详情

        Args:
            user_id: 用户ID
            favorite_id: 收藏项ID

        Returns:
            收藏详情或None
        """
        data = self._load_data()

        if user_id not in data["users"]:
            return None

        favorites = data["users"][user_id].get("favorites", [])

        for fav in favorites:
            if fav.get("id") == favorite_id:
                return fav

        return None

    async def add_tags(self, user_id: str, favorite_id: str, tags: List[str]) -> bool:
        """
        给收藏添加标签

        Args:
            user_id: 用户ID
            favorite_id: 收藏项ID
            tags: 标签列表

        Returns:
            是否成功
        """
        data = self._load_data()

        if user_id not in data["users"]:
            return False

        favorites = data["users"][user_id].get("favorites", [])

        for fav in favorites:
            if fav.get("id") == favorite_id:
                # 合并标签，去重
                existing_tags = set(fav.get("tags", []))
                existing_tags.update(tags)
                fav["tags"] = list(existing_tags)
                self._save_data(data)
                return True

        return False

    async def get_folders(self, user_id: str) -> List[str]:
        """
        获取用户的所有文件夹

        Args:
            user_id: 用户ID

        Returns:
            文件夹列表
        """
        data = self._load_data()

        if user_id not in data["users"]:
            return ["默认收藏夹"]

        return data["users"][user_id].get("folders", ["默认收藏夹"])
