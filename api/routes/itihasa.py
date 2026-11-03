from typing import List, Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
import _corpus

router = APIRouter(prefix="/api/v1/itihasa", tags=["Itihāsa & Canon Search"])

class ItihasaSearchRequest(BaseModel):
    query: str = Field(default="", description="Keyword, pada, or phrase in IAST or Devanagari")
    source: Optional[str] = Field(default=None, description="Optional text filter: e.g. 'Gītā', 'Rāmāyaṇa', 'Upaniṣad'")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum matches to return")

class ItihasaVerseMatch(BaseModel):
    source: str
    canto: str
    verse: str
    meter: str
    meaning: str
    keywords: List[str]

class ItihasaSearchResponse(BaseModel):
    total_matches: int
    matches: List[ItihasaVerseMatch]
    provenance: List[str]

ItihasaSearchRequest.model_rebuild()
ItihasaSearchResponse.model_rebuild()

@router.post("/search", response_model=ItihasaSearchResponse, summary="Search classical Itihāsa & Upaniṣadic corpus")
async def search_itihasa_canon(req: ItihasaSearchRequest):
    """
    Searches verses across the Bhagavad Gītā, Rāmāyaṇa, and Upaniṣads
    with metrical scansion and reference citations.
    """
    raw_matches = _corpus.search_corpus(query=req.query, source=req.source, limit=req.limit)
    return ItihasaSearchResponse(
        total_matches=len(raw_matches),
        matches=raw_matches,
        provenance=["corpus=golden-itihasa-manifest", "schema=0.2.0"]
    )
