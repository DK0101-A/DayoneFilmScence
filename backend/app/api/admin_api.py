"""
第三方API管理接口
用于在后台添加、编辑、删除、测试第三方影视API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.services.api_config_manager import api_config_manager
from app.api.auth import get_current_admin

router = APIRouter(prefix="/api/admin/apis", tags=["API管理"])


# ============== 请求/响应模型 ==============


class AddAPIRequest(BaseModel):
    """添加API请求"""

    name: str = Field(..., description="API名称")
    base_url: str = Field(..., description="基础URL")
    search_endpoint: str = Field(..., description="搜索接口路径")
    params: Dict[str, str] = Field(default_factory=dict, description="请求参数模板")
    enabled: bool = Field(default=True, description="是否启用")
    description: str = Field(default="", description="API描述")


class UpdateAPIRequest(BaseModel):
    """更新API请求"""

    name: Optional[str] = None
    base_url: Optional[str] = None
    search_endpoint: Optional[str] = None
    params: Optional[Dict[str, str]] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None


class APIListResponse(BaseModel):
    """API列表响应"""

    apis: List[Dict[str, Any]]
    total: int


class APITestResponse(BaseModel):
    """API测试响应"""

    success: bool
    status_code: Optional[int] = None
    message: str
    response: Optional[str] = None


# ============== API管理接口 ==============


@router.get("", response_model=APIListResponse, summary="获取API列表")
async def get_api_list():
    """获取所有已配置的第三方API列表"""
    apis = api_config_manager.get_all_apis()
    return {"apis": apis, "total": len(apis)}


@router.get("/{api_id}", summary="获取API详情")
async def get_api_detail(api_id: str):
    """获取单个API的详细信息"""
    api = api_config_manager.get_api_by_id(api_id)
    if not api:
        raise HTTPException(status_code=404, detail="API不存在")
    return api


@router.post("", summary="添加新API")
async def add_api(request: AddAPIRequest):
    """添加新的第三方API配置"""
    api_config = request.model_dump()
    result = api_config_manager.add_api(api_config)
    return {"success": True, "message": "API添加成功", "data": result}


@router.put("/{api_id}", summary="更新API")
async def update_api(api_id: str, request: UpdateAPIRequest):
    """更新API配置"""
    updates = request.model_dump(exclude_unset=True)
    result = api_config_manager.update_api(api_id, updates)

    if not result:
        raise HTTPException(status_code=404, detail="API不存在")

    return {"success": True, "message": "API更新成功", "data": result}


@router.delete("/{api_id}", summary="删除API")
async def delete_api(api_id: str):
    """删除API配置"""
    success = api_config_manager.delete_api(api_id)

    if not success:
        raise HTTPException(status_code=404, detail="API不存在")

    return {"success": True, "message": "API删除成功"}


@router.post("/{api_id}/toggle", summary="启用/禁用API")
async def toggle_api(api_id: str, enabled: bool = True):
    """启用或禁用API"""
    result = api_config_manager.toggle_api(api_id, enabled)

    if not result:
        raise HTTPException(status_code=404, detail="API不存在")

    return {
        "success": True,
        "message": f"API已{'启用' if enabled else '禁用'}",
        "data": result,
    }


@router.post("/{api_id}/test", response_model=APITestResponse, summary="测试API连接")
async def test_api(api_id: str):
    """测试API连接是否正常"""
    result = api_config_manager.test_api(api_id)
    return result


@router.get("/enabled/list", summary="获取已启用的API")
async def get_enabled_apis():
    """获取所有已启用的API列表（用于搜索）"""
    apis = api_config_manager.get_enabled_apis()
    return {"apis": apis, "total": len(apis)}
