import json
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import engine, Base
from auth.models import User
from auth.router import router as auth_router
from auth.deps import get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workbench", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_origin_regex=r"chrome-extension://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


# === 工具自动发现机制 ===


def discover_tools():
    """扫描 tools/ 目录，自动发现并注册所有工具"""
    tools_dir = Path(__file__).parent / "tools"
    discovered = []

    for tool_path in tools_dir.iterdir():
        if not tool_path.is_dir():
            continue
        if tool_path.name.startswith("_") or tool_path.name.startswith("."):
            continue

        router_file = tool_path / "router.py"
        meta_file = tool_path / "meta.json"

        if not router_file.exists() or not meta_file.exists():
            continue

        # 读取 meta.json
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            print(f"[Workbench] ⚠️ 跳过 {tool_path.name}: meta.json 解析失败")
            continue

        tool_id = meta.get("id", tool_path.name)

        # 动态导入 router
        module_path = f"tools.{tool_path.name}.router"
        try:
            import importlib

            module = importlib.import_module(module_path)
            router = getattr(module, "router", None)
            if router:
                app.include_router(
                    router,
                    prefix=f"/api/tools/{tool_id}",
                    tags=[meta.get("name", tool_id)],
                )
                print(
                    f"[Workbench] ✅ 注册工具: {meta.get('name', tool_id)} ({tool_id})"
                )
            else:
                print(
                    f"[Workbench] ⚠️ 跳过 {tool_path.name}: router.py 中没有找到 router"
                )
                continue
        except Exception as e:
            print(f"[Workbench] ⚠️ 跳过 {tool_path.name}: 导入失败 - {e}")
            continue

        discovered.append(meta)

    return discovered


# 执行工具发现
_tools_registry = discover_tools()


@app.get("/api/tools")
async def list_tools():
    """返回所有已注册的工具列表"""
    return _tools_registry


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


# === 主题 API ===

THEME_DIR = Path(__file__).parent / "data"
THEME_DIR.mkdir(exist_ok=True)


def _theme_file(user_id: int) -> Path:
    return THEME_DIR / f"theme_{user_id}.json"


def _load_theme(user_id: int) -> str:
    path = _theme_file(user_id)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("theme", "light")
        except (json.JSONDecodeError, Exception):
            pass
    return "light"


def _save_theme(user_id: int, theme: str):
    path = _theme_file(user_id)
    path.write_text(json.dumps({"theme": theme}), encoding="utf-8")


class ThemeResponse(BaseModel):
    theme: str


class ThemeUpdate(BaseModel):
    theme: str


@app.get("/api/theme", response_model=ThemeResponse)
def get_theme(current_user: User = Depends(get_current_user)):
    return ThemeResponse(theme=_load_theme(current_user.id))


@app.post("/api/theme", response_model=ThemeResponse)
def update_theme(update: ThemeUpdate, current_user: User = Depends(get_current_user)):
    if update.theme not in ("light", "dark"):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="theme must be 'light' or 'dark'")
    _save_theme(current_user.id, update.theme)
    return ThemeResponse(theme=update.theme)
