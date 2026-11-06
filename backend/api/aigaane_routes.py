from fastapi import APIRouter, HTTPException
from backend.engine.pydantic_models import KernelEnvelope
from backend.engine.adapter import EngineAdapter

router = APIRouter()
adapter = EngineAdapter()


@router.post("/parse", response_model=KernelEnvelope)
async def parse_sanskrit(payload: dict):
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' field")
    return adapter.parse(text)