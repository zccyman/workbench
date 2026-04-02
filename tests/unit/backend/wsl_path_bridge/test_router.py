"""Tests for wsl_path_bridge API router"""

import json
from pathlib import Path


def test_list_directory(test_app, temp_test_dir):
    """GET /dir should list directory contents."""
    response = test_app.get(
        "/api/tools/wsl_path_bridge/dir", params={"path": str(temp_test_dir)}
    )
    assert response.status_code == 200

    data = response.json()
    entries = data["entries"]
    names = [e["name"] for e in entries]

    assert "subdir1" in names
    assert "subdir2" in names
    assert "file1.txt" in names
    assert "file2.py" in names


def test_list_directory_directories_first(test_app, temp_test_dir):
    """GET /dir should list directories before files."""
    response = test_app.get(
        "/api/tools/wsl_path_bridge/dir", params={"path": str(temp_test_dir)}
    )
    data = response.json()
    entries = data["entries"]

    # Directories should come first
    dir_entries = [e for e in entries if e["isDirectory"]]
    file_entries = [e for e in entries if not e["isDirectory"]]

    assert len(dir_entries) == 2
    assert len(file_entries) == 2

    # Verify directories appear before files in the list
    first_file_idx = next(i for i, e in enumerate(entries) if not e["isDirectory"])
    last_dir_idx = max(i for i, e in enumerate(entries) if e["isDirectory"])
    assert last_dir_idx < first_file_idx


def test_list_directory_not_found(test_app):
    """GET /dir should return 404 for non-existent path."""
    response = test_app.get(
        "/api/tools/wsl_path_bridge/dir", params={"path": "/nonexistent/path/12345"}
    )
    assert response.status_code == 404


def test_get_favorites_empty(test_app, mock_data_dir):
    """GET /favorites should return empty list initially."""
    response = test_app.get("/api/tools/wsl_path_bridge/favorites")
    assert response.status_code == 200

    data = response.json()
    assert data["favorites"] == []


def test_add_favorite(test_app, mock_data_dir):
    """POST /favorites should add a new favorite."""
    payload = {
        "name": "My Project",
        "windowsPath": "G:\\Projects\\MyProject",
        "wslPath": "/mnt/g/Projects/MyProject",
    }

    response = test_app.post("/api/tools/wsl_path_bridge/favorites", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "My Project"
    assert data["windowsPath"] == "G:\\Projects\\MyProject"
    assert data["wslPath"] == "/mnt/g/Projects/MyProject"
    assert "id" in data


def test_add_and_get_favorite(test_app, mock_data_dir):
    """Added favorite should be retrievable via GET."""
    payload = {
        "name": "Test Dir",
        "windowsPath": "C:\\Users\\test",
        "wslPath": "/mnt/c/Users/test",
    }

    test_app.post("/api/tools/wsl_path_bridge/favorites", json=payload)

    response = test_app.get("/api/tools/wsl_path_bridge/favorites")
    data = response.json()

    assert len(data["favorites"]) == 1
    assert data["favorites"][0]["name"] == "Test Dir"


def test_delete_favorite(test_app, mock_data_dir):
    """DELETE /favorites/{id} should remove the favorite."""
    payload = {
        "name": "To Delete",
        "windowsPath": "D:\\Temp",
        "wslPath": "/mnt/d/Temp",
    }

    add_response = test_app.post("/api/tools/wsl_path_bridge/favorites", json=payload)
    fav_id = add_response.json()["id"]

    del_response = test_app.delete(f"/api/tools/wsl_path_bridge/favorites/{fav_id}")
    assert del_response.status_code == 200
    assert del_response.json()["status"] == "deleted"

    get_response = test_app.get("/api/tools/wsl_path_bridge/favorites")
    assert len(get_response.json()["favorites"]) == 0


def test_delete_nonexistent_favorite(test_app, mock_data_dir):
    """DELETE /favorites/{id} should return 404 for non-existent id."""
    response = test_app.delete("/api/tools/wsl_path_bridge/favorites/nonexistent-id")
    assert response.status_code == 404


def test_delete_file(test_app, temp_test_dir):
    """DELETE /file should remove a file."""
    target = temp_test_dir / "file1.txt"
    assert target.exists()

    response = test_app.delete(
        "/api/tools/wsl_path_bridge/file", params={"path": str(target)}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    assert not target.exists()


def test_delete_directory(test_app, temp_test_dir):
    """DELETE /file should remove a directory recursively."""
    target = temp_test_dir / "subdir1"
    (target / "nested.txt").write_text("nested")
    assert target.exists()

    response = test_app.delete(
        "/api/tools/wsl_path_bridge/file", params={"path": str(target)}
    )
    assert response.status_code == 200
    assert not target.exists()


def test_delete_nonexistent_file(test_app):
    """DELETE /file should return 404 for non-existent path."""
    response = test_app.delete(
        "/api/tools/wsl_path_bridge/file", params={"path": "/nonexistent/file.txt"}
    )
    assert response.status_code == 404
