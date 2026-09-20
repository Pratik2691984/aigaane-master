from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import re
import unicodedata
try:
    from api.engines.trace_graph import DerivationStep, DerivationTraceGraph
except ModuleNotFoundError:
    from engines.trace_graph import DerivationStep, DerivationTraceGraph
from engine.phonology.pratyahara import is_member, sthane_antaratamah, PHONETIC_COORDS

INDEPENDENT_VOWELS = {
    "\u0905": "a",
    "\u0906": "\u0101",
    "\u0907": "i",
    "\u0908": "\u012b",
    "\u0909": "u",
    "\u090a": "\u016b",
    "\u090b": "\u1e5b",
    "\u0960": "\u1e5d",
    "\u090c": "\u1e37",
    "\u090f": "e",
    "\u0910": "ai",
    "\u0913": "o",
    "\u0914": "au",
}

VOWEL_SIGNS = {
    "\u093e": "\u0101",
    "\u093f": "i",
    "\u0940": "\u012b",
    "\u0941": "u",
    "\u0942": "\u016b",
    "\u0943": "\u1e5b",
    "\u0944": "\u1e5d",
    "\u0962": "\u1e37",
    "\u0947": "e",
    "\u0948": "ai",
    "\u094b": "o",
    "\u094c": "au",
}

VOWEL_TO_SIGN = {
    "\u0101": "\u093e",
    "i": "\u093f",
    "\u012b": "\u0940",
    "u": "\u0941",
    "\u016b": "\u0942",
    "\u1e5b": "\u0943",
    "\u1e5d": "\u0944",
    "\u1e37": "\u0962",
    "e": "\u0947",
    "ai": "\u0948",
    "o": "\u094b",
    "au": "\u094c",
}

# Mapping between IAST and Devanagari phonemes for Pratyahara engine
IAST_TO_DEVA = {
    "a": "अ", "\u0101": "आ",
    "i": "इ", "\u012b": "ई",
    "u": "उ", "\u016b": "ऊ",
    "\u1e5b": "ऋ", "\u1e5d": "ॠ",
    "\u1e37": "ऌ",
    "e": "ए", "ai": "ऐ",
    "o": "ओ", "au": "औ"
}

DEVA_TO_IAST = {v: k for k, v in IAST_TO_DEVA.items()}

# 1.1.50 savarna dirgha mapping
DIRGHA_MAP = {
    "अ": "आ", "आ": "आ",
    "इ": "ई", "ई": "ई",
    "उ": "ऊ", "ऊ": "ऊ",
    "ऋ": "ॠ", "ॠ": "ॠ",
    "ऌ": "ऌ"
}

# Guna map for 6.1.87
GUNA_MAP = {
    "इ": "ए", "ई": "ए",
    "उ": "ओ", "ऊ": "ओ",
    "ऋ": "अर्", "ॠ": "अर्",
    "ऌ": "अल्"
}

CONSONANT_RE = re.compile(r"[\u0915-\u0939]")
VIRAMA = "\u094d"


class SandhiException(Exception):
    status_code = 400
    code = "sandhi_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass
class VowelBoundary:
    vowel: str
    orthographic_start: int
    orthographic_end: int
    carrier_start: Optional[int]
    carrier_end: Optional[int]
    kind: str


def normalize_word(value: str, field_name: str) -> str:
    if value is None or not isinstance(value, str):
        raise SandhiException(f"{field_name} is required.")
    normalized = unicodedata.normalize("NFC", value.strip())
    if not normalized:
        raise SandhiException(f"{field_name} must not be empty.")
    return normalized


def is_devanagari(text: str) -> bool:
    return any("\u0900" <= char <= "\u097f" for char in text)


def final_vowel_boundary(word: str) -> Optional[VowelBoundary]:
    index = len(word) - 1
    while index >= 0:
        char = word[index]
        if char in VOWEL_SIGNS:
            carrier = index - 1
            while carrier >= 0 and not CONSONANT_RE.match(word[carrier]):
                carrier -= 1
            return VowelBoundary(VOWEL_SIGNS[char], index, index + 1, carrier, carrier + 1 if carrier >= 0 else None, "vowel_sign")
        if char in INDEPENDENT_VOWELS:
            return VowelBoundary(INDEPENDENT_VOWELS[char], index, index + 1, index, index + 1, "independent")
        if CONSONANT_RE.match(char):
            next_char = word[index + 1] if index + 1 < len(word) else ""
            if next_char != VIRAMA:
                return VowelBoundary("a", index + 1, index + 1, index, index + 1, "inherent")
        index -= 1
    return None


def initial_vowel_boundary(word: str) -> Optional[VowelBoundary]:
    for index, char in enumerate(word):
        if char.isspace():
            continue
        if char in INDEPENDENT_VOWELS:
            return VowelBoundary(INDEPENDENT_VOWELS[char], index, index + 1, index, index + 1, "independent")
        return None
    return None


def remove_final_vowel(word: str, boundary: VowelBoundary) -> str:
    if boundary.kind == "vowel_sign":
        return word[:boundary.orthographic_start] + word[boundary.orthographic_end:]
    return word


def remove_initial_vowel(word: str, boundary: VowelBoundary) -> str:
    return word[:boundary.orthographic_start] + word[boundary.orthographic_end:]


def add_vowel_to_final_carrier(base: str, boundary: VowelBoundary, vowel: str) -> str:
    if boundary.carrier_end is None:
        return base + VOWEL_TO_SIGN.get(vowel, "")
    sign = VOWEL_TO_SIGN.get(vowel)
    if sign is None:
        return base
    return base[:boundary.carrier_end] + sign + base[boundary.carrier_end:]


def compose_yan(base: str, boundary: VowelBoundary, glide: str, next_vowel: str, remainder: str) -> str:
    glide_sign = VOWEL_TO_SIGN.get(next_vowel, "")
    glide_akshara = glide + glide_sign
    if boundary.carrier_end is not None:
        return base[:boundary.carrier_end] + VIRAMA + glide_akshara + base[boundary.carrier_end:] + remainder
    return base + glide_akshara + remainder


def trace(rule: str, word1: str, word2: str, left: VowelBoundary, right: VowelBoundary, merged: str) -> List[Dict[str, Any]]:
    return [
        {"layer": "orthographic_input", "word1": word1, "word2": word2},
        {"layer": "phonological_representation", "left_vowel": left.vowel, "right_vowel": right.vowel},
        {"layer": "sandhi_rule_engine", "sutra": rule},
        {"layer": "orthographic_recomposition", "merged": merged},
    ]


def derivation_path(
    rule: str,
    sutra_name: str,
    operation: str,
    word1: str,
    word2: str,
    merged: str,
) -> List[Dict[str, str]]:
    return DerivationTraceGraph(
        steps=[
            DerivationStep(
                sutra=rule,
                sutra_name=sutra_name,
                operation=operation,
                input_state=f"{word1} + {word2}",
                output_state=merged,
                engine_node="Node 2A Vowel Sandhi",
            )
        ]
    ).to_list()


def is_savarna(v1: str, v2: str) -> bool:
    """1.1.9 tulyāsya-prayatnaṁ savarṇam (matches sthāna & ābhyantara-prayatna)"""
    if v1 not in PHONETIC_COORDS or v2 not in PHONETIC_COORDS:
        return False
    # Check sthāna (index 0) and prayatna (index 1)
    return PHONETIC_COORDS[v1][:2] == PHONETIC_COORDS[v2][:2]


def is_ak(v: str) -> bool:
    """Extension of 'अक्' pratyāhāra to include short and dīrgha forms."""
    base_deva = {"आ": "अ", "ई": "इ", "ऊ": "उ", "ॠ": "ऋ"}.get(v, v)
    return is_member(base_deva, "अक्")


def is_ik(v: str) -> bool:
    """Extension of 'इक्' pratyāhāra (इ, उ, ऋ, ऌ and their dīrgha variants)."""
    base_deva = {"ई": "इ", "ऊ": "उ", "ॠ": "ऋ"}.get(v, v)
    return is_member(base_deva, "इक्")


def is_ac(v: str) -> bool:
    """Extension of 'अच्' pratyāhāra (all vowels short and long)."""
    base_deva = {"आ": "अ", "ई": "इ", "ऊ": "उ", "ॠ": "ऋ"}.get(v, v)
    return is_member(base_deva, "अच्")


def analyze_vowel_sandhi(word1: str, word2: str) -> Dict[str, Any]:
    left_word = normalize_word(word1, "word1")
    right_word = normalize_word(word2, "word2")
    if not (is_devanagari(left_word) and is_devanagari(right_word)):
        raise SandhiException("Only Devanagari vowel sandhi is enabled in this phase.")

    left = final_vowel_boundary(left_word)
    right = initial_vowel_boundary(right_word)
    if left is None or right is None:
        raise SandhiException("Both words must expose vowel boundaries.")

    remainder = remove_initial_vowel(right_word, right)
    base = remove_final_vowel(left_word, left)

    v1_deva = IAST_TO_DEVA.get(left.vowel)
    v2_deva = IAST_TO_DEVA.get(right.vowel)

    if not v1_deva or not v2_deva:
        raise SandhiException("Unrecognized vowel phonemes.")

    # Rule 1: Sūtra 6.1.101 akaḥ savarṇe dīrghaḥ
    if is_ak(v1_deva) and is_savarna(v1_deva, v2_deva):
        long_vowel_deva = DIRGHA_MAP.get(v1_deva, v1_deva)
        long_vowel_iast = DEVA_TO_IAST[long_vowel_deva]
        merged = add_vowel_to_final_carrier(base, left, long_vowel_iast) + remainder
        sutra_name = "\u0905\u0915\u0903 \u0938\u0935\u0930\u094d\u0923\u0947 \u0926\u0940\u0930\u094d\u0918\u0903"
        return {
            "merged": merged,
            "sutra": "6.1.101",
            "sutra_name": sutra_name,
            "type": "vowel_sandhi",
            "trace": trace("6.1.101", left_word, right_word, left, right, merged),
            "derivation_path": derivation_path("6.1.101", sutra_name, "savarna_dirgha_substitution", left_word, right_word, merged),
        }

    # Rule 2: Sūtra 6.1.87 ād guṇaḥ
    if v1_deva in {"अ", "आ"} and v2_deva in GUNA_MAP:
        guna_char = GUNA_MAP[v2_deva]
        guna_iast = DEVA_TO_IAST.get(guna_char, "e")
        merged = add_vowel_to_final_carrier(base, left, guna_iast) + remainder
        sutra_name = "\u0906\u0926\u094d \u0917\u0941\u0923\u0903"
        return {
            "merged": merged,
            "sutra": "6.1.87",
            "sutra_name": sutra_name,
            "type": "vowel_sandhi",
            "trace": trace("6.1.87", left_word, right_word, left, right, merged),
            "derivation_path": derivation_path("6.1.87", sutra_name, "guna_substitution", left_word, right_word, merged),
        }

    # Rule 3: Sūtra 6.1.77 iko yaṇ aci
    if is_ik(v1_deva) and is_ac(v2_deva) and not is_savarna(v1_deva, v2_deva):
        # Dynamically determine semivowel using 1.1.50 sthāne'ntaratamaḥ
        yan_candidates = ["य", "व", "र", "ल"]
        glide = sthane_antaratamah(v1_deva, yan_candidates)
        merged = compose_yan(base, left, glide, right.vowel, remainder)
        sutra_name = "\u0907\u0915\u094b \u092f\u0923\u091a\u093f"
        return {
            "merged": merged,
            "sutra": "6.1.77",
            "sutra_name": sutra_name,
            "type": "vowel_sandhi",
            "trace": trace("6.1.77", left_word, right_word, left, right, merged),
            "derivation_path": derivation_path("6.1.77", sutra_name, "yan_substitution", left_word, right_word, merged),
        }

    raise SandhiException("No supported vowel sandhi rule matched.")