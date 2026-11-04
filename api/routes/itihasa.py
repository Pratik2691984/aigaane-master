"""
Itihāsa & Śāstra Canonical Verse Corpus Search Endpoint.
Route: GET /api/v1/itihasa/search
"""
import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/itihasa", tags=["Itihāsa Corpus"])

CORPUS_PATH = Path("corpus/itihasa_manifest.json")


class VerseRecord(BaseModel):
    id: str
    source: str
    chapter: int
    verse: int
    text: str
    transliteration: str
    meter: str
    default_raga: str
    meaning: str


class CorpusSearchResponse(BaseModel):
    total: int
    query: Optional[str]
    results: List[VerseRecord]


def load_corpus() -> List[dict]:
    if not CORPUS_PATH.exists():
        return []
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/search", response_model=CorpusSearchResponse)
def search_corpus(
    q: Optional[str] = Query(None, description="Search query across text, transliteration, or meaning"),
    source: Optional[str] = Query(None, description="Filter by source text, e.g. 'Bhagavad Gītā'"),
    meter: Optional[str] = Query(None, description="Filter by meter, e.g. 'anuṣṭubh' or 'triṣṭubh'")
) -> CorpusSearchResponse:
    corpus = load_corpus()
    filtered = []

    for item in corpus:
        if source and source.lower() not in item.get("source", "").lower():
            continue
        if meter and meter.lower() != item.get("meter", "").lower():
            continue
        if q:
            ql = q.lower()
            matches = (
                ql in item.get("text", "").lower()
                or ql in item.get("transliteration", "").lower()
                or ql in item.get("meaning", "").lower()
                or ql in item.get("id", "").lower()
            )
            if not matches:
                continue
        filtered.append(VerseRecord(**item))

    return CorpusSearchResponse(
        total=len(filtered),
        query=q,
        results=filtered
    )
