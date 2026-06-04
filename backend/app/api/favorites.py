"""
收藏功能API路由
提供影视场景收藏的增删改查接口
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.services.favorites_service import FavoritesService

router = APIRouter(prefix="/api/favorites", tags=["收藏"])

# 初始化收藏服务
favorites_service = FavoritesService()


# ============== 请求/响应模型 ==============


class AddFavoriteRequest(BaseModel):
    """添加收藏请求"""

    user_id: str = Field(..., description="用户ID")
    scene_data: Dict[str, Any] = Field(..., description="场景数据")
    folder: Optional[str] = Field(None, description="文件夹名称")


class AddFavoriteResponse(BaseModel):
    """添加收藏响应"""

    success: bool
    favorite_id: str
    message: str
    data: Optional[Dict[str, Any]] = None


class GetFavoritesResponse(BaseModel):
    """获取收藏列表响应"""

    favorites: List[Dict[str, Any]]
    total: int
    folders: List[str]
    limit: int
    offset: int


class RemoveFavoriteResponse(BaseModel):
    """删除收藏响应"""

    success: bool
    message: str


class AddTagsRequest(BaseModel):
    """添加标签请求"""

    user_id: str = Field(..., description="用户ID")
    favorite_id: str = Field(..., description="收藏项ID")
    tags: List[str] = Field(..., description="标签列表")


# ============== API端点 ==============


@router.post(
    "/add",
    response_model=AddFavoriteResponse,
    summary="添加收藏",
    description="收藏一个影视场景参考",
)
async def add_favorite(request: AddFavoriteRequest):
    """
    添加收藏

    **示例**:
    ```json
    {
        "user_id": "user_001",
        "scene_data": {
            "title": "盗梦空间",
            "year": "2010",
            "scene_description": "雨夜追车",
            "relevance_score": 95
        },
        "folder": "动作场景参考"
    }
    ```
    """
    try:
        result = await favorites_service.add_favorite(
            user_id=request.user_id,
            scene_data=request.scene_data,
            folder=request.folder,
        )

        return AddFavoriteResponse(
            success=True, favorite_id=result["id"], message="收藏成功", data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"收藏失败: {str(e)}")


@router.get(
    "/{user_id}",
    response_model=GetFavoritesResponse,
    summary="获取收藏列表",
    description="获取用户的所有收藏",
)
async def get_favorites(
    user_id: str, folder: Optional[str] = None, limit: int = 50, offset: int = 0
):
    """
    获取收藏列表

    **参数**:
    - user_id: 用户ID（路径参数）
    - folder: 文件夹筛选（可选）
    - limit: 返回数量（默认50）
    - offset: 偏移量（分页）

    **示例**:
    ```
    GET /api/favorites/user_001?folder=动作场景参考&limit=10
    ```
    """
    try:
        result = await favorites_service.get_favorites(
            user_id=user_id, folder=folder, limit=limit, offset=offset
        )

        return GetFavoritesResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏失败: {str(e)}")


@router.delete(
    "/{user_id}/{favorite_id}",
    response_model=RemoveFavoriteResponse,
    summary="取消收藏",
    description="删除一个收藏项",
)
async def remove_favorite(user_id: str, favorite_id: str):
    """
    取消收藏

    **示例**:
    ```
    DELETE /api/favorites/user_001/abc123
    ```
    """
    try:
        success = await favorites_service.remove_favorite(user_id, favorite_id)

        if success:
            return RemoveFavoriteResponse(success=True, message="取消收藏成功")
        else:
            raise HTTPException(status_code=404, detail="收藏项不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消收藏失败: {str(e)}")


@router.get(
    "/{user_id}/{favorite_id}/detail",
    summary="获取收藏详情",
    description="获取单个收藏的详细信息",
)
async def get_favorite_detail(user_id: str, favorite_id: str):
    """
    获取收藏详情

    **示例**:
    ```
    GET /api/favorites/user_001/abc123/detail
    ```
    """
    try:
        result = await favorites_service.get_favorite_by_id(user_id, favorite_id)

        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="收藏项不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详情失败: {str(e)}")


@router.post("/add-tags", summary="添加标签", description="给收藏项添加标签")
async def add_tags(request: AddTagsRequest):
    """
    添加标签

    **示例**:
    ```json
    {
        "user_id": "user_001",
        "favorite_id": "abc123",
        "tags": ["动作", "雨夜", "紧张"]
    }
    ```
    """
    try:
        success = await favorites_service.add_tags(
            user_id=request.user_id, favorite_id=request.favorite_id, tags=request.tags
        )

        if success:
            return {"success": True, "message": "标签添加成功"}
        else:
            raise HTTPException(status_code=404, detail="收藏项不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加标签失败: {str(e)}")


@router.get(
    "/{user_id}/folders",
    summary="获取文件夹列表",
    description="获取用户的所有收藏文件夹",
)
async def get_folders(user_id: str):
    """
    获取文件夹列表

    **示例**:
    ```
    GET /api/favorites/user_001/folders
    ```
    """
    try:
        folders = await favorites_service.get_folders(user_id)
        return {"folders": folders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件夹失败: {str(e)}")
