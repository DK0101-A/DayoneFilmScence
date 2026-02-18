"""
用户认证与管理系统
开发期使用JSON文件存储，生产期迁移到数据库

功能：
- 用户注册/登录
- JWT Token认证
- 管理员权限
- 用户信息管理
"""

import json
import os
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
import uuid

# JWT配置
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class UserAuthService:
    """
    用户认证服务
    """

    def __init__(self, storage_path: str = "./data/users.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        """确保存储文件存在"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            self._save_data({"users": {}, "sessions": {}})

    def _load_data(self) -> Dict:
        """加载数据"""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"users": {}, "sessions": {}}

    def _save_data(self, data: Dict):
        """保存数据"""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _generate_user_id(self) -> str:
        """生成用户ID"""
        return f"user_{uuid.uuid4().hex[:8]}"

    async def register(
        self, username: str, email: str, password: str, is_admin: bool = False
    ) -> Dict[str, Any]:
        """
        用户注册

        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            is_admin: 是否为管理员

        Returns:
            用户信息（不含密码）
        """
        data = self._load_data()

        # 检查邮箱是否已注册
        for user in data["users"].values():
            if user.get("email") == email:
                raise ValueError("邮箱已被注册")

        # 检查用户名是否已存在
        for user in data["users"].values():
            if user.get("username") == username:
                raise ValueError("用户名已存在")

        # 创建用户
        user_id = self._generate_user_id()
        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "password_hash": self._hash_password(password),
            "is_admin": is_admin,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "profile": {
                "avatar": None,
                "phone": None,
                "company": None,
                "title": None,  # 导演/编剧/摄影等
            },
            "subscription": {
                "tier": "free",  # free/pro/enterprise
                "expires_at": None,
            },
        }

        data["users"][user_id] = user_data
        self._save_data(data)

        # 返回用户信息（不含密码）
        return self._sanitize_user_data(user_data)

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        用户登录

        Args:
            email: 邮箱
            password: 密码

        Returns:
            包含token的用户信息
        """
        data = self._load_data()

        # 查找用户
        user = None
        for u in data["users"].values():
            if u.get("email") == email:
                user = u
                break

        if not user:
            raise ValueError("用户不存在")

        if not user.get("is_active", True):
            raise ValueError("账户已被禁用")

        # 验证密码
        password_hash = self._hash_password(password)
        if user["password_hash"] != password_hash:
            raise ValueError("密码错误")

        # 更新最后登录时间
        user["last_login"] = datetime.now().isoformat()
        self._save_data(data)

        # 生成JWT Token
        token = self._generate_token(user["id"], user.get("is_admin", False))

        return {"token": token, "user": self._sanitize_user_data(user)}

    def _generate_token(self, user_id: str, is_admin: bool) -> str:
        """生成JWT Token"""
        payload = {
            "user_id": user_id,
            "is_admin": is_admin,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT Token

        Args:
            token: JWT Token

        Returns:
            解码后的token数据或None
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        data = self._load_data()
        user = data["users"].get(user_id)
        if user:
            return self._sanitize_user_data(user)
        return None

    async def update_user(
        self, user_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新用户信息"""
        data = self._load_data()

        if user_id not in data["users"]:
            return None

        # 不允许直接更新敏感字段
        forbidden_fields = ["id", "password_hash", "is_admin", "created_at"]
        for field in forbidden_fields:
            if field in update_data:
                del update_data[field]

        # 更新数据
        data["users"][user_id].update(update_data)
        self._save_data(data)

        return self._sanitize_user_data(data["users"][user_id])

    async def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        """修改密码"""
        data = self._load_data()

        if user_id not in data["users"]:
            return False

        user = data["users"][user_id]

        # 验证旧密码
        if user["password_hash"] != self._hash_password(old_password):
            return False

        # 更新密码
        user["password_hash"] = self._hash_password(new_password)
        self._save_data(data)

        return True

    def _sanitize_user_data(self, user: Dict) -> Dict:
        """清理用户数据（移除敏感信息）"""
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_admin": user.get("is_admin", False),
            "is_active": user.get("is_active", True),
            "created_at": user["created_at"],
            "last_login": user.get("last_login"),
            "profile": user.get("profile", {}),
            "subscription": user.get("subscription", {}),
        }

    # ========== 管理员功能 ==========

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        获取所有用户（管理员功能）

        Args:
            skip: 跳过数量
            limit: 返回数量

        Returns:
            用户列表和统计
        """
        data = self._load_data()
        users = list(data["users"].values())

        total = len(users)
        users = users[skip : skip + limit]

        return {
            "users": [self._sanitize_user_data(u) for u in users],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def admin_update_user(
        self, admin_id: str, target_user_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        管理员更新用户信息

        Args:
            admin_id: 管理员ID
            target_user_id: 目标用户ID
            update_data: 更新数据

        Returns:
            更新后的用户信息
        """
        data = self._load_data()

        # 验证管理员权限
        admin = data["users"].get(admin_id)
        if not admin or not admin.get("is_admin", False):
            raise ValueError("权限不足")

        if target_user_id not in data["users"]:
            return None

        # 管理员可以更新更多字段
        data["users"][target_user_id].update(update_data)
        self._save_data(data)

        return self._sanitize_user_data(data["users"][target_user_id])

    async def get_statistics(self) -> Dict[str, Any]:
        """获取系统统计（管理员功能）"""
        data = self._load_data()
        users = list(data["users"].values())

        total_users = len(users)
        admin_users = sum(1 for u in users if u.get("is_admin", False))
        active_users = sum(1 for u in users if u.get("is_active", True))

        # 按订阅层级统计
        tier_counts = {}
        for u in users:
            tier = u.get("subscription", {}).get("tier", "free")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        return {
            "total_users": total_users,
            "admin_users": admin_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "tier_distribution": tier_counts,
            "new_users_today": 0,  # 需要实际计算
            "new_users_this_week": 0,  # 需要实际计算
        }
