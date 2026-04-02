"""Tests for sessions and messages routes"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "backend"))

from fastapi.testclient import TestClient
from fastapi import FastAPI
from tools.ai_session_manager.database import Database


def create_test_app(db_path):
    """Create test app with database globals patched."""
    test_db = Database(db_path)

    # Remove all cached ai_session_manager modules
    for mod_name in list(sys.modules.keys()):
        if 'ai_session_manager' in mod_name:
            del sys.modules[mod_name]

    # Now import and patch
    import tools.ai_session_manager.database as db_mod
    db_mod.db_kilo = test_db
    db_mod.db_opencode = test_db

    from tools.ai_session_manager.router import router as asm_router
    app = FastAPI()
    app.include_router(asm_router, prefix="/api/tools/ai_session_manager")
    return TestClient(app)


class TestSessionsRoutes:
    def test_list_sessions(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_list_sessions_with_limit(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_list_sessions_with_project_id(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions?project_id=proj_001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_sessions_by_source(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions?source=kilo")
        assert response.status_code == 200

    def test_get_session(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions/sess_001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "sess_001"
        assert data["title"] == "Test Session 1"

    def test_get_session_not_found(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions/nonexistent")
        assert response.status_code == 404

    def test_get_sessions_by_project(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions/by-project/proj_001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_sessions_by_project_empty(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions/by-project/nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_sessions_by_date(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions/by-date/1700000000000")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_session_has_message_count(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions/sess_001")
        data = response.json()
        assert "message_count" in data
        assert data["message_count"] == 2

    def test_session_has_project_name(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/sessions/sess_001")
        data = response.json()
        assert data["project_name"] == "TestProject"


class TestMessagesRoutes:
    def test_get_messages_by_session(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/messages/session/sess_001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_messages_by_session_empty(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/messages/session/nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_get_message(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/messages/msg_001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "msg_001"

    def test_get_message_not_found(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/messages/nonexistent")
        assert response.status_code == 404

    def test_get_message_with_parts(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/messages/msg_002")
        assert response.status_code == 200
        data = response.json()
        assert "parts" in data
        assert len(data["parts"]) == 1

    def test_get_messages_with_parts(self, populated_db):
        client = create_test_app(populated_db)
        response = client.get("/api/tools/ai_session_manager/messages/session/sess_001/with-parts")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for msg in data:
            assert "parts" in msg
            assert "parsed_data" in msg
