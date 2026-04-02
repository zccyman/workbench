"""Tests for theme API endpoints"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture
def theme_test_app():
    """Create a FastAPI test client for theme endpoints."""
    from fastapi.testclient import TestClient
    from fastapi import FastAPI, Depends
    from auth.deps import get_current_user

    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.username = "testuser"

    tmpdir = tempfile.mkdtemp()

    # Patch THEME_DIR before importing main
    with patch("main.THEME_DIR", Path(tmpdir)):
        from main import app, _theme_file

        app.dependency_overrides[get_current_user] = lambda: mock_user
        client = TestClient(app)
        yield client

    app.dependency_overrides.clear()


def test_get_theme_default(theme_test_app):
    """GET /api/theme should return 'light' by default."""
    response = theme_test_app.get("/api/theme")
    assert response.status_code == 200
    assert response.json()["theme"] == "light"


def test_set_and_get_dark_theme(theme_test_app):
    """POST /api/theme should persist theme choice."""
    response = theme_test_app.post("/api/theme", json={"theme": "dark"})
    assert response.status_code == 200
    assert response.json()["theme"] == "dark"

    get_response = theme_test_app.get("/api/theme")
    assert get_response.json()["theme"] == "dark"


def test_set_light_theme(theme_test_app):
    """POST /api/theme should allow switching back to light."""
    theme_test_app.post("/api/theme", json={"theme": "dark"})
    theme_test_app.post("/api/theme", json={"theme": "light"})

    response = theme_test_app.get("/api/theme")
    assert response.json()["theme"] == "light"


def test_set_invalid_theme(theme_test_app):
    """POST /api/theme should reject invalid theme values."""
    response = theme_test_app.post("/api/theme", json={"theme": "blue"})
    assert response.status_code == 400
