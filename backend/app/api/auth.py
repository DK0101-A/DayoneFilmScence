"""
用户认证API路由
提供注册、登录、用户信息管理等接口
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any

from app.services.auth_service import UserAuthService, JWT_SECRET, JWT_ALGORITHM
import jwt

router = APIRouter(prefix="/api/auth", tags=["用户认证"])

# 初始化认证服务
auth_service = UserAuthService()


# ============== 请求/响应模型 ==============


class RegisterRequest(BaseModel):
    """注册请求"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")


class RegisterResponse(BaseModel):
    """注册响应"""

    success: bool
    user_id: str
    message: str


class LoginRequest(BaseModel):
    """登录请求"""

    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应"""

    success: bool
    token: str
    user: Dict[str, Any]
    message: str


class UserProfileResponse(BaseModel):
    """用户信息响应"""

    id: str
    username: str
    email: str
    is_admin: bool
    profile: Dict[str, Any]
    subscription: Dict[str, Any]


class UpdateProfileRequest(BaseModel):
    """更新资料请求"""

    username: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""

    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")


# ============== 依赖函数 ==============


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    获取当前登录用户

    从Authorization header中提取并验证JWT Token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证信息")

    # 提取token
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    # 验证token
    payload = await auth_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token无效或已过期")

    # 获取用户信息
    user = await auth_service.get_user(payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


async def get_current_admin(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取当前管理员用户

    验证用户是否为管理员
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="需要管理员权限")

    return current_user


# ============== 公开接口 ==============


@router.post(
    "/register",
    response_model=RegisterResponse,
    summary="用户注册",
    description="注册新用户账户",
)
async def register(request: RegisterRequest):
    """
    用户注册

    **示例**:
    ```json
    {
        "username": "张导演",
        "email": "director@example.com",
        "password": "123456"
    }
    ```
    """
    try:
        result = await auth_service.register(
            username=request.username,
            email=request.email,
            password=request.password,
            is_admin=False,  # 普通用户注册
        )

        return RegisterResponse(success=True, user_id=result["id"], message="注册成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="用户登录",
    description="用户登录获取JWT Token",
)
async def login(request: LoginRequest):
    """
    用户登录

    **示例**:
    ```json
    {
        "email": "director@example.com",
        "password": "123456"
    }
    ```

    **返回**:
    - token: JWT Token，用于后续请求认证
    - user: 用户信息
    """
    try:
        result = await auth_service.login(
            email=request.email, password=request.password
        )

        return LoginResponse(
            success=True, token=result["token"], user=result["user"], message="登录成功"
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


# ============== 需要登录的接口 ==============


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    summary="获取用户信息",
    description="获取当前登录用户的详细信息",
)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    获取当前用户信息

    **需要**: Authorization: Bearer {token}
    """
    return UserProfileResponse(**current_user)


@router.put("/profile", summary="更新用户信息", description="更新当前用户的资料")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    更新用户信息

    **示例**:
    ```json
    {
        "username": "新用户名",
        "profile": {
            "company": "某某影视公司",
            "title": "导演"
        }
    }
    ```
    """
    try:
        update_data = {}
        if request.username:
            update_data["username"] = request.username
        if request.profile:
            update_data["profile"] = request.profile

        result = await auth_service.update_user(current_user["id"], update_data)

        if result:
            return {"success": True, "user": result}
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post("/change-password", summary="修改密码", description="修改当前用户的密码")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    修改密码

    **示例**:
    ```json
    {
        "old_password": "旧密码",
        "new_password": "新密码"
    }
    ```
    """
    try:
        success = await auth_service.change_password(
            user_id=current_user["id"],
            old_password=request.old_password,
            new_password=request.new_password,
        )

        if success:
            return {"success": True, "message": "密码修改成功"}
        else:
            raise HTTPException(status_code=400, detail="旧密码错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.post(
    "/logout", summary="退出登录", description="退出登录（客户端需要清除token）"
)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    退出登录

    **注意**: 服务端无状态，只需客户端清除token
    """
    return {"success": True, "message": "退出成功"}
