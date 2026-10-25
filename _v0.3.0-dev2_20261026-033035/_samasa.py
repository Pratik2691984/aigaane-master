"""
Aigaane v0.2.0 — Samasa (compound) tree builder
"""

from typing import Dict, Optional, Tuple

_COMPOUND_DATA: Dict[str, Tuple[str, str, str, float, Optional[dict]]] = {
    "rājaputraḥ":        ("tatpurusha",   "rāja",   "putra",   0.90, None),
    "nīlotpalam":        ("karmadharaya", "nīla",   "utpala",  0.92, None),
    "pītāmbaraḥ":        ("bahuvrihi",    "pīta",   "ambara",  0.90, None),
    "rāmalakṣmaṇau":     ("dvandva",      "rāma",   "lakṣmaṇa",0.91, None),
    "yathāśakti":        ("avyayibhava",  "yathā",  "śakti",   0.89, None),
    "saptarṣiḥ":         ("dvigu",        "sapta",  "ṛṣi",     0.90, None),
    "mahārājaḥ":         ("karmadharaya", "mahā",   "rāja",    0.92, None),
    "devadattaḥ":        ("tatpurusha",   "deva",   "datta",   0.90, None),
    "somasūryau":        ("dvandva",      "soma",   "sūrya",   0.91, None),
    "rājaputravadhaḥ":   ("tatpurusha",   "rājaputra", "vadha", 0.88,
                          {"rājaputra": ("tatpurusha", "rāja", "putra", 0.91)}),
    "jagannāthaḥ":       ("tatpurusha",   "jagat",  "nātha",   0.90, None),
    "atyuttamaḥ":        ("karmadharaya", "ati",    "uttama",  0.89, None),
    "bhūpatiḥ":          ("tatpurusha",   "bhū",    "pati",    0.90, None),
    "caturdaśa":         ("dvigu",        "catur",  "daśa",    0.92, None),
    "nirviśeṣaḥ":        ("bahuvrihi",    "nir",    "viśeṣa",  0.90, None),
}

def _leaf(component_surface: str, role: str, confidence: float) -> dict:
    return {
        "component_surface": component_surface,
        "role": role,
        "confidence": confidence,
    }

def _build_component(surface: str, role: str, nested_map: Optional[dict]) -> dict:
    if nested_map and surface in nested_map:
        inner_type, inner_purva, inner_uttara, inner_conf = nested_map[surface]
        return {
            "type": inner_type,
            "component_surface": surface,
            "role": role,
            "confidence": inner_conf,
            "children": [
                _leaf(inner_purva, "purva_pada", inner_conf),
                _leaf(inner_uttara, "uttara_pada", inner_conf),
            ],
        }
    return _leaf(surface, role, 0.90)

def build_tree(surface: str) -> Optional[dict]:
    row = _COMPOUND_DATA.get(surface)
    if row is None:
        return None

    type_, purva, uttara, conf, nested = row
    return {
        "type": type_,
        "component_surface": surface,
        "role": "single",
        "confidence": conf,
        "children": [
            _build_component(purva, "purva_pada", nested),
            _build_component(uttara, "uttara_pada", nested),
        ],
    }
