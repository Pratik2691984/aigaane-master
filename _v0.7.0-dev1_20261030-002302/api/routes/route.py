"""
Route Endpoint — Multi-Studio Intent Classification & Governance Routing
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from api.deps import get_engine

router = APIRouter(prefix="/api/v1", tags=["Routing"])

_POLICY_PATH = Path(__file__).resolve().parents[2] / "schemas" / "router_policy.json"
_DEFAULT_POLICY: Optional[Dict[str, Any]] = None

def _get_default_policy() -> Dict[str, Any]:
    global _DEFAULT_POLICY
    if _DEFAULT_POLICY is None:
        with open(_POLICY_PATH, "r", encoding="utf-8") as f:
            _DEFAULT_POLICY = json.load(f)
    return _DEFAULT_POLICY

class RouteRequest(BaseModel):
    doc: Dict[str, Any] = Field(..., description="Parsed Sanskrit document conforming to sanskrit_contract.json")
    policy: Optional[Dict[str, Any]] = Field(None, description="Optional router policy override")
    intent_hint: Optional[str] = Field(None, description="Optional intent hint")

@router.post("/route", response_model=Dict[str, Any])
def route_decision(req: RouteRequest, engine=Depends(get_engine)) -> Dict[str, Any]:
    policy = req.policy or _get_default_policy()
    try:
        decision = engine.route(req.doc, policy, intent_hint=req.intent_hint)
        if decision is None:
            raise HTTPException(status_code=422, detail="Routing decision could not be reached.")
        return decision
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Routing failure: {str(e)}")
