"""
Gāndharva Neural Phrasing Endpoint
Route: POST /api/v1/gandharva/phrase
Pillar 1: Bounded neural swara phrase generation with deterministic fallback.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from aigaane.neural.schemas import ChandasInput, SwaraSequence, SwaraToken
from aigaane.neural.gemini_swara import GeminiSwaraEngine, deterministic_fallback
from aigaane.neural.guards import validate_sanskrit_text

router = APIRouter(prefix="/api/v1/gandharva", tags=["Gāndharva Neural"])

_engine = GeminiSwaraEngine()


class PhraseRequest(BaseModel):
    verse_text: str = Field(..., min_length=1, max_length=500)
    syllables: List[str] = Field(..., min_length=1, max_length=64)
    weights: List[str] = Field(..., min_length=1, max_length=64)
    target_raga: str = Field("Bhairav", max_length=50)


class PhraseResponse(BaseModel):
    status: str
    target_raga: str
    neural_used: bool
    confidence: float
    rationale: str
    swara_sequence: List[SwaraToken]


@router.post("/phrase", response_model=PhraseResponse)
async def phrase_verse(
    req: PhraseRequest,
    debug: bool = Query(False, description="Surface backend error details in rationale if fallback occurs")
) -> PhraseResponse:
    if not validate_sanskrit_text(req.verse_text):
        raise HTTPException(
            status_code=422,
            detail="Input text must be valid Sanskrit (Devanagari or IAST with diacritics).",
        )

    if len(req.syllables) != len(req.weights):
        raise HTTPException(
            status_code=422,
            detail=f"Syllable count ({len(req.syllables)}) does not match weights count ({len(req.weights)}).",
        )

    if not all(w in ("L", "G") for w in req.weights):
        raise HTTPException(
            status_code=422,
            detail="All weights must strictly be 'L' or 'G'.",
        )

    chandas_input = ChandasInput(
        verse_text=req.verse_text,
        syllables=req.syllables,
        weights=req.weights,
        target_raga=req.target_raga,
    )

    neural_res: Optional[SwaraSequence] = None
    try:
        neural_res = _engine.phrase(chandas_input)
    except Exception:
        neural_res = None

    if neural_res is not None:
        return PhraseResponse(
            status="success",
            target_raga=req.target_raga,
            neural_used=True,
            confidence=neural_res.confidence,
            rationale=neural_res.rationale,
            swara_sequence=neural_res.sequence,
        )

    fallback_res = deterministic_fallback(chandas_input)
    rationale_str = fallback_res.rationale
    if debug and _engine.last_error:
        rationale_str = f"Fallback ({_engine.last_error}) | {fallback_res.rationale}"

    return PhraseResponse(
        status="success",
        target_raga=req.target_raga,
        neural_used=False,
        confidence=fallback_res.confidence,
        rationale=rationale_str,
        swara_sequence=fallback_res.sequence,
    )
