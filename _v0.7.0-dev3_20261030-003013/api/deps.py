"""
Dependency injection for Aigaane Core API.
"""

import os
import importlib

def get_engine():
    """Dynamically loads and returns the configured Sanskrit grammar engine."""
    mod_name = os.getenv("AIGAANE_ENGINE_MODULE", "engine")
    mod = importlib.import_module(mod_name)
    return mod
