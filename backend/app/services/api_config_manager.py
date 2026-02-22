"""
API配置管理服务 - 动态管理第三方影视API
支持在后台添加、编辑、删除API配置
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# 配置文件路径
CONFIG_FILE = "data/api_config.json"


class APIConfigManager:
    """
    API配置管理器

    用于管理第三方影视API的添加、编辑、删除和启用/禁用
    """

    # 默认API配置（不会被删除）
    DEFAULT_APIS = [
        {
            "id": "default_1",
            "name": "jkyapi",
            "display_name": "热门短剧API",
            "api_key": "jkyapi",
            "base_url": "https://jkyapi.top/API",
            "search_endpoint": "/rmdjss.php",
            "params": {"name": "{keyword}"},
            "mapping": {"items": "data", "title": "name", "url": "connection_url"},
            "type": "short_drama",
            "enabled": True,
            "description": "热门短剧搜索API",
            "is_default": True,  # 标记为默认API，不可删除
            "created_at": "2026-01-01",
            "last_tested": None,
            "status": "unknown",
        },
        {
            "id": "default_2",
            "name": "uuuka",
            "display_name": "短剧资源API",
            "api_key": "uuuka",
            "base_url": "https://api.uuuka.com",
            "search_endpoint": "/api/search",
            "params": {"keyword": "{keyword}", "page": "1", "limit": "20"},
            "mapping": {"items": "data.items", "title": "title", "url": "source_link"},
            "type": "short_drama",
            "enabled": True,
            "description": "短剧/影视搜索API",
            "is_default": True,  # 标记为默认API，不可删除
            "created_at": "2026-01-01",
            "last_tested": None,
            "status": "unknown",
        },
    ]

    def __init__(self):
        self.config_file = CONFIG_FILE
        self._ensure_config_file()

    def _ensure_config_file(self):
        """确保配置文件存在"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        if not os.path.exists(self.config_file):
            self._save_config(self.DEFAULT_APIS)

    def _load_config(self) -> List[Dict[str, Any]]:
        """加载配置"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return self.DEFAULT_APIS

    def _save_config(self, configs: List[Dict[str, Any]]):
        """保存配置"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get_all_apis(self) -> List[Dict[str, Any]]:
        """获取所有API配置"""
        return self._load_config()

    def get_enabled_apis(self) -> List[Dict[str, Any]]:
        """获取已启用的API"""
        configs = self._load_config()
        return [api for api in configs if api.get("enabled", False)]

    def get_api_by_id(self, api_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取API配置"""
        configs = self._load_config()
        for api in configs:
            if api.get("id") == api_id:
                return api
        return None

    def add_api(self, api_config: Dict[str, Any]) -> Dict[str, Any]:
        """添加新API"""
        configs = self._load_config()

        # 生成ID
        new_id = str(int(datetime.now().timestamp()))
        api_config["id"] = new_id
        api_config["created_at"] = datetime.now().strftime("%Y-%m-%d")
        api_config["status"] = "unknown"
        api_config["enabled"] = api_config.get("enabled", True)

        configs.append(api_config)
        self._save_config(configs)

        return api_config

    def update_api(
        self, api_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新API配置"""
        configs = self._load_config()

        for i, api in enumerate(configs):
            if api.get("id") == api_id:
                configs[i].update(updates)
                configs[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d")
                self._save_config(configs)
                return configs[i]

        return None

    def delete_api(self, api_id: str) -> bool:
        """删除API"""
        configs = self._load_config()

        initial_len = len(configs)
        configs = [api for api in configs if api.get("id") != api_id]

        if len(configs) < initial_len:
            self._save_config(configs)
            return True

        return False

    def toggle_api(self, api_id: str, enabled: bool) -> Optional[Dict[str, Any]]:
        """启用/禁用API"""
        return self.update_api(api_id, {"enabled": enabled})

    def test_api(self, api_id: str) -> Dict[str, Any]:
        """测试API连接"""
        import httpx

        api = self.get_api_by_id(api_id)
        if not api:
            return {"success": False, "message": "API不存在"}

        try:
            # 构建URL
            base_url = api.get("base_url", "")
            endpoint = api.get("search_endpoint", "")
            url = f"{base_url}{endpoint}"

            # 构建测试参数
            params = {}
            for k, v in api.get("params", {}).items():
                if "{keyword}" in v:
                    params[k] = v.replace("{keyword}", "测试")
                else:
                    params[k] = v
            params["page"] = 1
            params["limit"] = 3

            # 发送测试请求
            import asyncio

            async def _test():
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(url, params=params)
                    return resp.status_code, resp.text[:200]

            status_code, response_text = asyncio.run(_test())

            # 更新测试结果
            self.update_api(
                api_id,
                {
                    "last_tested": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "online" if status_code == 200 else "error",
                },
            )

            return {
                "success": status_code == 200,
                "status_code": status_code,
                "message": f"HTTP {status_code}" if status_code != 200 else "连接成功",
                "response": response_text[:100],
            }

        except Exception as e:
            self.update_api(
                api_id,
                {
                    "last_tested": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "error",
                },
            )
            return {"success": False, "message": str(e)}


# 全局实例
api_config_manager = APIConfigManager()
