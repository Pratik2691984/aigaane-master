"""
Morphology (Subanta/Tiṅanta) domain routes.

Wraps `_lexicon.lookup()` which returns full morphological analysis:
  {stem, pos, linga, vibhakti, vacana, confidence}

Also exposes the paradigm matrices for common stems via `_lexicon._analyze_subanta`.
"""
import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

router = APIRouter(tags=["morphology"])

try:
    import _lexicon
    _LEXICON_OK = True
except Exception:
    _lexicon = None
    _LEXICON_OK = False


class MorphAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Inflected Sanskrit form")
    max_results: int = Field(5, ge=1, le=20)


@router.post("/analyze")
async def analyze_morphology(payload: MorphAnalyzeRequest):
    """
    Analyze an inflected Sanskrit form and return its morphological properties.

    Uses `_lexicon.lookup()` which returns:
      stem, pos (subhanta/tinanta), linga, vibhakti, vacana, confidence

    Returns the raw lookup result plus a normalized view.
    """
    if not _LEXICON_OK:
        raise HTTPException(status_code=503, detail="Lexicon module unavailable")

    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty input")

    try:
        raw = _lexicon.lookup(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lookup failed: {e}")

    if raw is None:
        return {
            "surface": text,
            "found": False,
            "analysis": None,
            "message": f"'{text}' not attested in lexicon",
        }

    return {
        "surface": text,
        "found": True,
        "analysis": {
            "stem": raw.get("stem"),
            "pos": raw.get("pos"),
            "linga": raw.get("linga"),
            "vibhakti": raw.get("vibhakti"),
            "vacana": raw.get("vacana"),
            "confidence": raw.get("confidence", 0.0),
            # Verb-specific fields
            "dhatu": raw.get("dhatu"),
            "gana": raw.get("gana"),
        },
    }


@router.get("/paradigm/{stem}")
async def get_paradigm(stem: str):
    """
    Return common inflected forms for a stem.

    Generates likely paradigm forms by probing the lexicon for
    standard subanta endings. This is a best-effort scan, not a
    complete paradigm table.
    """
    if not _LEXICON_OK:
        raise HTTPException(status_code=503, detail="Lexicon module unavailable")

    # Common subanta endings to try
    endings = ["", "H", "m", "au", "AH", "ena", "Aya", "At", "asya", "e", "i", "oH", "Am", "su"]
    forms = []
    seen = set()

    for suffix in endings:
        candidate = stem + suffix
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            hit = _lexicon.lookup(candidate)
        except Exception:
            hit = None
        if hit and hit.get("stem") == stem:
            forms.append({
                "form": candidate,
                "vibhakti": hit.get("vibhakti"),
                "vacana": hit.get("vacana"),
                "linga": hit.get("linga"),
            })

    return {
        "stem": stem,
        "count": len(forms),
        "forms": forms,
    }


@router.get("/probe")
async def morphology_probe():
    return {
        "lexicon_ok": _LEXICON_OK,
        "has_lookup": _LEXICON_OK and hasattr(_lexicon, "lookup"),
        "has_lookup_classical_verb": _LEXICON_OK and hasattr(_lexicon, "lookup_classical_verb"),
        "has_analyze_subanta": _LEXICON_OK and hasattr(_lexicon, "_analyze_subanta"),
        "has_analyze_tinanta": _LEXICON_OK and hasattr(_lexicon, "_analyze_tinanta"),
    }