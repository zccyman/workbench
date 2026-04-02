"""Shared fixtures for wsl_path_bridge tests"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for storage tests."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def mock_data_dir(temp_data_dir):
    """Patch the DATA_DIR in storage module to use temp directory."""
    with patch("backend.tools.wsl_path_bridge.storage.DATA_DIR", temp_data_dir):
        yield temp_data_dir


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    return user


@pytest.fixture
def test_app(mock_user):
    """Create a FastAPI test client with mocked auth."""
    from fastapi.testclient import TestClient
    from fastapi import FastAPI, Depends
    from backend.tools.wsl_path_bridge.router import router

    app = FastAPI()

    def override_get_current_user():
        return mock_user

    from auth import deps

    app.dependency_overrides[deps.get_current_user] = override_get_current_user
    app.include_router(router, prefix="/api/tools/wsl_path_bridge")

    return TestClient(app)


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory with test files for directory listing tests."""
    tmpdir = tempfile.mkdtemp()
    base = Path(tmpdir)
    (base / "subdir1").mkdir()
    (base / "subdir2").mkdir()
    (base / "file1.txt").write_text("hello")
    (base / "file2.py").write_text("print('hi')")
    yield base
    shutil.rmtree(tmpdir, ignore_errors=True)
