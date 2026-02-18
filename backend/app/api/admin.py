"""
管理后台API路由
提供系统管理、用户管理、数据统计等接口

权限要求：管理员
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from app.services.auth_service import UserAuthService
from app.api.auth import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["管理后台"])

# 初始化服务
auth_service = UserAuthService()


# ============== 请求/响应模型 ==============


class AdminUpdateUserRequest(BaseModel):
    """管理员更新用户请求"""

    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    subscription: Optional[Dict[str, Any]] = None


class SystemStatsResponse(BaseModel):
    """系统统计响应"""

    total_users: int
    admin_users: int
    active_users: int
    inactive_users: int
    tier_distribution: Dict[str, int]


class UserListResponse(BaseModel):
    """用户列表响应"""

    users: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int


# ============== 用户管理接口 ==============


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="获取用户列表",
    description="获取所有用户列表（分页）",
)
async def get_users(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    获取所有用户列表

    **需要**: 管理员权限

    **示例**:
    ```
    GET /api/admin/users?skip=0&limit=50
    Authorization: Bearer {admin_token}
    ```
    """
    try:
        result = await auth_service.get_all_users(skip=skip, limit=limit)
        return UserListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@router.get(
    "/users/{user_id}", summary="获取用户详情", description="获取指定用户的详细信息"
)
async def get_user_detail(
    user_id: str, current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """
    获取用户详情

    **需要**: 管理员权限
    """
    try:
        user = await auth_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


@router.put(
    "/users/{user_id}", summary="更新用户信息", description="管理员更新指定用户的信息"
)
async def admin_update_user(
    user_id: str,
    request: AdminUpdateUserRequest,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    管理员更新用户信息

    **示例**:
    ```json
    {
        "is_active": false,
        "subscription": {
            "tier": "pro",
            "expires_at": "2024-12-31"
        }
    }
    ```
    """
    try:
        update_data = {}
        if request.is_active is not None:
            update_data["is_active"] = request.is_active
        if request.is_admin is not None:
            update_data["is_admin"] = request.is_admin
        if request.subscription:
            update_data["subscription"] = request.subscription

        result = await auth_service.admin_update_user(
            admin_id=current_admin["id"],
            target_user_id=user_id,
            update_data=update_data,
        )

        if result:
            return {"success": True, "user": result}
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete(
    "/users/{user_id}",
    summary="删除用户",
    description="删除指定用户（软删除，标记为禁用）",
)
async def delete_user(
    user_id: str, current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """
    删除用户（实际上是禁用）

    **需要**: 管理员权限
    """
    try:
        result = await auth_service.admin_update_user(
            admin_id=current_admin["id"],
            target_user_id=user_id,
            update_data={"is_active": False},
        )

        if result:
            return {"success": True, "message": "用户已禁用"}
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


# ============== 统计接口 ==============


@router.get(
    "/statistics",
    response_model=SystemStatsResponse,
    summary="系统统计",
    description="获取系统整体统计数据",
)
async def get_statistics(current_admin: Dict[str, Any] = Depends(get_current_admin)):
    """
    获取系统统计

    **需要**: 管理员权限

    **返回**:
    - 总用户数
    - 管理员数
    - 活跃用户数
    - 订阅层级分布
    """
    try:
        stats = await auth_service.get_statistics()
        return SystemStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


# ============== 系统管理接口 ==============


@router.post(
    "/system/create-admin", summary="创建管理员", description="创建一个新的管理员账户"
)
async def create_admin(
    username: str,
    email: str,
    password: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    创建管理员账户

    **需要**: 管理员权限

    **示例**:
    ```json
    {
        "username": "管理员",
        "email": "admin@example.com",
        "password": "admin123"
    }
    ```
    """
    try:
        result = await auth_service.register(
            username=username, email=email, password=password, is_admin=True
        )

        return {"success": True, "message": "管理员创建成功", "user_id": result["id"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get(
    "/system/logs", summary="查看系统日志", description="查看系统运行日志（预留接口）"
)
async def get_system_logs(
    limit: int = Query(100, ge=1, le=1000),
    current_admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    获取系统日志

    **需要**: 管理员权限

    **注意**: 当前为预留接口，需要接入日志系统
    """
    # 这里应该接入实际的日志系统
    # 例如：ELK、Filebeat等
    return {"logs": [], "message": "日志功能待实现", "total": 0}


@router.post(
    "/system/maintenance",
    summary="系统维护模式",
    description="切换系统维护模式（预留接口）",
)
async def toggle_maintenance(
    enabled: bool, current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """
    切换维护模式

    **需要**: 管理员权限

    **注意**: 当前为预留接口
    """
    # 这里应该实现维护模式切换逻辑
    return {
        "success": True,
        "maintenance_mode": enabled,
        "message": f"维护模式已{'开启' if enabled else '关闭'}",
    }
