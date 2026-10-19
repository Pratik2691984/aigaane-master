"""
routers/morphology.py
Subanta (nominal declension) endpoints.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from engines.morphology.subanta import inflect, Stem, Inflected
from engines.morphology.tinanta_engine import TinantaEngine


router = APIRouter(prefix="/api/v3/morphology", tags=["Morphology"])
_tinanta = TinantaEngine()

# ─────────────────────── Schemas ───────────────────────

class InflectRequest(BaseModel):
    lemma: str = Field(..., min_length=1, max_length=64)
    stem_class: str = Field(
        ...,
        description="One of: a-masc, a-neut, ā-fem, i-masc, i-fem, u-masc, ū-fem",
    )


class InflectedModel(BaseModel):
    vibhakti: str
    vibhakti_num: int
    vacana: str
    vacana_num: int
    form: str
    rule: str


class ParadigmResponse(BaseModel):
    lemma: str
    stem_class: str
    forms: list[InflectedModel]
    count: int


class SingleFormResponse(BaseModel):
    lemma: str
    stem_class: str
    vibhakti: str
    vacana: str
    form: str
    rule: str


# ─────────────────────── Endpoints ───────────────────────

@router.post(
    "/noun/inflect",
    response_model=ParadigmResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate full nominal declension paradigm",
)
def inflect_noun(payload: InflectRequest) -> ParadigmResponse:
    """
    Generate all 24 inflected forms (8 vibhaktis × 3 vacanas) for a given
    stem. Every form cites Aṣṭādhyāyī 4.1.2.
    """
    try:
        forms = inflect(payload.lemma, payload.stem_class)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    return ParadigmResponse(
        lemma=payload.lemma,
        stem_class=payload.stem_class,
        forms=[
            InflectedModel(
                vibhakti=f.vibhakti,
                vibhakti_num=f.vibhakti_num,
                vacana=f.vacana,
                vacana_num=f.vacana_num,
                form=f.form,
                rule=f.rule,
            )
            for f in forms
        ],
        count=len(forms),
    )


class SingleFormRequest(BaseModel):
    lemma: str = Field(..., min_length=1, max_length=64)
    stem_class: str = Field(..., max_length=32)
    vibhakti: str = Field(..., max_length=32)
    vacana: str = Field(..., max_length=32)


@router.post(
    "/noun/form",
    response_model=SingleFormResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single inflected form",
)
def get_single_form(payload: SingleFormRequest) -> SingleFormResponse:
    """Return one specific inflected form."""
    try:
        forms = inflect(payload.lemma, payload.stem_class)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    for f in forms:
        if f.vibhakti == payload.vibhakti and f.vacana == payload.vacana:
            return SingleFormResponse(
                lemma=payload.lemma,
                stem_class=payload.stem_class,
                vibhakti=f.vibhakti,
                vacana=f.vacana,
                form=f.form,
                rule=f.rule,
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No form found for vibhakti='{payload.vibhakti}', vacana='{payload.vacana}'",
    )


@router.get(
    "/noun/stem-classes",
    status_code=status.HTTP_200_OK,
    summary="List supported stem classes",
)
def list_stem_classes() -> dict:
    """Return the seven supported stem classes with example lemmas."""
    return {
        "stem_classes": [
            {"id": "a-masc", "example": "deva", "gender": "puṃ", "gloss": "god"},
            {"id": "a-neut", "example": "phala", "gender": "napuṃsaka", "gloss": "fruit"},
            {"id": "ā-fem", "example": "senā", "gender": "strī", "gloss": "army"},
            {"id": "i-masc", "example": "agni", "gender": "puṃ", "gloss": "fire"},
            {"id": "i-fem", "example": "mati", "gender": "strī", "gloss": "thought"},
            {"id": "u-masc", "example": "viṣṇu", "gender": "puṃ", "gloss": "Viṣṇu"},
            {"id": "ū-fem", "example": "bhū", "gender": "strī", "gloss": "earth"},
        ]
    }



# ─────────────────────── Tiṅanta (verb conjugation) ───────────────────────

class VerbConjugateRequest(BaseModel):
    root: str = Field(..., min_length=1, max_length=64)
    gana: int = Field(1, ge=1, le=10)
    lakara: str = Field("lat", max_length=32)
    prayoga: str = Field("kartari", max_length=16)
    script: str = Field("iast", max_length=16)
    include_traces: bool = False


@router.post(
    "/verb/conjugate",
    status_code=status.HTTP_200_OK,
    summary="Generate a 3x3 finite verb paradigm",
)
def conjugate_verb(payload: VerbConjugateRequest) -> dict:
    """Generate the nine finite forms of a root in a given lakāra."""
    try:
          return _tinanta.conjugate_grid(
            root=payload.root,
            gana=payload.gana,
            lakara=payload.lakara,
            prayoga=payload.prayoga,
            input_script="iast",
            output_script=payload.script,
            include_traces=payload.include_traces,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )