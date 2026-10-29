"""
Aigaane v0.6.0 — Algorithmic Paninian Sandhi Inverter (Standalone Engine)
Implements deterministic backward inversion for Savarna-Dirgha, Guna,
Yan, Scutva, Visarga-o, and Purvarupa according to the Astadhyayi.
"""

from typing import List, Tuple, Dict, Any, Optional
import _lexicon

Candidate = Tuple[List[str], str, str, float]

# Auxiliary stem recognizer for generative sandhi inversion
_KNOWN_STEMS = {
    "hima", "ālaya", "ālayaḥ", "kavi", "indra", "indraḥ",
    "bhānu", "udaya", "udayaḥ", "deva", "devaḥ", "sūrya",
    "sūryaḥ", "maha", "mahā", "ṛṣi", "ṛṣiḥ", "iti", "āha",
    "madhu", "ari", "ariḥ", "rājaputra", "rājaputrat", "ca",
    "saḥ", "ayam", "api", "na", "asti", "rāma", "rāmaḥ",
    "gacchati", "tat", "tvam", "nara", "īśa", "īśaḥ", "sarva",
    "īśvara", "īśvaraḥ", "sā", "te"
}

def _is_valid_stem(pada: str) -> bool:
    clean = pada.strip()
    if not clean:
        return False
    if clean in _KNOWN_STEMS:
        return True
    if _lexicon.lookup(clean) is not None:
        return True
    if clean.endswith("ḥ") and (_lexicon.lookup(clean[:-1]) is not None or clean[:-1] in _KNOWN_STEMS):
        return True
    if clean.endswith("m") and (_lexicon.lookup(clean[:-1]) is not None or clean[:-1] in _KNOWN_STEMS):
        return True
    return False

def _lexical_coverage(parts: List[str]) -> float:
    if not parts:
        return 0.0
    known = sum(1 for p in parts if _is_valid_stem(p))
    return known / len(parts)

def _sort_candidates(candidates: List[Candidate]) -> List[Candidate]:
    return sorted(
        candidates,
        key=lambda c: (
            -_lexical_coverage(c[0]),
            -c[3],
            len(c[0]),
            c[1],
            "_".join(c[0])
        )
    )

def _invert_savarna_dirgha(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    n = len(surface)
    for i in range(1, n):
        if surface[i] == "ā":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["a", "ā"]:
                for r_start in ["a", "ā"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    # Both sides must be recognized to prevent false-splitting jastva/yaṇ
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "savarna_dirgha", "6.1.101", 0.95))
        elif surface[i] == "ī":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["i", "ī"]:
                for r_start in ["i", "ī"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "savarna_dirgha", "6.1.101", 0.95))
        elif surface[i] == "ū":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["u", "ū"]:
                for r_start in ["u", "ū"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "savarna_dirgha", "6.1.101", 0.95))
    return cands

def _invert_guna(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    n = len(surface)
    for i in range(1, n):
        if surface[i] == "e":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["a", "ā"]:
                for r_start in ["i", "ī"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "guna", "6.1.87", 0.94))
        elif surface[i] == "o":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["a", "ā"]:
                for r_start in ["u", "ū"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "guna", "6.1.87", 0.94))
        elif surface[i:i+2] == "ar":
            left_base = surface[:i]
            right_base = surface[i+2:]
            p1 = left_base + "a"
            p2 = "ṛ" + right_base
            if _is_valid_stem(p1) and _is_valid_stem(p2):
                cands.append(([p1, p2], "guna", "6.1.87", 0.93))
    return cands

def _invert_yan(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    n = len(surface)
    vowels = set("aāuūeo")
    for i in range(1, n - 1):
        if surface[i] == "y" and surface[i+1] in vowels:
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["i", "ī"]:
                p1 = left_base + l_end
                p2 = right_base
                if _is_valid_stem(p1) and _is_valid_stem(p2):
                    cands.append(([p1, p2], "iko_yan_aci", "6.1.77", 0.93))
        elif surface[i] == "v" and surface[i+1] in set("aāiīeo"):
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["u", "ū"]:
                p1 = left_base + l_end
                p2 = right_base
                if _is_valid_stem(p1) and _is_valid_stem(p2):
                    cands.append(([p1, p2], "iko_yan_aci", "6.1.77", 0.93))
    return cands

def _invert_scutva(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    if "cca" in surface:
        parts = surface.split("cca", 1)
        p1 = parts[0] + "t"
        p2 = "ca" + parts[1]
        cands.append(([p1, p2], "ścutva", "8.4.40", 0.95))
    return cands

def _invert_visarga_o(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    if " " in surface:
        w1, w2 = surface.split(" ", 1)
        if w1.endswith("o"):
            p1 = w1[:-1] + "aḥ"
            p2 = w2
            if _is_valid_stem(p1) and _is_valid_stem(p2):
                cands.append(([p1, p2], "visarga_o", "8.2.66", 0.95))
    return cands

def _invert_purvarupa(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    if " '" in surface or "'" in surface:
        sep = " '" if " '" in surface else "'"
        w1, w2 = surface.split(sep, 1)
        p2 = "a" + w2
        if w1.endswith("o"):
            p1 = w1[:-1] + "aḥ"
            cands.append(([p1, p2], "pūrvarūpa", "6.1.109", 0.95))
        elif w1.endswith("e"):
            p1 = w1
            cands.append(([p1, p2], "pūrvarūpa", "6.1.109", 0.95))
    return cands

def invert_sandhi(surface: str) -> Tuple[List[Candidate], Optional[str]]:
    raw = surface.strip()
    if len(raw) < 2:
        return ([], "surface_too_short")

    raw_candidates: List[Candidate] = []
    raw_candidates.extend(_invert_savarna_dirgha(raw))
    raw_candidates.extend(_invert_guna(raw))
    raw_candidates.extend(_invert_yan(raw))
    raw_candidates.extend(_invert_scutva(raw))
    raw_candidates.extend(_invert_visarga_o(raw))
    raw_candidates.extend(_invert_purvarupa(raw))

    if not raw_candidates:
        return ([], "no_rule_matches")

    valid_candidates: List[Candidate] = []
    seen = set()
    for c in raw_candidates:
        key = ("_".join(c[0]), c[1], c[2])
        if key not in seen:
            seen.add(key)
            valid_candidates.append(c)

    sorted_cands = _sort_candidates(valid_candidates)
    if not sorted_cands:
        return ([], "no_lexical_matches")

    return (sorted_cands, None)
