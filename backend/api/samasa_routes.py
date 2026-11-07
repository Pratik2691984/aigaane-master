"""
Samāsa (compound) domain routes.

Exposes the same deterministic engine that `/api/v3/aigaane/parse` uses,
but under a dedicated prefix so frontend components can call
`/api/v3/samasa/split` directly.

Both `/api/v1/samasa/*` and `/api/v3/samasa/*` mount this router in
`backend/api/main.py` — identical handlers, zero drift.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.engine.adapter import EngineAdapter
from backend.engine.pydantic_models import KernelEnvelope
from backend.critic.gatekeeper import CegarGatekeeper

router = APIRouter(tags=["samasa"])

# Same adapter + critic instances the main parse route uses
_adapter = EngineAdapter()
_critic = CegarGatekeeper()


class SamasaRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Sanskrit compound in SLP1, IAST, or Devanagari")


@router.post("/split", response_model=KernelEnvelope)
async def split_samasa(payload: SamasaRequest):
    """
    Decomposes a Sanskrit compound into constituents, classifies the samāsa
    type, cites governing Pāṇinian sūtras, and generates vigraha.

    Returns the same KernelEnvelope contract as `/api/v3/aigaane/parse`.
    """
    try:
        envelope = _adapter.parse(payload.text)
        return _critic.verify(envelope)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Samāsa decomposition failed: {str(e)}",
        )


@router.get("/categories")
async def list_samasa_categories():
    """
    Returns the Pāṇinian samāsa classification taxonomy supported by the engine.
    """
    return {
        "status": "ok",
        "categories": [
            {"id": "avyayibhava", "name": "Avyayībhāva", "sutra": "2.1.5"},
            {"id": "tatpurusha", "name": "Tatpuruṣa", "sutra": "2.1.22"},
            {"id": "karmadharaya", "name": "Karmadhāraya", "sutra": "2.1.57"},
            {"id": "dvigu", "name": "Dvigu", "sutra": "2.1.52"},
            {"id": "dvandva", "name": "Dvandva", "sutra": "2.2.29"},
            {"id": "bahuvrihi", "name": "Bahuvrīhi", "sutra": "2.2.24"},
        ],
    }