"""
routers/corpus.py
Itihāsa corpus search endpoints.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from engines.corpus.loader import Corpus


router = APIRouter(prefix="/api/v3/corpus", tags=["Corpus"])


# Singleton corpus instance
_corpus: Optional[Corpus] = None


def get_corpus() -> Corpus:
    global _corpus
    if _corpus is None:
        _corpus = Corpus()
    return _corpus


# ─────────────────────── Schemas ───────────────────────

class SearchRequest(BaseModel):
    query: str = Field("", max_length=500)
    source: Optional[str] = Field(None, max_length=64)
    meter: Optional[str] = Field(None, max_length=64)
    theme: Optional[str] = Field(None, max_length=64)
    limit: int = Field(10, ge=1, le=50)


class VerseModel(BaseModel):
    id: str
    source: str
    location: str
    iast: str
    meter: str
    themes: list[str]
    gloss: str


class SearchResultModel(BaseModel):
    verse: VerseModel
    score: float
    matched_terms: list[str]


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultModel]
    total_returned: int


# ─────────────────────── Endpoints ───────────────────────

@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search the Itihāsa corpus",
)
def search_corpus(payload: SearchRequest) -> SearchResponse:
    """Full-text search over Rāmāyaṇa and Mahābhārata verses."""
    corpus = get_corpus()
    results = corpus.search(
        query=payload.query,
        source=payload.source,
        meter=payload.meter,
        theme=payload.theme,
        limit=payload.limit,
    )

    return SearchResponse(
        query=payload.query,
        results=[
            SearchResultModel(
                verse=VerseModel(
                    id=r.verse.id,
                    source=r.verse.source,
                    location=r.verse.location,
                    iast=r.verse.iast,
                    meter=r.verse.meter,
                    themes=list(r.verse.themes),
                    gloss=r.verse.gloss,
                ),
                score=r.score,
                matched_terms=list(r.matched_terms),
            )
            for r in results
        ],
        total_returned=len(results),
    )


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Corpus statistics",
)
def corpus_stats() -> dict:
    """Return counts by source, meter, and theme."""
    corpus = get_corpus()
    return corpus.stats()


@router.get(
    "/sources",
    status_code=status.HTTP_200_OK,
    summary="List corpus sources",
)
def list_sources() -> dict:
    """Return the list of Itihāsa sources available."""
    corpus = get_corpus()
    stats = corpus.stats()
    return {
        "sources": list(stats["sources"].keys()),
        "counts": stats["sources"],
    }