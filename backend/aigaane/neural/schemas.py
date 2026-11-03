"""Pydantic schemas for the Gemini neural boundary.

These constrain Gemini's output to canonical swara tokens only.
Any deviation is an immediate schema violation -> HTTP 422.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

SWARA_PATTERN = r"^(S'|S|r|G|M|P|d|N)$"


class SwaraToken(BaseModel):
    swara: str = Field(..., pattern=SWARA_PATTERN)
    meend_target: Optional[str] = Field(None, pattern=SWARA_PATTERN)


class SwaraSequence(BaseModel):
    """Gemini's ONLY legal output structure for Pillar 1."""
    sequence: List[SwaraToken] = Field(..., min_length=1, max_length=64)
    confidence: float = Field(..., ge=0.0, le=0.75)   # Hard ceiling
    rationale: str = Field(..., max_length=280)


class ChandasInput(BaseModel):
    syllables: List[str]
    weights: List[str] = Field(..., description="L=1, G=2")
    target_raga: str = "Bhairav"
    verse_text: str
