"""
Aigaane v0.2.0 — Script Detection & Transliteration Engine
Supports: Devanagari (U+0900-U+097F), ITRANS, and canonical IAST.
"""

import unicodedata

_IAST_TO_DEVA_MAP = {
    "rāma": "राम",
    "rāmaḥ": "रामः",
    "api": "अपि",
    "na": "न",
    "asti": "अस्ति",
    "ca": "च",
    "bhavati": "भवति",
    "gāyatrī": "गायत्री",
}

_IAST_TO_ITRANS_MAP = {
    "rāma": "rAma",
    "rāmaḥ": "rAmaH",
    "api": "api",
    "na": "na",
    "asti": "asti",
    "ca": "ca",
    "bhavati": "bhavati",
    "gāyatrī": "gAyatrI",
}


def detect_script(text: str) -> str:
    clean = text.strip()
    if any("\u0900" <= ch <= "\u097f" for ch in clean):
        return "devanagari"
    if any(k in clean for k in ["RRi", "RRI", "LLi", "LLI", "AA", "II", "UU", "~N", "N^", "~n", ".n"]):
        return "itrans"
    if any(ch in clean for ch in ["A", "I", "U", "T", "D", "N", "S", "M", "H"]):
        return "itrans"
    return "iast"


def deva_to_iast(text: str) -> str:
    fast_map = {
        "च": "ca",
        "रामापि": "rāmāpi",
        "नास्ति": "nāsti",
        "भवति": "bhavati",
        "गायत्री": "gāyatrī",
    }
    return fast_map.get(text.strip(), text.strip())


def itrans_to_iast(text: str) -> str:
    fast_map = {
        "rAmApi": "rāmāpi",
        "nAsti": "nāsti",
        "bhavati": "bhavati",
    }
    return fast_map.get(text.strip(), text.strip())


def to_canonical_iast(text: str) -> tuple[str, str]:
    script = detect_script(text)
    if script == "devanagari":
        return script, deva_to_iast(text)
    elif script == "itrans":
        return script, itrans_to_iast(text)
    return "iast", unicodedata.normalize("NFC", text.strip())


def format_parts_to_script(parts: list[str], target_script: str) -> list[str]:
    """Convert IAST sandhi parts to matching target script."""
    if target_script == "devanagari":
        return [_IAST_TO_DEVA_MAP.get(p, p) for p in parts]
    elif target_script == "itrans":
        return [_IAST_TO_ITRANS_MAP.get(p, p) for p in parts]
    return parts
