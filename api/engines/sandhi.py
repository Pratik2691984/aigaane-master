from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import re
import unicodedata


INDEPENDENT_VOWELS = {
    "\u0905": "a",
    "\u0906": "\u0101",
    "\u0907": "i",
    "\u0908": "\u012b",
    "\u0909": "u",
    "\u090a": "\u016b",
    "\u090b": "\u1e5b",
    "\u0960": "\u1e5d",
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
    "e": "\u0947",
    "ai": "\u0948",
    "o": "\u094b",
    "au": "\u094c",
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

    savarna_dirgha = {
        ("a", "a"): "\u0101",
        ("a", "\u0101"): "\u0101",
        ("\u0101", "a"): "\u0101",
        ("\u0101", "\u0101"): "\u0101",
        ("i", "i"): "\u012b",
        ("i", "\u012b"): "\u012b",
        ("\u012b", "i"): "\u012b",
        ("\u012b", "\u012b"): "\u012b",
        ("u", "u"): "\u016b",
        ("u", "\u016b"): "\u016b",
        ("\u016b", "u"): "\u016b",
        ("\u016b", "\u016b"): "\u016b",
    }
    long_vowel = savarna_dirgha.get((left.vowel, right.vowel))
    if long_vowel:
        merged = add_vowel_to_final_carrier(base, left, long_vowel) + remainder
        return {
            "merged": merged,
            "sutra": "6.1.101",
            "sutra_name": "\u0905\u0915\u0903 \u0938\u0935\u0930\u094d\u0923\u0947 \u0926\u0940\u0930\u094d\u0918\u0903",
            "type": "vowel_sandhi",
            "trace": trace("6.1.101", left_word, right_word, left, right, merged),
        }

    if left.vowel in {"a", "\u0101"} and right.vowel in {"i", "\u012b"}:
        merged = add_vowel_to_final_carrier(base, left, "e") + remainder
        return {
            "merged": merged,
            "sutra": "6.1.87",
            "sutra_name": "\u0906\u0926\u094d \u0917\u0941\u0923\u0903",
            "type": "vowel_sandhi",
            "trace": trace("6.1.87", left_word, right_word, left, right, merged),
        }

    if left.vowel in {"i", "\u012b"} and right.vowel in {"a", "\u0101", "i", "\u012b", "u", "\u016b", "e", "o", "ai", "au"}:
        merged = compose_yan(base, left, "\u092f", right.vowel, remainder)
        return {
            "merged": merged,
            "sutra": "6.1.77",
            "sutra_name": "\u0907\u0915\u094b \u092f\u0923\u091a\u093f",
            "type": "vowel_sandhi",
            "trace": trace("6.1.77", left_word, right_word, left, right, merged),
        }

    raise SandhiException("No supported vowel sandhi rule matched.")
