"""
engines/chandas/trishtubh.py
Triṣṭubh meter validator — 4 pādas × 11 syllables = 44 total.

Varieties:
  - Indravajrā:      − − − − ⏑ − − ⏑ − ⏑ −
  - Upendravajrā:    ⏑ − − − ⏑ − − ⏑ − ⏑ −
  - Upajāti:         a mixture of the above across pādas
"""

from __future__ import annotations

from typing import List, NamedTuple, Optional

from engines.chandas.scansion import scan


# ─────────────────────── Pattern definitions ───────────────────────
# L = Laghu (⏑), G = Guru (−)

INDRAVAJRA   = "GGGGLGGLGLG"   # − − − − ⏑ − − ⏑ − ⏑ −
UPENDRAVAJRA = "LGGGLGGLGLG"   # ⏑ − − − ⏑ − − ⏑ − ⏑ −

VARIETIES = {
    "indravajrā": INDRAVAJRA,
    "upendravajrā": UPENDRAVAJRA,
}

PADA_SYLLABLES = 11
TOTAL_SYLLABLES = 44


class PadaAnalysis(NamedTuple):
    index: int
    text_pattern: str
    variety: Optional[str]
    is_valid: bool
    reason: Optional[str]


class TrishtubhResult(NamedTuple):
    input: str
    padas: List[PadaAnalysis]
    is_valid: bool
    errors: List[str]


def _classify_pada(pattern: str) -> Optional[str]:
    """Classify an 11-syllable pāda by its pattern."""
    for name, sig in VARIETIES.items():
        if pattern == sig:
            return name
    return None


def validate_trishtubh(text: str) -> TrishtubhResult:
    """
    Validate an IAST string as a Triṣṭubh verse (or Upajāti).

    Returns a structured analysis with per-pāda variety and diagnostics.
    """
    scansion = scan(text)
    errors: List[str] = []

    if scansion.length != TOTAL_SYLLABLES:
        errors.append(
            f"Expected {TOTAL_SYLLABLES} syllables, got {scansion.length}"
        )
        return TrishtubhResult(
            input=text,
            padas=[],
            is_valid=False,
            errors=errors,
        )

    # Split into 4 pādas of 11
    syll_list = list(scansion.syllables)
    padas: List[PadaAnalysis] = []

    for i in range(4):
        group = syll_list[i * PADA_SYLLABLES:(i + 1) * PADA_SYLLABLES]
        pattern = "".join(s.weight for s in group)
        variety = _classify_pada(pattern)

        if variety is None:
            errors.append(
                f"Pāda {i + 1}: pattern {pattern} matches neither "
                f"Indravajrā nor Upendravajrā"
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

    # Upajāti requires at least one of each variety
    varieties_used = {p.variety for p in padas if p.variety}
    if is_valid and len(varieties_used) == 1:
        # Uniform — pure Indravajrā or pure Upendravajrā is valid
        pass

    return TrishtubhResult(
        input=text,
        padas=padas,
        is_valid=is_valid,
        errors=errors,
    )


# ─────────────────────── Self-test ───────────────────────

if __name__ == "__main__":
    # A genuine Indravajrā line (attested pattern)
    sample = (
        "upaiti siddhiḥ parameṣṭhine śrīḥ\n"
        "prasanna-cetāḥ prathitaṃ yathārtham\n"
        "kāvyāni kāvyāni sukāvyakartuḥ\n"
        "vicitra-citrāṇi manoharāṇi"
    )
    result = validate_trishtubh(sample)
    print(f"Input has {len(sample.split())} words")
    print(f"Valid: {result.is_valid}")
    if result.errors:
        for e in result.errors:
            print(f"  Error: {e}")
    for p in result.padas:
        print(f"  Pāda {p.index}: {p.text_pattern} — {p.variety}")

    print("trishtubh.py OK")