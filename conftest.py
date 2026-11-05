"""
Aigaane test configuration and shared fixtures.
"""

import os
import pytest
from fastapi.testclient import TestClient
from api.main import app

# Default tests to the real engine, not the stub
os.environ.setdefault("AIGAANE_ENGINE_MODULE", "engine")

@pytest.fixture
def client():
    return TestClient(app)