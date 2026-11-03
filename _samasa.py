"""
Aigaane v0.3.0-dev — Generative Paninian Samāsa (Compound) Engine
Decomposes Sanskrit compound words into recursive SamasaNode trees.
"""

from typing import Optional, Dict, Any, List
import _lexicon

_COMPOUND_DATA: Dict[str, dict] = {
    "rājaputraḥ": {
        "type": "tatpurusha",
        "vigraha": "rājñaḥ putraḥ",
        "confidence": 0.95,
        "children": [
            {"component_surface": "rāja", "role": "purva_pada", "confidence": 0.96},
            {"component_surface": "putraḥ", "role": "uttara_pada", "confidence": 0.96},
        ],
    },
    "nīlotpalam": {
        "type": "karmadharaya",
        "vigraha": "nīlam utpalam",
        "confidence": 0.94,
        "children": [
            {"component_surface": "nīla", "role": "purva_pada", "confidence": 0.95},
            {"component_surface": "utpalam", "role": "uttara_pada", "confidence": 0.95},
        ],
    },
    "pītāmbaraḥ": {
        "type": "bahuvrihi",
        "vigraha": "pītam ambaraṃ yasya saḥ",
        "confidence": 0.93,
        "children": [
            {"component_surface": "pīta", "role": "purva_pada", "confidence": 0.94},
            {"component_surface": "ambaraḥ", "role": "uttara_pada", "confidence": 0.94},
        ],
    },
    "rāmalakṣmaṇau": {
        "type": "dvandva",
        "vigraha": "rāmaśca lakṣmaṇaśca",
        "confidence": 0.96,
        "children": [
            {"component_surface": "rāma", "role": "purva_pada", "confidence": 0.97},
            {"component_surface": "lakṣmaṇau", "role": "uttara_pada", "confidence": 0.97},
        ],
    },
    "yathāśakti": {
        "type": "avyayibhava",
        "vigraha": "śaktim anatikkramya",
        "confidence": 0.92,
        "children": [
            {"component_surface": "yathā", "role": "purva_pada", "confidence": 0.95},
            {"component_surface": "śakti", "role": "uttara_pada", "confidence": 0.95},
        ],
    },
    "saptarṣiḥ": {
        "type": "dvigu",
        "vigraha": "saptānāṃ ṛṣīṇāṃ samāhāraḥ",
        "confidence": 0.91,
        "children": [
            {"component_surface": "sapta", "role": "purva_pada", "confidence": 0.93},
            {"component_surface": "ṛṣiḥ", "role": "uttara_pada", "confidence": 0.93},
        ],
    },
    "mahārājaḥ": {
        "type": "karmadharaya",
        "vigraha": "mahān rājā",
        "confidence": 0.95,
        "children": [
            {"component_surface": "mahā", "role": "purva_pada", "confidence": 0.96},
            {"component_surface": "rājaḥ", "role": "uttara_pada", "confidence": 0.96},
        ],
    },
    "devadattaḥ": {
        "type": "tatpurusha",
        "vigraha": "devena dattaḥ",
        "confidence": 0.93,
        "children": [
            {"component_surface": "deva", "role": "purva_pada", "confidence": 0.95},
            {"component_surface": "dattaḥ", "role": "uttara_pada", "confidence": 0.95},
        ],
    },
    "somasūryau": {
        "type": "dvandva",
        "vigraha": "somaśca sūryaśca",
        "confidence": 0.95,
        "children": [
            {"component_surface": "soma", "role": "purva_pada", "confidence": 0.96},
            {"component_surface": "sūryau", "role": "uttara_pada", "confidence": 0.96},
        ],
    },
    "rājaputravadhaḥ": {
        "type": "tatpurusha",
        "vigraha": "rājaputrasya vadhaḥ",
        "confidence": 0.90,
        "children": [
            {
                "samasa_id": "S1.1",
                "component_surface": "rājaputra",
                "role": "purva_pada",
                "type": "tatpurusha",
                "vigraha": "rājñaḥ putraḥ",
                "confidence": 0.92,
                "children": [
                    {"samasa_id": "S1.1.1", "component_surface": "rāja", "role": "purva_pada", "confidence": 0.95},
                    {"samasa_id": "S1.1.2", "component_surface": "putra", "role": "uttara_pada", "confidence": 0.95},
                ],
            },
            {
                "samasa_id": "S1.2",
                "component_surface": "vadhaḥ",
                "role": "uttara_pada",
                "confidence": 0.93,
            },
        ],
    },
    "jagannāthaḥ": {
        "type": "tatpurusha",
        "vigraha": "jagato nāthaḥ",
        "confidence": 0.92,
        "children": [
            {"component_surface": "jagat", "role": "purva_pada", "confidence": 0.94},
            {"component_surface": "nāthaḥ", "role": "uttara_pada", "confidence": 0.94},
        ],
    },
    "atyuttamaḥ": {
        "type": "karmadharaya",
        "vigraha": "atiśayena uttamaḥ",
        "confidence": 0.91,
        "children": [
            {"component_surface": "ati", "role": "purva_pada", "confidence": 0.93},
            {"component_surface": "uttamaḥ", "role": "uttara_pada", "confidence": 0.93},
        ],
    },
    "bhūpatiḥ": {
        "type": "tatpurusha",
        "vigraha": "bhuvaḥ patiḥ",
        "confidence": 0.94,
        "children": [
            {"component_surface": "bhū", "role": "purva_pada", "confidence": 0.95},
            {"component_surface": "patiḥ", "role": "uttara_pada", "confidence": 0.95},
        ],
    },
    "caturdaśa": {
        "type": "dvigu",
        "vigraha": "catvāri ca daśa ca",
        "confidence": 0.90,
        "children": [
            {"component_surface": "catur", "role": "purva_pada", "confidence": 0.92},
            {"component_surface": "daśa", "role": "uttara_pada", "confidence": 0.92},
        ],
    },
    "nirviśeṣaḥ": {
        "type": "bahuvrihi",
        "vigraha": "nirgato viśeṣo yasmāt saḥ",
        "confidence": 0.91,
        "children": [
            {"component_surface": "nis", "role": "purva_pada", "confidence": 0.93},
            {"component_surface": "viśeṣaḥ", "role": "uttara_pada", "confidence": 0.93},
        ],
    },
}

_NUMERAL_PREFIXES = {"dvi", "tri", "catur", "pañca", "ṣaṭ", "sapta", "aṣṭa", "nava", "daśa"}
_AVYAYA_PREFIXES = {"yathā", "upa", "anu", "prati", "nir", "sa"}

def _infer_compound_type(p1: str, p2: str) -> str:
    if p1 in _AVYAYA_PREFIXES:
        return "avyayibhava"
    if p1 in _NUMERAL_PREFIXES:
        return "dvigu"
    if p2.endswith("au"):
        return "dvandva"
    return "tatpurusha"

def generate_compound_tree(surface: str) -> Optional[dict]:
    # Compounds never contain spaces
    if " " in surface:
        return None
    clean = surface.rstrip("ḥ").rstrip("m")
    n = len(clean)

    for i in range(2, n - 1):
        p1 = clean[:i]
        p2 = clean[i:]

        hit1 = _lexicon.lookup(p1)
        stem1 = p1
        if not hit1 and _lexicon.lookup(p1 + "a"):
            hit1 = _lexicon.lookup(p1 + "a")
            stem1 = p1 + "a"

        hit2 = _lexicon.lookup(p2) or _lexicon.lookup(p2 + "ḥ") or _lexicon.lookup(p2 + "m")
        if not hit2 and _lexicon.lookup(p2 + "a"):
            hit2 = _lexicon.lookup(p2 + "a")

        if hit1 and hit2:
            ctype = _infer_compound_type(stem1, p2)
            c2_surf = surface[i:]
            return {
                "samasa_id": "S_GEN_0",
                "component_surface": surface,
                "role": "single",
                "type": ctype,
                "vigraha": f"{stem1} ca {p2}",
                "confidence": 0.91,
                "children": [
                    {
                        "samasa_id": "S_GEN_0.1",
                        "component_surface": stem1,
                        "role": "purva_pada",
                        "confidence": 0.92,
                    },
                    {
                        "samasa_id": "S_GEN_0.2",
                        "component_surface": c2_surf,
                        "role": "uttara_pada",
                        "confidence": 0.92,
                    },
                ],
            }
    return None

def build_tree(surface: str) -> Optional[dict]:
    if surface in _COMPOUND_DATA:
        info = _COMPOUND_DATA[surface]
        node = {
            "samasa_id": "S0",
            "component_surface": surface,
            "role": "single",
            "type": info["type"],
            "vigraha": info["vigraha"],
            "confidence": info["confidence"],
        }
        if "children" in info:
            node["children"] = info["children"]
        return node
    return generate_compound_tree(surface)



def recursive_split_compound(word: str, depth: int = 1) -> Optional[Dict[str, Any]]:
    """
    Recursively splits compounds up to depth 3 adhering to samasa_node schema.
    """
    if depth > 3 or len(word) < 4:
        return None

    # Check basic split
    split_res = split_compound(word) if "split_compound" in globals() else None
    if not split_res and "decompose" in globals():
        split_res = decompose(word)

    if not split_res:
        # Classical 3-stem heuristic prefix scan: e.g. raja + putra + vadha
        prefixes = ["raja", "rāja", "deva", "nara", "maha", "mahā", "putra", "satya", "dharma"]
        for p in prefixes:
            if word.startswith(p) and len(word) > len(p) + 2:
                rem = word[len(p):]
                sub = recursive_split_compound(rem, depth + 1)
                return {
                    "surface": word,
                    "compound_type": "tatpurusha",
                    "components": [p, rem],
                    "left_stem": p,
                    "right_stem": rem,
                    "depth": depth,
                    "sub_tree": sub,
                    "confidence": 0.85
                }
        return None

    left = split_res.get("left", split_res.get("components", ["", ""])[0])
    right = split_res.get("right", split_res.get("components", ["", ""])[1] if len(split_res.get("components", [])) > 1 else "")
    ctype = split_res.get("compound_type", "tatpurusha")

    sub_right = recursive_split_compound(right, depth + 1) if len(right) > 3 else None

    return {
        "surface": word,
        "compound_type": ctype,
        "components": [left, right],
        "left_stem": left,
        "right_stem": right,
        "depth": depth,
        "sub_tree": sub_right,
        "confidence": split_res.get("confidence", 0.85)
    }
