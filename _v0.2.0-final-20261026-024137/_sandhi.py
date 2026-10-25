"""
Aigaane v0.2.0 — Closed-Set Exact Sandhi Splits for Category A
"""

from typing import List, Tuple, Optional

_EXACT_SPLITS = {
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

def split_surface(surface: str) -> Optional[Tuple[List[str], str, str, float]]:
    return _EXACT_SPLITS.get(surface)
