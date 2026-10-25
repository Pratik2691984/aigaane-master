"""
conftest.py
Ensures repo root and api/ are on sys.path before pytest collects tests.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = ROOT / "api"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(API) not in sys.path:
    sys.path.insert(0, str(API))

# --- shared test fixtures -------------------------------------------------
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Module-scoped ASGI test client against api/kernel_api.py:app."""
    from kernel_api import app
    with TestClient(app) as c:
        yield c