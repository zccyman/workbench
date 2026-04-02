"""Tests for tab_contents routes"""
import pytest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "backend"))

from fastapi.testclient import TestClient
from fastapi import FastAPI
from tools.ai_session_manager.database import Database


def create_test_app_with_tab_db(tab_db_path, source_db_path):
    """Create test app with separate app DB for tab contents."""
    source_db = Database(source_db_path)

    for mod_name in list(sys.modules.keys()):
        if 'ai_session_manager' in mod_name:
            del sys.modules[mod_name]

    import tools.ai_session_manager.database as db_mod
    db_mod.db_kilo = source_db
    db_mod.db_opencode = source_db

    # Set APP_DB_PATH env var so get_app_db uses our test db
    os.environ["APP_DB_PATH"] = tab_db_path

    from tools.ai_session_manager.router import router as asm_router
    app = FastAPI()
    app.include_router(asm_router, prefix="/api/tools/ai_session_manager")

    return TestClient(app)


class TestTabContentsRoutes:
    @pytest.fixture
    def tab_db_path(self):
        db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        db_path = db_file.name
        db_file.close()
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
        # Clean up env var
        os.environ.pop("APP_DB_PATH", None)

    def test_create_tab_content(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        response = client.post(
            "/api/tools/ai_session_manager/tab-contents",
            json={
                "title": "Test Tab",
                "url": "http://example.com",
                "markdown": "# Test Content",
                "messages": [{"role": "user", "content": "Hello"}],
                "source": "tabbit",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Tab"
        assert data["id"].startswith("tab_")

    def test_list_tab_contents_empty(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        response = client.get("/api/tools/ai_session_manager/tab-contents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_tab_contents(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        client.post(
            "/api/tools/ai_session_manager/tab-contents",
            json={"title": "Test Tab", "markdown": "# Content", "messages": []},
        )
        response = client.get("/api/tools/ai_session_manager/tab-contents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_tab_content(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        create_resp = client.post(
            "/api/tools/ai_session_manager/tab-contents",
            json={"title": "Test Tab", "markdown": "# Content", "messages": []},
        )
        content_id = create_resp.json()["id"]
        response = client.get(f"/api/tools/ai_session_manager/tab-contents/{content_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == content_id

    def test_get_tab_content_not_found(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        response = client.get("/api/tools/ai_session_manager/tab-contents/nonexistent")
        assert response.status_code == 404

    def test_update_tab_content(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        create_resp = client.post(
            "/api/tools/ai_session_manager/tab-contents",
            json={"title": "Original", "markdown": "# Original", "messages": []},
        )
        content_id = create_resp.json()["id"]
        response = client.put(
            f"/api/tools/ai_session_manager/tab-contents/{content_id}",
            json={"title": "Updated", "markdown": "# Updated", "messages": []},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"

    def test_update_tab_content_not_found(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        response = client.put(
            "/api/tools/ai_session_manager/tab-contents/nonexistent",
            json={"title": "Test", "markdown": "# Test", "messages": []},
        )
        assert response.status_code == 404

    def test_delete_tab_content(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        create_resp = client.post(
            "/api/tools/ai_session_manager/tab-contents",
            json={"title": "To Delete", "markdown": "# Content", "messages": []},
        )
        content_id = create_resp.json()["id"]
        response = client.delete(f"/api/tools/ai_session_manager/tab-contents/{content_id}")
        assert response.status_code == 200
        get_resp = client.get(f"/api/tools/ai_session_manager/tab-contents/{content_id}")
        assert get_resp.status_code == 404

    def test_delete_tab_content_not_found(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        response = client.delete("/api/tools/ai_session_manager/tab-contents/nonexistent")
        assert response.status_code == 404

    def test_search_tab_contents(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        client.post(
            "/api/tools/ai_session_manager/tab-contents",
            json={"title": "Searchable Tab", "markdown": "# Searchable Content", "messages": []},
        )
        response = client.get("/api/tools/ai_session_manager/tab-contents/search?q=Searchable")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_search_tab_contents_no_results(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        response = client.get("/api/tools/ai_session_manager/tab-contents/search?q=nonexistent_xyz")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_export_tab_content_markdown(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        create_resp = client.post(
            "/api/tools/ai_session_manager/tab-contents",
            json={"title": "Export Tab", "markdown": "# Export Content", "messages": []},
        )
        content_id = create_resp.json()["id"]
        response = client.get(f"/api/tools/ai_session_manager/tab-contents/{content_id}/markdown")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Export Tab"
        assert data["markdown"] == "# Export Content"

    def test_export_tab_contents_to_directory(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        client.post(
            "/api/tools/ai_session_manager/tab-contents",
            json={"title": "Export Tab", "markdown": "# Content", "messages": []},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            response = client.post(
                "/api/tools/ai_session_manager/tab-contents/export-to-directory",
                json={"output_dir": tmpdir},
            )
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data

    def test_tab_export_progress_not_found(self, temp_db_path, tab_db_path):
        client = create_test_app_with_tab_db(tab_db_path, temp_db_path)
        response = client.get("/api/tools/ai_session_manager/tab-contents/export-to-directory/progress/nonexistent")
        assert response.status_code == 404
