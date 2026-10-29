"""
Aigaane test configuration and shared fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    return TestClient(app)
