"""Tests for export routes"""
import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "backend"))

from fastapi.testclient import TestClient
from fastapi import FastAPI
from tools.ai_session_manager.database import Database


def create_test_app(db_path):
    """Create test app with database globals patched."""
    test_db = Database(db_path)
    for mod_name in list(sys.modules.keys()):
        if 'ai_session_manager' in mod_name:
            del sys.modules[mod_name]
    import tools.ai_session_manager.database as db_mod
    db_mod.db_kilo = test_db
    db_mod.db_opencode = test_db
    from tools.ai_session_manager.router import router as asm_router
    app = FastAPI()
    app.include_router(asm_router, prefix="/api/tools/ai_session_manager")
    return TestClient(app)


class TestExportRoutes:
    def test_export_markdown(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/export/markdown/sess_001")
        assert response.status_code == 200
        data = response.text
        assert "Test Session 1" in data

    def test_export_markdown_not_found(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/export/markdown/nonexistent")
        assert response.status_code == 404

    def test_export_json(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/export/json/sess_001")
        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        assert "messages" in data

    def test_export_json_not_found(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/export/json/nonexistent")
        assert response.status_code == 404

    def test_export_to_directory(self, populated_db):
        client = create_test_app(populated_db)
        with tempfile.TemporaryDirectory() as tmpdir:
            response = client.post(
                "/api/tools/ai_session_manager/export/to-directory",
                json={"output_dir": tmpdir, "source": "kilo"},
            )
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert "message" in data

    def test_export_progress_not_found(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/export/to-directory/progress/nonexistent")
        assert response.status_code == 404
