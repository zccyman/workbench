"""Shared fixtures for ai_session_manager tests"""

import pytest
import sqlite3
import os
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# Test fixtures for database


@pytest.fixture
def temp_db_path():
    """Create a temporary SQLite database with test schema."""
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = db_file.name
    db_file.close()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create test tables
    cursor.execute("""
        CREATE TABLE session (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            title TEXT,
            directory TEXT,
            time_created INTEGER,
            time_updated INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE project (
            id TEXT PRIMARY KEY,
            worktree TEXT,
            name TEXT,
            time_created INTEGER,
            time_updated INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE message (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            time_created INTEGER,
            data TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE part (
            id TEXT PRIMARY KEY,
            message_id TEXT,
            session_id TEXT,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def populated_db(temp_db_path):
    """Create a database with sample test data."""
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Insert test project
    cursor.execute(
        "INSERT INTO project (id, worktree, name, time_created, time_updated) VALUES (?, ?, ?, ?, ?)",
        (
            "proj_001",
            "/home/user/project1",
            "TestProject",
            1700000000000,
            1700000000000,
        ),
    )

    # Insert test sessions
    cursor.execute(
        "INSERT INTO session (id, project_id, title, directory, time_created, time_updated) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "sess_001",
            "proj_001",
            "Test Session 1",
            "/home/user/project1",
            1700000000000,
            1700000100000,
        ),
    )
    cursor.execute(
        "INSERT INTO session (id, project_id, title, directory, time_created, time_updated) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "sess_002",
            "proj_001",
            "Test Session 2",
            "/home/user/project2",
            1700000200000,
            1700000300000,
        ),
    )

    # Insert test messages
    cursor.execute(
        "INSERT INTO message (id, session_id, time_created, data) VALUES (?, ?, ?, ?)",
        (
            "msg_001",
            "sess_001",
            1700000000000,
            '{"role": "user", "content": "Hello world"}',
        ),
    )
    cursor.execute(
        "INSERT INTO message (id, session_id, time_created, data) VALUES (?, ?, ?, ?)",
        (
            "msg_002",
            "sess_001",
            1700000050000,
            '{"role": "assistant", "content": "Hi there! How can I help?"}',
        ),
    )
    cursor.execute(
        "INSERT INTO message (id, session_id, time_created, data) VALUES (?, ?, ?, ?)",
        (
            "msg_003",
            "sess_002",
            1700000200000,
            '{"role": "user", "content": "Fix the bug in router.py"}',
        ),
    )

    # Insert test parts
    cursor.execute(
        "INSERT INTO part (id, message_id, session_id, data) VALUES (?, ?, ?, ?)",
        ("part_001", "msg_002", "sess_001", '{"text": "Here is the solution"}'),
    )

    conn.commit()
    conn.close()

    yield temp_db_path


@pytest.fixture
def mock_db(populated_db):
    """Mock the database connection to use a temporary test database."""
    with patch(
        "backend.tools.ai_session_manager.config.Config.KILO_CODE_DB_PATH", populated_db
    ):
        with patch(
            "backend.tools.ai_session_manager.config.Config.OPENCODE_DB_PATH",
            populated_db,
        ):
            from backend.tools.ai_session_manager.database import get_db, Database

            yield Database(populated_db)


@pytest.fixture
def mock_config(temp_db_path):
    """Mock config to point to test database."""
    with patch(
        "backend.tools.ai_session_manager.config.Config.KILO_CODE_DB_PATH", temp_db_path
    ):
        with patch(
            "backend.tools.ai_session_manager.config.Config.OPENCODE_DB_PATH",
            temp_db_path,
        ):
            yield


@pytest.fixture
def test_app():
    """Create a FastAPI test client for the ai_session_manager router."""
    from fastapi.testclient import TestClient
    from fastapi import FastAPI

    app = FastAPI()

    # Import and include the router
    from backend.tools.ai_session_manager.router import router as asm_router

    app.include_router(asm_router, prefix="/api/tools/ai_session_manager")

    return TestClient(app)
