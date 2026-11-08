r"""
Tala congruence engine -- v2.0

Implements the rhythmic-position validator documented in audit-findings.md:

    3P + 2D + L + t_start == 17 (mod C)

Where:
    P         = count of pluta syllables  (3 matras each)
    D         = count of dirgha syllables (2 matras each)
    L         = count of laghu syllables  (1 matra each; optional extension)
    t_start   = starting offset within the cycle (aksharas, 0-based)
    C         = tala cycle length (aksharas)
    17        = canonical sam anchor constant (audit-findings.md)

When laghu_count == 0 (the default), the formula reduces exactly to the
documented form 3P + 2D + t_start == 17 (mod C).

NOTE: This module is pure ASCII at the byte level. IAST diacritics in the
TalaSpec name strings are written as \uXXXX escapes so the file survives any
encoding. The module docstring is a raw string so those escapes are not
interpreted by Python at parse time.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


# ------------------------------------------------------------------ #
#   Canonical constants                                              #
# ------------------------------------------------------------------ #

SAM_ANCHOR: int = 17
"""The canonical sam anchor constant (target residue mod C)."""

MATRA_PLUTA: int = 3
MATRA_DIRGHA: int = 2
MATRA_LAGHU: int = 1


# ------------------------------------------------------------------ #
#   Tala registry                                                    #
# ------------------------------------------------------------------ #

@dataclass(frozen=True)
class TalaSpec:
    name: str
    cycle_length: int          # C, in aksharas
    jati: str
    description: str


TALA_REGISTRY: Dict[str, TalaSpec] = {
    "adi": TalaSpec(
        "\u0100di", 8, "chatusra",
        "8-akshara cycle (laghu + 2 drutam)",
    ),
    "rupaka": TalaSpec(
        "R\u016bpaka", 6, "chatusra",
        "6-akshara cycle (drutam + laghu)",
    ),
    "misra_chapu": TalaSpec(
        "Mi\u015bra Ch\u0101pu", 7, "misra",
        "7-akshara cycle",
    ),
    "khanda_chapu": TalaSpec(
        "Kha\u1e47\u1e0da Ch\u0101pu", 5, "khanda",
        "5-akshara cycle",
    ),
    "trisra_eka": TalaSpec(
        "Tri\u015bra Eka", 3, "trisra",
        "3-akshara cycle",
    ),
    "khanda_eka": TalaSpec(
        "Kha\u1e47\u1e0da Eka", 5, "khanda",
        "5-akshara cycle",
    ),
    "misra_eka": TalaSpec(
        "Mi\u015bra Eka", 7, "misra",
        "7-akshara cycle",
    ),
    "chatusra_eka": TalaSpec(
        "Chatu\u015bra Eka", 4, "chatusra",
        "4-akshara cycle",
    ),
    "dhruva": TalaSpec(
        "Dhruva", 14, "chatusra",
        "14-akshara cycle",
    ),
    "matya": TalaSpec(
        "M\u0101\u1e6dya", 10, "chatusra",
        "10-akshara cycle",
    ),
    "jhampa": TalaSpec(
        "Jhampa", 9, "misra",
        "9-akshara cycle",
    ),
    "triputa": TalaSpec(
        "Triputa", 7, "trisra",
        "7-akshara cycle",
    ),
    "ata": TalaSpec(
        "A\u1e6da", 14, "khanda",
        "14-akshara cycle",
    ),
    "eka": TalaSpec(
        "Eka", 4, "chatusra",
        "4-akshara cycle",
    ),
}


def lookup_tala(name: str) -> Optional[TalaSpec]:
    """Case-insensitive lookup; returns None if not in the registry."""
    return TALA_REGISTRY.get(name.lower().strip())


def list_talas() -> List[Dict]:
    """Full registry as a JSON-friendly list."""
    return [asdict(t) for t in TALA_REGISTRY.values()]


# ------------------------------------------------------------------ #
#   Core congruence                                                  #
# ------------------------------------------------------------------ #

@dataclass
class CongruenceResult:
    pluta_count: int
    dirgha_count: int
    laghu_count: int
    t_start: int
    cycle_length: int
    total_matras: int
    residue: int
    target: int
    congruent: bool
    deviation: int
    sam_landing: int

    def to_dict(self) -> dict:
        return asdict(self)


def check_congruence(
    pluta_count: int,
    dirgha_count: int,
    cycle_length: int,
    t_start: int = 0,
    laghu_count: int = 0,
    sam_anchor: int = SAM_ANCHOR,
) -> CongruenceResult:
    """
    Check tala congruence: 3P + 2D + L + t_start == sam_anchor (mod C).

    Raises ValueError on invalid inputs.
    """
    if pluta_count < 0 or dirgha_count < 0 or laghu_count < 0 or t_start < 0:
        raise ValueError("Counts and t_start must be non-negative")
    if cycle_length <= 0:
        raise ValueError("cycle_length must be >= 1")

    total = (
        MATRA_PLUTA * pluta_count
        + MATRA_DIRGHA * dirgha_count
        + MATRA_LAGHU * laghu_count
        + t_start
    )
    residue = total % cycle_length
    target = sam_anchor % cycle_length
    congruent = (residue == target)

    k = round((total - sam_anchor) / cycle_length)
    nearest_correct = sam_anchor + k * cycle_length
    deviation = total - nearest_correct
    sam_landing = total % cycle_length

    return CongruenceResult(
        pluta_count=pluta_count,
        dirgha_count=dirgha_count,
        laghu_count=laghu_count,
        t_start=t_start,
        cycle_length=cycle_length,
        total_matras=total,
        residue=residue,
        target=target,
        congruent=congruent,
        deviation=deviation,
        sam_landing=sam_landing,
    )


def suggest_correction(
    pluta_count: int,
    dirgha_count: int,
    cycle_length: int,
    t_start: int = 0,
    laghu_count: int = 0,
    sam_anchor: int = SAM_ANCHOR,
) -> dict:
    """
    Given a non-congruent phrase, suggest minimal adjustments.
    """
    r = check_congruence(
        pluta_count, dirgha_count, cycle_length, t_start, laghu_count, sam_anchor
    )
    if r.congruent:
        return {"already_congruent": True, **r.to_dict()}

    options = {}
    dev = r.deviation

    if dev < 0 and -dev % MATRA_LAGHU == 0:
        options["add_laghu"] = -dev // MATRA_LAGHU
    elif dev > 0 and dev % MATRA_LAGHU == 0:
        options["drop_laghu"] = dev // MATRA_LAGHU

    options["shift_t_start"] = -dev if t_start - dev >= 0 else dev % cycle_length

    alts = []
    for cand in range(2, 33):
        rr = check_congruence(
            pluta_count, dirgha_count, cand, t_start, laghu_count, sam_anchor
        )
        if rr.congruent:
            alts.append(cand)
    if alts:
        options["congruent_cycle_lengths"] = alts

    return {"already_congruent": False, "current": r.to_dict(), "corrections": options}