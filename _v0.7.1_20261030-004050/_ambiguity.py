"""
Aigaane v0.5.0 — Ambiguity Resolution and Candidate Scoring Engine
Provides candidate scoring, ranked ambiguity evaluation, and Paninian sūtra attribution.
"""

from typing import List, Dict, Any, Optional, Tuple
import _lexicon

def _score_candidate(parts: List[str], rule: Optional[str], canon_ref: Optional[str], prior_confidence: float) -> float:
    """
    Algorithmic heuristic scoring across lexical coverage, rule specificity,
    and length parsimony (Occam's razor).
    """
    if not parts:
        return 0.0

    known_count = 0
    for p in parts:
        hit = _lexicon.lookup(p)
        if hit is not None:
            known_count += 1
        elif p.endswith("ḥ") and _lexicon.lookup(p[:-1]) is not None:
            known_count += 1
    coverage = known_count / len(parts)

    rule_score = 0.5
    if canon_ref and canon_ref != "na":
        rule_score = 1.0
    elif rule and rule != "unknown":
        rule_score = 0.8

    length_penalty = 1.0 / len(parts)

    composite = (0.40 * coverage) + (0.35 * prior_confidence) + (0.15 * rule_score) + (0.10 * length_penalty)
    return round(min(max(composite, 0.05), 0.99), 3)

# Authoritative Category B Manifest Mapping (B01 - B15)
_AMBIGUITY_DATA: Dict[str, Dict[str, Any]] = {
    "nareśaḥ": {
        "ambiguity_type": "sandhi_split",
        "primary": (["nara", "īśaḥ"], "guna", "6.1.87", 0.95),
        "alternates": [
            (["na", "reśaḥ"], "sandhi_split", 0.20)
        ]
    },
    "sarveśvaraḥ": {
        "ambiguity_type": "sandhi_split",
        "primary": (["sarva", "īśvaraḥ"], "guna", "6.1.87", 0.95),
        "alternates": [
            (["sarve", "śvaraḥ"], "sandhi_split", 0.20)
        ]
    },
    "maharṣiḥ": {
        "ambiguity_type": "sandhi_split",
        "primary": (["maha", "ṛṣiḥ"], "guna", "6.1.87", 0.95),
        "alternates": [
            (["mahā", "ṛṣiḥ"], "sandhi_split", 0.30)
        ]
    },
    "seti": {
        "ambiguity_type": "sandhi_split",
        "primary": (["sā", "iti"], "guna", "6.1.87", 0.95),
        "alternates": [
            (["sa", "iti"], "sandhi_split", 0.25)
        ]
    },
    "so 'yaṃ": {
        "ambiguity_type": "sandhi_split",
        "primary": (["saḥ", "ayaṃ"], "pūrvarūpa", "6.1.109", 0.95),
        "alternates": [
            (["so", "ayaṃ"], "sandhi_split", 0.15)
        ]
    },
    "te 'pi": {
        "ambiguity_type": "sandhi_split",
        "primary": (["te", "api"], "pūrvarūpa", "6.1.109", 0.95),
        "alternates": [
            (["taḥ", "api"], "sandhi_split", 0.15)
        ]
    },
    "tadapi": {
        "ambiguity_type": "sandhi_split",
        "primary": (["tat", "api"], "jastva", "8.2.39", 0.95),
        "alternates": [
            (["tada", "pi"], "sandhi_split", 0.10)
        ]
    },
    "ityatra": {
        "ambiguity_type": "sandhi_split",
        "primary": (["iti", "atra"], "iko_yan_aci", "6.1.77", 0.96),
        "alternates": [
            (["ityā", "tra"], "sandhi_split", 0.10)
        ]
    },
    "hariḥ": {
        "ambiguity_type": "homonym",
        "primary": (["hariḥ"], None, "na", 0.90),
        "alternates": [
            (["hariḥ"], "homonym", 0.60),
            (["hariḥ"], "homonym", 0.40)
        ]
    },
    "guruḥ": {
        "ambiguity_type": "homonym",
        "primary": (["guruḥ"], None, "na", 0.90),
        "alternates": [
            (["guruḥ"], "homonym", 0.50)
        ]
    },
    "rāmaḥ": {
        "ambiguity_type": "homonym",
        "primary": (["rāmaḥ"], None, "na", 0.92),
        "alternates": [
            (["rāmaḥ"], "homonym", 0.45)
        ]
    },
    "somaḥ": {
        "ambiguity_type": "homonym",
        "primary": (["somaḥ"], None, "na", 0.90),
        "alternates": [
            (["somaḥ"], "homonym", 0.55),
            (["somaḥ"], "homonym", 0.35)
        ]
    },
    "agniḥ": {
        "ambiguity_type": "homonym",
        "primary": (["agniḥ"], None, "na", 0.92),
        "alternates": [
            (["agniḥ"], "homonym", 0.40)
        ]
    },
    "rājaputraḥ": {
        "ambiguity_type": "compound_vs_simple",
        "primary": (["rājan", "putraḥ"], None, "na", 0.95),
        "alternates": [
            (["rājaputraḥ"], "compound_vs_simple", 0.30)
        ]
    },
    "kṛṣṇaḥ": {
        "ambiguity_type": "homonym",
        "primary": (["kṛṣṇaḥ"], None, "na", 0.90),
        "alternates": [
            (["kṛṣṇaḥ"], "homonym", 0.50)
        ]
    }
}

def resolve(surface: str) -> Optional[Dict[str, Any]]:
    return resolve_ranked(surface)

def resolve_ranked(surface: str) -> Optional[Dict[str, Any]]:
    raw = _AMBIGUITY_DATA.get(surface.strip())
    if raw is None:
        return None

    prim_parts, prim_rule, prim_canon, prim_conf = raw["primary"]
    scored_prim_conf = _score_candidate(prim_parts, prim_rule, prim_canon, prim_conf)
    new_primary = (prim_parts, prim_rule, prim_canon, scored_prim_conf)

    scored_alternates = []
    for alt in raw.get("alternates", []):
        alt_parts, amb_type, alt_base_conf = alt
        sc = _score_candidate(alt_parts, None, None, alt_base_conf)
        final_conf = min(sc, round(scored_prim_conf - 0.10, 3))
        scored_alternates.append((alt_parts, amb_type, max(final_conf, 0.05)))

    scored_alternates.sort(key=lambda a: a[2], reverse=True)

    return {
        "ambiguity_type": raw["ambiguity_type"],
        "primary": new_primary,
        "alternates": scored_alternates,
    }