"""Tests for wsl_path_bridge storage module"""

import json
from pathlib import Path


def test_load_favorites_empty(mock_data_dir):
    """load_favorites should return empty list when no file exists."""
    from backend.tools.wsl_path_bridge.storage import load_favorites

    result = load_favorites(user_id=999)
    assert result == {"favorites": []}


def test_save_and_load_favorites(mock_data_dir):
    """save_favorites should persist data, load_favorites should retrieve it."""
    from backend.tools.wsl_path_bridge.storage import save_favorites, load_favorites

    user_id = 1
    data = {
        "favorites": [
            {
                "id": "abc",
                "name": "Projects",
                "windowsPath": "G:\\Projects",
                "wslPath": "/mnt/g/Projects",
            }
        ]
    }

    save_favorites(user_id, data)
    result = load_favorites(user_id)

    assert result == data


def test_favorites_per_user_isolation(mock_data_dir):
    """Different users should have separate favorites."""
    from backend.tools.wsl_path_bridge.storage import save_favorites, load_favorites

    save_favorites(1, {"favorites": [{"id": "u1", "name": "User1 Fav"}]})
    save_favorites(2, {"favorites": [{"id": "u2", "name": "User2 Fav"}]})

    result1 = load_favorites(1)
    result2 = load_favorites(2)

    assert result1["favorites"][0]["id"] == "u1"
    assert result2["favorites"][0]["id"] == "u2"


def test_save_favorites_creates_data_dir(mock_data_dir):
    """save_favorites should work even if data directory needs to be created."""
    from backend.tools.wsl_path_bridge.storage import save_favorites, load_favorites

    save_favorites(42, {"favorites": [{"id": "test"}]})
    result = load_favorites(42)

    assert len(result["favorites"]) == 1


def test_load_json_handles_invalid_json(mock_data_dir):
    """load_json should handle corrupted JSON files gracefully."""
    from backend.tools.wsl_path_bridge.storage import load_json

    bad_file = mock_data_dir / "bad.json"
    bad_file.write_text("{invalid json", encoding="utf-8")

    # Should raise JSONDecodeError
    import pytest

    with pytest.raises(json.JSONDecodeError):
        load_json(bad_file, default={})


def test_load_json_returns_default_for_missing(mock_data_dir):
    """load_json should return default when file doesn't exist."""
    from backend.tools.wsl_path_bridge.storage import load_json

    missing = mock_data_dir / "nonexistent.json"
    result = load_json(missing, default={"key": "value"})

    assert result == {"key": "value"}


def test_save_json_creates_file(mock_data_dir):
    """save_json should create a file with correct content."""
    from backend.tools.wsl_path_bridge.storage import save_json

    target = mock_data_dir / "test.json"
    data = {"name": "test", "value": 123}

    save_json(target, data)

    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == data
