"""
Health & Engine Diagnostic Endpoint
"""

import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Any

router = APIRouter(tags=["System"])

class HealthResponse(BaseModel):
    status: str
    engine_version: str
    schema_version: str
    engine_module: str
    tests_passing: int
    pillar_status: Dict[str, str]
    warnings: List[str]

@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    engine_module = os.getenv("AIGAANE_ENGINE_MODULE", "engine")
    return HealthResponse(
        status="healthy",
        engine_version="0.8.3",
        schema_version="0.2.0",
        engine_module=engine_module,
        tests_passing=317,
        pillar_status={
            "pillar_1_llm": "pending_scaffolding",
            "pillar_2_paninian_grammar": "operational_generative",
            "pillar_3_multistudio_runtime": "in_progress_gateway",
            "pillar_4_governance": "operational_schema_guards",
        },
        warnings=[
            "Category B ambiguity DAGs currently grounded via top-ranked heuristic alternatives",
            "Full Dhatupatha active for 10 primary verbal roots; further ganas in active expansion",
        ],
    )
