"""Tests for search and stats routes"""
import pytest
import sys
import sqlite3
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


class TestSearchRoutes:
    def test_search_sessions(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/search?q=Hello")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_sessions_no_results(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/search?q=nonexistent_query_xyz")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_search_in_session(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/search/sessions/sess_001?q=Hello")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_has_highlights(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/search?q=Hello")
        data = response.json()
        for result in data:
            assert "highlights" in result


class TestStatsRoutes:
    def test_stats_overview(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/stats/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 2
        assert data["total_messages"] == 3
        assert data["total_projects"] == 1
        assert data["total_parts"] == 1

    def test_stats_trends(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/stats/trends")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_stats_trends_with_days(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/stats/trends?days=7")
        assert response.status_code == 200

    def test_stats_by_project(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/stats/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["project_id"] == "proj_001"
        assert data[0]["session_count"] == 2

    def test_message_stats(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/stats/messages")
        assert response.status_code == 200
        data = response.json()
        assert "avg_messages_per_session" in data
        assert "total_parts" in data
        assert data["total_parts"] == 1


class TestProjectsRoutes:
    def test_list_projects(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/projects")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "TestProject"

    def test_get_project(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/projects/proj_001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "proj_001"
        assert data["session_count"] == 2

    def test_get_project_not_found(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/projects/nonexistent")
        assert response.status_code == 404

    def test_project_name_fallback(self, temp_db_path):
        conn = sqlite3.connect(temp_db_path)
        conn.execute("INSERT INTO project (id, worktree, name) VALUES (?, ?, ?)",
                     ("proj_002", "/home/user/unnamed", None))
        conn.commit()
        conn.close()
        client = create_test_app(temp_db_path)
        response = client.get("/api/tools/ai_session_manager/projects/proj_002")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "unnamed"


class TestSourcesRoutes:
    def test_get_sources(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sources")
        assert response.status_code == 200
        data = response.json()
        assert "available" in data
        assert "default" in data
        assert data["default"] == "kilo"

    def test_get_available_sources(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sources/available")
        assert response.status_code == 200
