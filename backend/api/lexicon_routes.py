"""
Lexicon (Kośa) domain routes — dictionary-style access to the 2-5K stem lexicon.

Wraps `_lexicon.lookup()`, which returns:
  {stem, pos, linga, vibhakti, vacana, confidence, [dhatu, gana]}

Provides:
  POST /lexicon/lookup      → full morphology with match strategy attribution
  POST /lexicon/attest      → boolean: is this stem attested?
  GET  /lexicon/probe       → module availability
"""
import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(tags=["lexicon"])

try:
    import _lexicon
    _LEXICON_OK = True
except Exception:
    _lexicon = None
    _LEXICON_OK = False


# Matching strategies: try exact, then progressively strip endings
_MATCH_STRATEGIES = [
    "exact",           # Try as-is
    "strip_aH",        # SLP1 nominative singular
    "strip_AH",        # SLP1 plural
    "strip_H",         # bare visarga
    "strip_aḥ",        # IAST nominative singular
    "strip_āḥ",        # IAST plural
    "strip_ḥ",         # bare IAST visarga
    "add_a",           # base + 'a' (most common masc stem)
    "add_A",           # base + 'A'
]


def _try_lookup_with_strategy(text: str) -> tuple:
    """
    Try lookup with fallback strategies. Returns (result, strategy_used, tried_count).
    """
    strategies_tried = []

    # Strategy 1: exact
    strategies_tried.append("exact")
    try:
        hit = _lexicon.lookup(text)
        if hit:
            return (hit, "exact", len(strategies_tried))
    except Exception:
        pass

    # Strategy 2: strip SLP1 endings
    slp1_endings = [("aH", "strip_aH"), ("AH", "strip_AH"), ("H", "strip_H")]
    for suffix, name in slp1_endings:
        if text.endswith(suffix) and len(text) > len(suffix):
            base = text[: -len(suffix)]
            strategies_tried.append(name)
            try:
                hit = _lexicon.lookup(base)
                if hit:
                    return (hit, name, len(strategies_tried))
                # also try base + 'a'
                hit = _lexicon.lookup(base + "a")
                if hit:
                    return (hit, name + "+a", len(strategies_tried))
            except Exception:
                pass

    # Strategy 3: strip IAST endings
    iast_endings = [("aḥ", "strip_aḥ"), ("āḥ", "strip_āḥ"), ("ḥ", "strip_ḥ")]
    for suffix, name in iast_endings:
        if text.endswith(suffix) and len(text) > len(suffix):
            base = text[: -len(suffix)]
            strategies_tried.append(name)
            try:
                hit = _lexicon.lookup(base)
                if hit:
                    return (hit, name, len(strategies_tried))
                hit = _lexicon.lookup(base + "a")
                if hit:
                    return (hit, name + "+a", len(strategies_tried))
            except Exception:
                pass

    # Strategy 4: add 'a' at end (recover bare stem)
    strategies_tried.append("add_a")
    try:
        hit = _lexicon.lookup(text + "a")
        if hit:
            return (hit, "add_a", len(strategies_tried))
    except Exception:
        pass

    return (None, None, len(strategies_tried))


class LexiconLookupRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Stem or inflected form")


class LexiconAttestRequest(BaseModel):
    stem: str = Field(..., min_length=1, description="Bare stem to check")


@router.post("/lookup")
async def lexicon_lookup(payload: LexiconLookupRequest):
    """
    Dictionary-style lookup with strategy attribution.

    Tries exact match, then progressively strips Sanskrit endings to
    recover the base stem. Reports which strategy succeeded so the
    frontend can surface "matched via ending-strip" vs "exact match".
    """
    if not _LEXICON_OK:
        raise HTTPException(status_code=503, detail="Lexicon module unavailable")

    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty input")

    result, strategy, tried = _try_lookup_with_strategy(text)

    if not result:
        return {
            "surface": text,
            "found": False,
            "strategy": None,
            "strategies_tried": tried,
            "analysis": None,
            "message": f"'{text}' not attested (tried {tried} strategies)",
        }

    return {
        "surface": text,
        "found": True,
        "strategy": strategy,
        "strategies_tried": tried,
        "analysis": {
            "stem": result.get("stem"),
            "pos": result.get("pos"),
            "linga": result.get("linga"),
            "vibhakti": result.get("vibhakti"),
            "vacana": result.get("vacana"),
            "confidence": result.get("confidence", 0.0),
            "dhatu": result.get("dhatu"),
            "gana": result.get("gana"),
        },
    }


@router.post("/attest")
async def lexicon_attest(payload: LexiconAttestRequest):
    """
    Boolean attestation check — is this bare stem in the lexicon?

    Lighter than `/lookup` — just returns true/false. Useful for
    frontend validation without full morphology payload.
    """
    if not _LEXICON_OK:
        raise HTTPException(status_code=503, detail="Lexicon module unavailable")

    stem = payload.stem.strip()
    if not stem:
        raise HTTPException(status_code=400, detail="Empty input")

    try:
        hit = _lexicon.lookup(stem)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lookup failed: {e}")

    return {
        "stem": stem,
        "attested": hit is not None,
        "confidence": hit.get("confidence", 0.0) if hit else 0.0,
    }


@router.get("/probe")
async def lexicon_probe():
    return {
        "lexicon_ok": _LEXICON_OK,
        "has_lookup": _LEXICON_OK and hasattr(_lexicon, "lookup"),
        "has_lookup_classical_verb": _LEXICON_OK and hasattr(_lexicon, "lookup_classical_verb"),
        "strategies": _MATCH_STRATEGIES,
    }