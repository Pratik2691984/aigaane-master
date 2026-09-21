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