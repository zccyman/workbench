"""测试工具自动发现机制"""
import json
from pathlib import Path
from unittest.mock import patch


def test_meta_json_exists():
    """wsl_path_bridge 的 meta.json 应该存在且合法"""
    meta_path = Path(__file__).parent.parent.parent.parent / "backend" / "tools" / "wsl_path_bridge" / "meta.json"
    assert meta_path.exists(), "meta.json 不存在"

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert "name" in meta
    assert "id" in meta
    assert "version" in meta
    assert meta["id"] == "wsl_path_bridge"


def test_meta_json_fields():
    """meta.json 应包含必要字段"""
    meta_path = Path(__file__).parent.parent.parent.parent / "backend" / "tools" / "wsl_path_bridge" / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    required_fields = ["name", "id", "description", "icon", "category", "version"]
    for field in required_fields:
        assert field in meta, f"缺少字段: {field}"


def test_router_exists():
    """wsl_path_bridge 的 router.py 应该存在"""
    router_path = Path(__file__).parent.parent.parent.parent / "backend" / "tools" / "wsl_path_bridge" / "router.py"
    assert router_path.exists(), "router.py 不存在"
