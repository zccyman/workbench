import os
import shutil
import uuid
from typing import List
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.models import User
from auth.deps import get_current_user
from .storage import load_favorites, save_favorites

router = APIRouter(prefix="", tags=["wsl-path-bridge"])


class FileEntry(BaseModel):
    name: str
    isDirectory: bool
    path: str


class DirectoryResponse(BaseModel):
    entries: List[FileEntry]


class Favorite(BaseModel):
    id: str
    name: str
    windowsPath: str
    wslPath: str


class FavoritesResponse(BaseModel):
    favorites: List[Favorite]


class FavoriteCreate(BaseModel):
    name: str
    windowsPath: str
    wslPath: str


@router.get("/dir", response_model=DirectoryResponse)
def list_directory(path: str = "/", current_user: User = Depends(get_current_user)):
    try:
        target_path = Path(path)
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        entries = []
        for item in sorted(
            target_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
        ):
            try:
                entries.append(
                    FileEntry(
                        name=item.name,
                        isDirectory=item.is_dir(),
                        path=str(item),
                    )
                )
            except PermissionError:
                continue

        return DirectoryResponse(entries=entries)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/file")
def delete_file(path: str, current_user: User = Depends(get_current_user)):
    try:
        target_path = Path(path)
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            os.remove(target_path)

        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/favorites", response_model=FavoritesResponse)
def get_favorites(current_user: User = Depends(get_current_user)):
    data = load_favorites(current_user.id)
    return FavoritesResponse(favorites=data.get("favorites", []))


@router.post("/favorites", response_model=Favorite)
def add_favorite(fav: FavoriteCreate, current_user: User = Depends(get_current_user)):
    data = load_favorites(current_user.id)
    favorites = data.get("favorites", [])

    new_favorite = Favorite(
        id=str(uuid.uuid4()),
        name=fav.name,
        windowsPath=fav.windowsPath,
        wslPath=fav.wslPath,
    )
    favorites.append(new_favorite.model_dump())
    save_favorites(current_user.id, {"favorites": favorites})

    return new_favorite


@router.delete("/favorites/{fav_id}")
def delete_favorite(fav_id: str, current_user: User = Depends(get_current_user)):
    data = load_favorites(current_user.id)
    favorites = data.get("favorites", [])

    filtered = [f for f in favorites if f.get("id") != fav_id]
    if len(filtered) == len(favorites):
        raise HTTPException(status_code=404, detail="Favorite not found")

    save_favorites(current_user.id, {"favorites": filtered})
    return {"status": "deleted"}
