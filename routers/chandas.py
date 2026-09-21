"""
routers/chandas.py
POST /api/v3/chandas/scan and /api/v3/chandas/anustubh
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from engines.chandas.scansion import scan
from engines.chandas.anustubh import validate_anustubh

router = APIRouter(prefix="/api/v3/chandas", tags=["Chandas Engine"])


class ScanRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, examples=["rāma"])


class SyllableModel(BaseModel):
    text: str
    weight: str
    position: int


class ScanResponse(BaseModel):
    input: str
    syllables: list[SyllableModel]
    pattern: str
    length: int


class AnustubhRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class PadaModel(BaseModel):
    index: int
    text_pattern: str
    variety: str | None
    is_valid: bool
    reason: str | None


class AnustubhResponse(BaseModel):
    input: str
    is_valid: bool
    padas: list[PadaModel]
    errors: list[str]


@router.post("/scan", response_model=ScanResponse, status_code=status.HTTP_200_OK)
def scan_endpoint(payload: ScanRequest) -> ScanResponse:
    try:
        result = scan(payload.text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Scansion failed: {e}")
    return ScanResponse(
        input=result.input,
        syllables=[SyllableModel(text=s.text, weight=s.weight, position=s.position)
                   for s in result.syllables],
        pattern=result.pattern,
        length=result.length,
    )


@router.post("/anustubh", response_model=AnustubhResponse, status_code=status.HTTP_200_OK)
def anustubh_endpoint(payload: AnustubhRequest) -> AnustubhResponse:
    result = validate_anustubh(payload.text)
    return AnustubhResponse(
        input=result.input,
        is_valid=result.is_valid,
        padas=[PadaModel(index=p.index, text_pattern=p.text_pattern,
                         variety=p.variety, is_valid=p.is_valid, reason=p.reason)
               for p in result.padas],
        errors=result.errors,
    )
