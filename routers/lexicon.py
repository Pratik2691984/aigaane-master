"""
routers/lexicon.py
GET /api/v3/lexicon/lookup, /exists, /stats
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from engines.lexicon.vidyut_kosha import VidyutKosha


router = APIRouter(prefix="/api/v3/lexicon", tags=["Lexicon"])

# Preload disabled: the 78 MB Kosha takes several seconds to fully scan
# for glosses. Construction is instant; gloss lookups load lazily.
_kosha = VidyutKosha(preload_dhatus=False)


class EntryModel(BaseModel):
    lemma: str
    lemma_slp1: str
    is_avyaya: bool
    gloss: Optional[dict] = None


class LookupResponse(BaseModel):
    word: str
    word_slp1: str
    script: str
    found: bool
    count: int
    entries: list[EntryModel]


class ExistsResponse(BaseModel):
    word: str
    exists: bool


@router.get(
    "/lookup",
    response_model=LookupResponse,
    status_code=status.HTTP_200_OK,
    summary="Look up a canonical Sanskrit word",
)
def lookup(
    q: str = Query(..., min_length=1, max_length=64),
    script: str = Query("iast", max_length=16),
    limit: int = Query(10, ge=1, le=50),
) -> LookupResponse:
    try:
        result = _kosha.lookup(q, script=script, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return LookupResponse(**result)


@router.get(
    "/exists",
    response_model=ExistsResponse,
    status_code=status.HTTP_200_OK,
    summary="Check whether a word is canonical",
)
def exists(
    q: str = Query(..., min_length=1, max_length=64),
    script: str = Query("iast", max_length=16),
) -> ExistsResponse:
    return ExistsResponse(word=q, exists=_kosha.exists(q, script=script))


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Lexicon statistics",
)
def stats() -> dict:
    return {
        "dhatu_glosses_loaded": _kosha.dhatu_count,
        "kosha_available": True,
        "preload_disabled": True,
        "note": "Glosses load lazily; use /lookup for entries.",
    }