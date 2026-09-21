"""
engines/chandas/jagati.py
Jagatī meter validator — 4 pādas × 12 syllables = 48 total.

Varieties:
  - Vaṃśastha:      ⏑ − ⏑ − ⏑ − ⏑ − − ⏑ − ⏑
  - Indravaṃśā:     − − − − ⏑ − ⏑ − ⏑ − ⏑ −
  - Svāgatā:        − − ⏑ − − ⏑ ⏑ − ⏑ − ⏑ −
"""

from __future__ import annotations

from typing import List, NamedTuple, Optional

from engines.chandas.scansion import scan


# ─────────────────────── Pattern definitions ───────────────────────

VAMSHASTHA   = "LGLGLGLGGLGL"   # ⏑ − ⏑ − ⏑ − ⏑ − − ⏑ − ⏑
INDRAVAMSHA  = "GGGGLGLGLGLG"   # − − − − ⏑ − ⏑ − ⏑ − ⏑ −
SVAGATA      = "GGLGGLGLGLGL"   # − − ⏑ − − ⏑ ⏑ − ⏑ − ⏑ −

VARIETIES = {
    "vaṃśastha": VAMSHASTHA,
    "indravaṃśā": INDRAVAMSHA,
    "svāgatā": SVAGATA,
}

PADA_SYLLABLES = 12
TOTAL_SYLLABLES = 48


class PadaAnalysis(NamedTuple):
    index: int
    text_pattern: str
    variety: Optional[str]
    is_valid: bool
    reason: Optional[str]


class JagatiResult(NamedTuple):
    input: str
    padas: List[PadaAnalysis]
    is_valid: bool
    errors: List[str]


def _classify_pada(pattern: str) -> Optional[str]:
    for name, sig in VARIETIES.items():
        if pattern == sig:
            return name
    return None


def validate_jagati(text: str) -> JagatiResult:
    """
    Validate an IAST string as a Jagatī verse.
    """
    scansion = scan(text)
    errors: List[str] = []

    if scansion.length != TOTAL_SYLLABLES:
        errors.append(
            f"Expected {TOTAL_SYLLABLES} syllables, got {scansion.length}"
        )
        return JagatiResult(
            input=text,
            padas=[],
            is_valid=False,
            errors=errors,
        )

    syll_list = list(scansion.syllables)
    padas: List[PadaAnalysis] = []

    for i in range(4):
        group = syll_list[i * PADA_SYLLABLES:(i + 1) * PADA_SYLLABLES]
        pattern = "".join(s.weight for s in group)
        variety = _classify_pada(pattern)

        if variety is None:
            errors.append(
                f"Pāda {i + 1}: pattern {pattern} matches no known "
                f"Jagatī variety"
            )
            padas.append(PadaAnalysis(
                index=i + 1,
                text_pattern=pattern,
                variety=None,
                is_valid=False,
                reason="invalid pattern",
            ))
            continue

        padas.append(PadaAnalysis(
            index=i + 1,
            text_pattern=pattern,
            variety=variety,
            is_valid=True,
            reason=None,
        ))

    is_valid = all(p.is_valid for p in padas) and not errors

    return JagatiResult(
        input=text,
        padas=padas,
        is_valid=is_valid,
        errors=errors,
    )


# ─────────────────────── Self-test ───────────────────────

if __name__ == "__main__":
    sample = "test text with twelve syllables per line"
    result = validate_jagati(sample)
    print(f"Valid: {result.is_valid}")
    for p in result.padas:
        print(f"  Pāda {p.index}: {p.text_pattern} — {p.variety}")
    print("jagati.py OK")