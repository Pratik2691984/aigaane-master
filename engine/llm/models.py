"""
engine/llm/models.py
Declarative Model Registry and Quota Metadata for Sanskrit Generation Agents
"""
from typing import List, Dict, Any

CANDIDATE_MODELS: List[Dict[str, Any]] = [
    {
        "name": "gemini-3.5-flash-lite",
        "tier": "fast_free",
        "rpd_limit": 20,
        "role": "primary_composition",
        "temperature": 0.2
    },
    {
        "name": "gemini-2.0-flash",
        "tier": "standard_free",
        "rpd_limit": 20,
        "role": "fallback_composition",
        "temperature": 0.2
    },
    {
        "name": "gemini-2.0-flash-lite",
        "tier": "light_free",
        "rpd_limit": 20,
        "role": "secondary_fallback",
        "temperature": 0.2
    },
    {
        "name": "gemini-3.6-flash",
        "tier": "flagship_free",
        "rpd_limit": 20,
        "role": "high_precision_fallback",
        "temperature": 0.2
    }
]

def get_model_names() -> List[str]:
    return [m["name"] for m in CANDIDATE_MODELS]
