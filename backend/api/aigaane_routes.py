from fastapi import APIRouter, HTTPException
from backend.engine.pydantic_models import KernelEnvelope
from backend.engine.adapter import EngineAdapter
from backend.critic.gatekeeper import CegarGatekeeper

router = APIRouter()
adapter = EngineAdapter()
critic = CegarGatekeeper()

@router.post("/parse", response_model=KernelEnvelope)
async def parse_sanskrit(payload: dict):
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' field")
    
    # 1. Run the Legacy Engine via Adapter
    envelope = adapter.parse(text)
    
    # 2. Pass through the Deterministic Critic
    verified_envelope = critic.verify(envelope)
    
    return verified_envelope