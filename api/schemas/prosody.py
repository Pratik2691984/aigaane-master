import typing
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class ProsodyScanRequest(BaseModel):
    text: str = Field(..., description="Devanagari text of the verse")
    chandas: Optional[str] = Field("anustubh", description="Target meter")
    padanta_guru: Optional[bool] = Field(True, description="Enforce padante va")

class SyllableDetail(BaseModel):
    index: int
    text: str
    weight: Literal["L", "G"]
    matra: int
    rule: str

class PadaScanResult(BaseModel):
    pada_number: int
    text: str
    syllables: List[str]
    weights: List[Literal["L", "G"]]
    weight_pattern: str
    total_syllables: int
    total_matras: int
    valid: bool

class ProsodyDiagnostic(BaseModel):
    pada: int
    syllable: int
    found: str
    expected: str
    rule: str
    sutra: str
    message: str

class ProsodyTraceStep(BaseModel):
    rule: str
    pada: int
    syllable: int
    found: str
    ok: bool

class ProsodyScanResponse(BaseModel):
    valid: bool
    chandas: str
    variant: Optional[str] = None
    padas: List[PadaScanResult]
    diagnostics: List[ProsodyDiagnostic]
    trace: List[ProsodyTraceStep]
    governance: Dict[str, Any]
