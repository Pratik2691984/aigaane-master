"""Deterministic boundary guards rejecting neural output outside the legal rāga space."""
import re
from aigaane.neural.schemas import SwaraSequence

BHAIRAV_ALLOWED = {"S", "r", "G", "M", "P", "d", "N", "S'"}

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
IAST_DIACRITIC_RE = re.compile(r"[āīūṛṝḷḹēṃḥṅñṭḍṇśṣ]", re.IGNORECASE)


def validate_swara_sequence(seq: SwaraSequence, raga: str = "Bhairav") -> SwaraSequence:
    """Reject any swara outside canonical rāga grammar."""
    allowed = BHAIRAV_ALLOWED

    for tok in seq.sequence:
        if tok.swara not in allowed:
            raise ValueError(
                f"Swara '{tok.swara}' not in {raga} grammar. Allowed: {sorted(allowed)}"
            )
        if tok.meend_target and tok.meend_target not in allowed:
            raise ValueError(f"Meend target '{tok.meend_target}' not in {raga}")

    return seq


def validate_sanskrit_text(text: str) -> bool:
    """BOM sanitization + Sanskrit-only orthographic guard."""
    if not text or not text.strip():
        return False
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    if not (DEVANAGARI_RE.search(text) or IAST_DIACRITIC_RE.search(text)):
        return False
    return True
