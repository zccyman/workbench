"""Core Assets - API 路由"""

import json
from fastapi import APIRouter, HTTPException

from .models import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse
from .database import (
    list_assets, get_asset, add_asset, update_asset,
    remove_asset, reorder_assets,
)
from .knowledge_search import auto_fill_description

router = APIRouter(tags=["core-assets"])


@router.get("/assets", response_model=AssetListResponse)
async def api_list_assets():
    """获取所有核心资产（按 priority 排序）"""
    assets = list_assets()
    for a in assets:
        if isinstance(a.get("tags"), str):
            a["tags"] = json.loads(a["tags"])
        a["auto_filled"] = bool(a.get("auto_filled", 0))
    return AssetListResponse(total=len(assets), assets=[AssetResponse(**a) for a in assets])


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def api_get_asset(asset_id: int):
    """获取单个资产详情"""
    asset = get_asset(asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found")
    if isinstance(asset.get("tags"), str):
        asset["tags"] = json.loads(asset["tags"])
    asset["auto_filled"] = bool(asset.get("auto_filled", 0))
    return AssetResponse(**asset)


@router.post("/assets", response_model=AssetResponse)
async def api_add_asset(body: AssetCreate):
    """添加核心资产，自动从知识库搜索补充描述"""
    fill = auto_fill_description(body.name)

    # 如果用户没提供描述，用自动补充的
    description = body.description or fill["description"]
    category = body.category if body.category != "general" else fill["category"]
    tags = body.tags or fill["tags"]
    auto_filled = bool(fill["auto_filled"])

    asset = add_asset(
        name=body.name,
        description=description,
        category=category,
        icon=body.icon,
        source_url=body.source_url,
        tags=tags,
        priority=body.priority,
        auto_filled=auto_filled,
    )
    if isinstance(asset.get("tags"), str):
        asset["tags"] = json.loads(asset["tags"])
    asset["auto_filled"] = bool(asset.get("auto_filled", 0))
    return AssetResponse(**asset)


@router.patch("/assets/{asset_id}", response_model=AssetResponse)
async def api_update_asset(asset_id: int, body: AssetUpdate):
    """更新资产信息"""
    existing = get_asset(asset_id)
    if not existing:
        raise HTTPException(404, "Asset not found")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        return AssetResponse(**existing)

    asset = update_asset(asset_id, **updates)
    if isinstance(asset.get("tags"), str):
        asset["tags"] = json.loads(asset["tags"])
    asset["auto_filled"] = bool(asset.get("auto_filled", 0))
    return AssetResponse(**asset)


@router.delete("/assets/{asset_id}")
async def api_remove_asset(asset_id: int):
    """移除资产"""
    success = remove_asset(asset_id)
    if not success:
        raise HTTPException(404, "Asset not found")
    return {"ok": True, "message": "Asset removed"}


@router.post("/assets/reorder")
async def api_reorder_assets(asset_ids: list[int]):
    """重排资产顺序（列表前面的排在前面）"""
    reorder_assets(asset_ids)
    return {"ok": True, "message": f"Reordered {len(asset_ids)} assets"}


@router.post("/assets/search-wiki")
async def api_search_wiki(query: str):
    """搜索知识库（用于添加资产时的预览）"""
    from .knowledge_search import search_wiki
    results = search_wiki(query, limit=5)
    return {"query": query, "matches": results}
