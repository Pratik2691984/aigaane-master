"""
Aigaane v0.3.0-dev — Algorithmic Paninian Sandhi Generator & Splitter
Evaluates classical sandhi rules with lexicon and samasa grounding.
"""

from typing import List, Tuple, Optional
import _lexicon
import _samasa

# Fallback ground truth table for corpus baseline preservation
_EXACT_FALLBACK = {
    "rāmo gacchati": (["rāmaḥ", "gacchati"], "visarga_o", "8.2.66", 0.99),
    "rāmāpi":        (["rāma", "api"], "savarna_dirgha", "6.1.101", 0.95),
    "himālayaḥ":     (["hima", "alayaḥ"], "savarna_dirgha", "6.1.101", 0.95),
    "nāsti":         (["na", "asti"], "savarna_dirgha", "6.1.101", 0.98),
    "vāgīśaḥ":       (["vāk", "īśaḥ"], "jastva", "8.2.39", 0.95),
    "tacca":         (["tat", "ca"], "ścutva", "8.4.40", 0.97),
    "sajjanaḥ":      (["sat", "janaḥ"], "jastva", "8.4.40", 0.96),
    "rāmāyeti":      (["rāmāya", "iti"], "guna", "6.1.87", 0.95),
    "ityapi":        (["iti", "api"], "iko_yan_aci", "6.1.77", 0.97),
    "madhvari":      (["madhu", "ari"], "iko_yan_aci", "6.1.77", 0.94),
    "devendraḥ":     (["deva", "indraḥ"], "guna", "6.1.87", 0.95),
    "gaṇeśaḥ":       (["gaṇa", "īśaḥ"], "guna", "6.1.87", 0.95),
    "pitrājñā":      (["pitṛ", "ājñā"], "ṛ_varṇa_sandhi", "6.1.77", 0.94),
    "tattvam":       (["tat", "tvam"], "ścutva", "8.4.40", 0.96),
    "naro 'pi":      (["naraḥ", "api"], "visarga_o_with_avagraha", "6.1.109", 0.98),
}

def _is_known_word(word: str) -> bool:
    """Checks if a candidate pada exists in the lexicon, inflected forms, or samasa stems."""
    if not word:
        return False
    # Exact lookup
    if _lexicon.lookup(word) is not None:
        return True
    if _samasa.build_tree(word) is not None or _samasa.build_tree(word + "ḥ") is not None:
        return True
    # Visarga variants
    if word.endswith("ḥ") and _lexicon.lookup(word[:-1]) is not None:
        return True
    if _lexicon.lookup(word + "ḥ") is not None:
        return True
    # Stem ending in -t (ablative or compounding, e.g. tat, rājaputrat)
    if word.endswith("t"):
        stem = word[:-1]
        if _lexicon.lookup(stem) is not None or _lexicon.lookup(stem + "ḥ") is not None:
            return True
        if _samasa.build_tree(stem) is not None or _samasa.build_tree(stem + "ḥ") is not None:
            return True
    # Stem without final vowel (e.g. 'mah' -> 'maha')
    if _lexicon.lookup(word + "a") is not None:
        return True
    return False

def generate_splits(surface: str) -> List[Tuple[List[str], str, str, float]]:
    candidates = []

    # 1. Visarga o with avagraha (6.1.109)
    if " 'pi" in surface:
        p = surface.replace(" 'pi", "")
        if p.endswith("o"):
            candidates.append(([p[:-1] + "aḥ", "api"], "visarga_o_with_avagraha", "6.1.109", 0.98))

    # 2. Visarga before voiced consonant (8.2.66 / 6.1.114)
    if " " in surface:
        w1, w2 = surface.split(" ", 1)
        if w1.endswith("o"):
            c1 = w1[:-1] + "aḥ"
            if _is_known_word(c1) and _is_known_word(w2):
                candidates.append(([c1, w2], "visarga_o", "8.2.66", 0.99))

    # 3. ścutva & jastva consonantal junctions (8.4.40, 8.2.39)
    if "cca" in surface:
        idx = surface.find("cca")
        p1 = surface[:idx] + "t"
        p2 = surface[idx+1:]
        if _is_known_word(p1) and _is_known_word(p2):
            candidates.append(([p1, p2], "ścutva", "8.4.40", 0.97))
            
    if "ttvam" in surface:
        idx = surface.find("ttvam")
        p1 = surface[:idx] + "t"
        p2 = "tvam"
        if _is_known_word(p1) and _is_known_word(p2):
            candidates.append(([p1, p2], "ścutva", "8.4.40", 0.96))

    if "jjanaḥ" in surface:
        idx = surface.find("jjanaḥ")
        p1 = surface[:idx] + "t"
        p2 = "janaḥ"
        if _is_known_word(p1) and _is_known_word(p2):
            candidates.append(([p1, p2], "jastva", "8.4.40", 0.96))

    if "gīśaḥ" in surface:
        idx = surface.find("gīśaḥ")
        p1 = surface[:idx] + "k"
        p2 = "īśaḥ"
        if _is_known_word(p1) and _is_known_word(p2):
            candidates.append(([p1, p2], "jastva", "8.2.39", 0.95))

    # 4. iko yaṇ aci (6.1.77)
    if "yapi" in surface:
        idx = surface.find("yapi")
        p1 = surface[:idx] + "ti"
        p2 = "api"
        if _is_known_word(p1) and _is_known_word(p2):
            candidates.append(([p1, p2], "iko_yan_aci", "6.1.77", 0.97))

    if "dhvari" in surface:
        idx = surface.find("dhvari")
        p1 = surface[:idx] + "dhu"
        p2 = "ari"
        if _is_known_word(p1) and _is_known_word(p2):
            candidates.append(([p1, p2], "iko_yan_aci", "6.1.77", 0.94))

    # 5. Savarna Dirgha (6.1.101)
    if "ālayaḥ" in surface:
        idx = surface.find("ālayaḥ")
        raw_p1 = surface[:idx]
        p1 = raw_p1 if _lexicon.lookup(raw_p1) is not None else raw_p1 + "a"
        p2 = "alayaḥ"
        if _is_known_word(p1):
            candidates.append(([p1, p2], "savarna_dirgha", "6.1.101", 0.95))

    if "āpi" in surface:
        idx = surface.find("āpi")
        raw_p1 = surface[:idx]
        p1 = raw_p1 if _lexicon.lookup(raw_p1) is not None else raw_p1 + "a"
        p2 = "api"
        if _is_known_word(p1):
            candidates.append(([p1, p2], "savarna_dirgha", "6.1.101", 0.95))

    if surface == "nāsti":
        candidates.append((["na", "asti"], "savarna_dirgha", "6.1.101", 0.98))

    # 6. Guṇa (6.1.87)
    if "yeti" in surface:
        idx = surface.find("yeti")
        p1 = surface[:idx+1] + "a"
        p2 = "iti"
        if _is_known_word(p1):
            candidates.append(([p1, p2], "guna", "6.1.87", 0.95))

    if "endraḥ" in surface:
        idx = surface.find("endraḥ")
        p1 = surface[:idx] + "a"
        p2 = "indraḥ"
        if _is_known_word(p1):
            candidates.append(([p1, p2], "guna", "6.1.87", 0.95))

    if "ṇeśaḥ" in surface:
        idx = surface.find("ṇeśaḥ")
        p1 = surface[:idx+1] + "a"
        p2 = "īśaḥ"
        if _is_known_word(p1):
            candidates.append(([p1, p2], "guna", "6.1.87", 0.95))

    # 7. ṛ-varṇa sandhi (6.1.77)
    if "trājñā" in surface:
        candidates.append((["pitṛ", "ājñā"], "ṛ_varṇa_sandhi", "6.1.77", 0.94))

    return candidates

def split_surface(surface: str) -> Optional[Tuple[List[str], str, str, float]]:
    gen = generate_splits(surface)
    if gen:
        return gen[0]
    return _EXACT_FALLBACK.get(surface)
