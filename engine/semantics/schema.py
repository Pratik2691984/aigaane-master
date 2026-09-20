"""
engine/semantics/schema.py
Strict Pydantic Schema for Sanskrit Semantic Fields and Relational Edges
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

RelationType = Literal[
    "synonym",     # paryāya (पर्याय)
    "hypernym",    # sāmānya / jāti (सामान्य / जाति)
    "hyponym",     # viśeṣa (विशेष)
    "antonym",     # viloma / pratidvandvī (विलोम / प्रतिद्वन्द्विन्)
    "imagery",     # rūpaka / upamāna (रूपक / उपमान)
    "verbal",      # dhātu-prabhavatā / kriyā (धातुप्रभवता / क्रिया)
    "instrument"   # sādhana (साधन)
]

class SemanticEdge(BaseModel):
    source: str = Field(..., description="Canonical Devanagari lemma for the source term.")
    target: str = Field(..., description="Canonical Devanagari lemma for the target term.")
    relation: RelationType = Field(..., description="The typed lexical or conceptual relationship.")
    source_ref: Optional[str] = Field(None, description="Traditional textual authority (e.g., Amarakośa 1.1.2).")
    weight: float = Field(1.0, ge=0.0, le=1.0, description="Semantic proximity or co-occurrence weight.")

class SemanticFieldProfile(BaseModel):
    lemma: str = Field(..., description="The core concept lemma (e.g., प्रज्ञा).")
    gloss: str = Field(..., description="English gloss or primary definition.")
    edges: List[SemanticEdge] = Field(default_factory=list, description="All outgoing semantic edges from this lemma.")
