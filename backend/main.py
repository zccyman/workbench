import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from auth.models import User
from auth.router import router as auth_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workbench", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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
                app.include_router(router, prefix=f"/api/tools/{tool_id}", tags=[meta.get("name", tool_id)])
                print(f"[Workbench] ✅ 注册工具: {meta.get('name', tool_id)} ({tool_id})")
            else:
                print(f"[Workbench] ⚠️ 跳过 {tool_path.name}: router.py 中没有找到 router")
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
