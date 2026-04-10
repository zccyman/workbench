"""Core Assets - 数据模型"""

from pydantic import BaseModel
from datetime import datetime


class AssetBase(BaseModel):
    name: str
    description: str = ""
    category: str = "general"
    icon: str = "📦"
    source_url: str = ""
    tags: list[str] = []
    priority: int = 0  # 越大越靠前
    auto_filled: bool = False  # 是否从知识库自动补充


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    icon: str | None = None
    source_url: str | None = None
    tags: list[str] | None = None
    priority: int | None = None


class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    total: int
    assets: list[AssetResponse]
