"""
Parse Endpoint — Generative Paninian Morphological Parsing
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from api.deps import get_engine

router = APIRouter(prefix="/api/v1", tags=["Analysis"])

class ParseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Sanskrit text in IAST, Devanāgarī, or ITRANS")
    intent_hint: Optional[str] = Field(None, description="Optional intent hint to guide processing")

@router.post("/parse", response_model=Dict[str, Any])
def parse_sanskrit(req: ParseRequest, engine=Depends(get_engine)) -> Dict[str, Any]:
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Text cannot be empty.")
    
    doc = engine.parse(text)
    if doc is None:
        raise HTTPException(status_code=422, detail=f"Engine could not parse input: '{req.text}'")
    
    return doc
