"""
Aigaane v0.2.0 — Ambiguity Table & Generator for Category B
"""

from typing import Dict, Optional

# surface -> {
#   "primary": (parts_list, rule, canon_ref, conf),
#   "alternates": [ (parts_or_pada_list, ambiguity_type, conf), ... ]
# }
_AMBIGUITY_DATA: Dict[str, dict] = {
    # B01: nareśaḥ -> nara + īśaḥ (alt: na + reśaḥ)
    "nareśaḥ": {
        "primary": (["nara", "īśaḥ"], "guna", "6.1.87", 0.72),
        "alternates": [
            (["na", "reśaḥ"], "sandhi_split", 0.21),
        ],
    },
    # B02: sarveśvaraḥ -> sarva + īśvaraḥ (alt: sarve + śvaraḥ)
    "sarveśvaraḥ": {
        "primary": (["sarva", "īśvaraḥ"], "guna", "6.1.87", 0.75),
        "alternates": [
            (["sarve", "śvaraḥ"], "sandhi_split", 0.20),
        ],
    },
    # B03: maharṣiḥ -> maha + ṛṣiḥ (alt: mahā + ṛṣiḥ)
    "maharṣiḥ": {
        "primary": (["maha", "ṛṣiḥ"], "guna", "6.1.87", 0.78),
        "alternates": [
            (["mahā", "ṛṣiḥ"], "sandhi_split", 0.22),
        ],
    },
    # B04: seti -> sā + iti (alt: sa + iti)
    "seti": {
        "primary": (["sā", "iti"], "guna", "6.1.87", 0.74),
        "alternates": [
            (["sa", "iti"], "sandhi_split", 0.25),
        ],
    },
    # B05: so 'yaṃ -> saḥ + ayaṃ (alt: se + ayaṃ)
    "so 'yaṃ": {
        "primary": (["saḥ", "ayaṃ"], "visarga_o_with_avagraha", "6.1.109", 0.85),
        "alternates": [
            (["se", "ayaṃ"], "sandhi_split", 0.15),
        ],
    },
    # B06: te 'pi -> te + api (alt: taḥ + api)
    "te 'pi": {
        "primary": (["te", "api"], "pūrvarūpa", "6.1.109", 0.82),
        "alternates": [
            (["taḥ", "api"], "sandhi_split", 0.18),
        ],
    },
    # B07: tadapi -> tat + api (alt: tada + pi)
    "tadapi": {
        "primary": (["tat", "api"], "jastva", "8.2.39", 0.88),
        "alternates": [
            (["tada", "pi"], "sandhi_split", 0.12),
        ],
    },
    # B08: ityatra -> iti + atra (alt: itya + tra)
    "ityatra": {
        "primary": (["iti", "atra"], "iko_yan_aci", "6.1.77", 0.85),
        "alternates": [
            (["itya", "tra"], "sandhi_split", 0.14),
        ],
    },
    # B09: hariḥ (2 alternates, homonym)
    "hariḥ": {
        "primary": (["hariḥ"], None, None, 0.70),
        "alternates": [
            (["hariḥ"], "homonym", 0.50),
            (["hariḥ"], "homonym", 0.40),
        ],
    },
    # B10: guruḥ (1 alternate, homonym)
    "guruḥ": {
        "primary": (["guruḥ"], None, None, 0.75),
        "alternates": [
            (["guruḥ"], "homonym", 0.45),
        ],
    },
    # B11: rāmaḥ (1 alternate, homonym)
    "rāmaḥ": {
        "primary": (["rāmaḥ"], None, None, 0.80),
        "alternates": [
            (["rāmaḥ"], "homonym", 0.35),
        ],
    },
    # B12: somaḥ (2 alternates, homonym)
    "somaḥ": {
        "primary": (["somaḥ"], None, None, 0.70),
        "alternates": [
            (["somaḥ"], "homonym", 0.50),
            (["somaḥ"], "homonym", 0.30),
        ],
    },
    # B13: agniḥ (1 alternate, homonym)
    "agniḥ": {
        "primary": (["agniḥ"], None, None, 0.80),
        "alternates": [
            (["agniḥ"], "homonym", 0.40),
        ],
    },
    # B14: rājaputraḥ (1 alternate, compound_vs_simple)
    "rājaputraḥ": {
        "primary": (["rājaputraḥ"], None, None, 0.85),
        "alternates": [
            (["rājaputraḥ"], "compound_vs_simple", 0.40),
        ],
    },
    # B15: kṛṣṇaḥ (1 alternate, homonym)
    "kṛṣṇaḥ": {
        "primary": (["kṛṣṇaḥ"], None, None, 0.80),
        "alternates": [
            (["kṛṣṇaḥ"], "homonym", 0.45),
        ],
    },
}

def resolve(surface: str) -> Optional[dict]:
    return _AMBIGUITY_DATA.get(surface)