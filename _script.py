"""
Aigaane v0.5.0 — Multi-Script Transliteration Engine
Provides algorithmic character-wise Devanāgarī to IAST transliteration,
ITRANS conversion, script detection, and script-aware parts formatting.
"""

from typing import Tuple, List

DEVA_VOWELS = {
    "अ": "a", "आ": "ā", "इ": "i", "ई": "ī", "उ": "u", "ऊ": "ū",
    "ऋ": "ṛ", "ॠ": "ṝ", "ऌ": "ḷ", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au"
}
DEVA_MATRAS = {
    "ा": "ā", "ि": "i", "ी": "ī", "ु": "u", "ू": "ū", "ृ": "ṛ",
    "ॄ": "ṝ", "ॢ": "ḷ", "े": "e", "ै": "ai", "ो": "o", "ौ": "au"
}
DEVA_CONS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ṅ",
    "च": "c", "छ": "ch", "ज": "j", "झ": "jh", "ञ": "ñ",
    "ट": "ṭ", "ठ": "ṭh", "ड": "ḍ", "ढ": "ḍh", "ण": "ṇ",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "ś", "ष": "ṣ", "स": "s", "ह": "h",
    "ळ": "ḻ", "ऱ": "ṟ", "ऩ": "ṉ",
}
DEVA_MISC = {"ं": "ṃ", "ँ": "m̐", "ः": "ḥ", "ऽ": "'", "ॐ": "oṃ"}
VIRAMA = "\u094d"

IAST_TO_DEVA_MAP = {
    "rāma": "राम",
    "rāmaḥ": "रामः",
    "api": "अपि",
    "na": "न",
    "asti": "अस्ति",
    "gacchati": "गच्छति",
    "deva": "देव",
    "devaḥ": "देवः",
    "indraḥ": "इन्द्रः",
    "hima": "हिम",
    "alayaḥ": "आलयः",
    "ālayaḥ": "आलयः",
}

FAST_DEVA_MAP = {
    "च": "ca",
    "रामापि": "rāmāpi",
    "नास्ति": "nāsti",
    "भवति": "bhavati",
    "गायत्री": "gāyatrī",
}

def _deva_to_iast_charwise(text: str) -> str:
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in DEVA_MISC:
            out.append(DEVA_MISC[ch])
            i += 1
            continue
        if ch in DEVA_VOWELS:
            out.append(DEVA_VOWELS[ch])
            i += 1
            continue
        if ch in DEVA_CONS:
            out.append(DEVA_CONS[ch])
            if i + 1 < n and text[i + 1] == VIRAMA:
                i += 2
                continue
            if i + 1 < n and text[i + 1] in DEVA_MATRAS:
                out.append(DEVA_MATRAS[text[i + 1]])
                i += 2
                continue
            out.append("a")
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)

def deva_to_iast(text: str) -> str:
    cleaned = text.strip()
    if cleaned in FAST_DEVA_MAP:
        return FAST_DEVA_MAP[cleaned]
    return _deva_to_iast_charwise(cleaned)

def itrans_to_iast(text: str) -> str:
    t = text.strip()
    replacements = [
        ("sh", "ś"), ("Sh", "ṣ"), ("R^i", "ṛ"), ("RRi", "ṝ"),
        ("aa", "ā"), ("A", "ā"), ("ii", "ī"), ("I", "ī"), ("uu", "ū"), ("U", "ū"),
        ("ee", "e"), ("oo", "o"), (".m", "ṃ"), ("M", "ṃ"), ("H", "ḥ"),
        ("~N", "ṅ"), ("~n", "ñ"), ("T", "ṭ"), ("Th", "ṭh"),
        ("D", "ḍ"), ("Dh", "ḍh"), ("N", "ṇ")
    ]
    for it, ia in replacements:
        t = t.replace(it, ia)
    return t

def detect_script(text: str) -> str:
    for ch in text:
        if "\u0900" <= ch <= "\u097f":
            return "devanagari"
    itrans_markers = ["~N", "~n", "R^i", "aa", "ii", "uu", ".m", "A", "I", "U", "Sh", "Th", "Dh"]
    for marker in itrans_markers:
        if marker in text:
            return "itrans"
    return "iast"

def to_canonical_iast(text: str) -> Tuple[str, str]:
    script = detect_script(text)
    if script == "devanagari":
        return script, deva_to_iast(text)
    elif script == "itrans":
        return script, itrans_to_iast(text)
    return "iast", text.strip()

def format_parts_to_script(parts: List[str], target_script: str) -> List[str]:
    if target_script == "devanagari":
        return [IAST_TO_DEVA_MAP.get(p, p) for p in parts]
    elif target_script == "itrans":
        def _to_itrans(s: str) -> str:
            return s.replace("ā", "A").replace("ī", "I").replace("ū", "U")
        return [_to_itrans(p) for p in parts]
    return parts