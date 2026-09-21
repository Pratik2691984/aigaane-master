"""
engines/chandas/anustubh.py
Anuṣṭubh validator — pathyā + 5 vipulā variations (corrected table).
"""

from typing import List, NamedTuple, Optional
from engines.chandas.scansion import scan

PATHYA   = ("L", "G", "L")
NA_VIP   = ("L", "G", "G")
BHA_VIP  = ("G", "L", "L")
MA_VIP   = ("G", "G", "L")
RA_VIP   = ("G", "G", "G")
JA_VIP   = ("L", "L", "L")

VIPULAS = {
    "pathyā": PATHYA,
    "na":     NA_VIP,
    "bha":    BHA_VIP,
    "ma":     MA_VIP,
    "ra":     RA_VIP,
    "ja":     JA_VIP,
}


class PadaAnalysis(NamedTuple):
    index: int
    text_pattern: str
    variety: Optional[str]
    is_valid: bool
    reason: Optional[str]


class AnustubhResult(NamedTuple):
    input: str
    padas: List[PadaAnalysis]
    is_valid: bool
    errors: List[str]


def _weight_tuple(pattern: str, positions):
    return tuple(pattern[i - 1] for i in positions)


def _classify_odd_pada(pattern: str) -> Optional[str]:
    key = _weight_tuple(pattern, (5, 6, 7))
    for name, sig in VIPULAS.items():
        if key == sig:
            return name
    return None


def _classify_even_pada(pattern: str) -> Optional[str]:
    key = _weight_tuple(pattern, (5, 6, 7))
    return "pathyā" if key == PATHYA else None


def validate_anustubh(text: str) -> AnustubhResult:
    scansion = scan(text)
    errors: List[str] = []
    if scansion.length != 32:
        errors.append(f"Expected 32 syllables, got {scansion.length}")
        return AnustubhResult(text, [], False, errors)
    sylls = list(scansion.syllables)
    groups = [sylls[i*8:(i+1)*8] for i in range(4)]
    padas: List[PadaAnalysis] = []
    for i, g in enumerate(groups, start=1):
        pattern = "".join(s.weight for s in g)
        is_odd = (i % 2 == 1)
        if is_odd:
            variety = _classify_odd_pada(pattern)
            if variety is None:
                errors.append(f"Pāda {i} (odd): positions 5-7 invalid")
                padas.append(PadaAnalysis(i, pattern, None, False, "invalid 5-7"))
                continue
        else:
            variety = _classify_even_pada(pattern)
            if variety is None:
                errors.append(f"Pāda {i} (even): not pathyā")
                padas.append(PadaAnalysis(i, pattern, None, False, "even must be pathyā"))
                continue
        reason = None if pattern[7] == "G" else "position 8 is L"
        padas.append(PadaAnalysis(i, pattern, variety, True, reason))
    return AnustubhResult(text, padas, all(p.is_valid for p in padas), errors)


if __name__ == "__main__":
    r = validate_anustubh("rāma")
    assert not r.is_valid
    assert "32" in r.errors[0]
    print("✓ anustubh.py OK")
