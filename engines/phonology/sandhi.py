"""
engines/phonology/sandhi.py
Svara + Hal + Visarga sandhi — Aṣṭādhyāyī 6.1.x, 8.4.x, 8.3.x
"""

import re
from typing import Optional

from engines.phonology.pratyahara import PratyaharaEngine
from engines.phonology.siksha import SikshaTensor

_LONG_MAP = {"a": "ā", "i": "ī", "u": "ū", "ṛ": "ṝ", "ḷ": "ḹ"}
_GUNA_MAP = {"i": "e", "ī": "e", "u": "o", "ū": "o",
             "ṛ": "ar", "ṝ": "ar", "ḷ": "al", "ḹ": "al"}
_VRDDHI_MAP = {"e": "ai", "ai": "ai", "o": "au", "au": "au"}
_SEMIVOWEL_MAP = {"i": "y", "ī": "y", "u": "v", "ū": "v",
                  "ṛ": "r", "ṝ": "r", "ḷ": "l", "ḹ": "l"}

_DENTAL_TO_PALATAL = {"t": "c", "th": "ch", "d": "j", "dh": "jh",
                      "n": "ñ", "s": "ś"}
_DENTAL_TO_RETROFLEX = {"t": "ṭ", "th": "ṭh", "d": "ḍ", "dh": "ḍh",
                        "n": "ṇ", "s": "ṣ"}
_PALATALS = frozenset({"c", "ch", "j", "jh", "ñ", "ś"})
_RETROFLEXES = frozenset({"ṭ", "ṭh", "ḍ", "ḍh", "ṇ", "ṣ"})

_HAŚ = frozenset({
    "a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "ḹ",
    "e", "ai", "o", "au",
    "g", "gh", "ṅ", "j", "jh", "ñ", "ḍ", "ḍh", "ṇ",
    "d", "dh", "n", "b", "bh", "m", "y", "r", "l", "v", "h",
})
_ŚAR = frozenset({"ś", "ṣ", "s"})
_KHAR = frozenset({"k", "kh", "c", "ch", "ṭ", "ṭh", "t", "th",
                   "p", "ph", "ś", "ṣ", "s"})
_VOWELS = frozenset({"a", "ā", "i", "ī", "u", "ū", "ṛ", "ṝ", "ḷ", "ḹ",
                     "e", "ai", "o", "au"})
_DIGRAPH_CONSONANTS = frozenset({"kh", "gh", "ch", "jh", "ṭh", "ḍh",
                                 "th", "dh", "ph", "bh"})
_SINGLE_CONSONANTS = frozenset({"k", "g", "ṅ", "c", "j", "ñ", "ṭ", "ḍ",
                                "ṇ", "t", "d", "n", "p", "b", "m",
                                "y", "r", "l", "v", "ś", "ṣ", "s", "h"})


def _first_phoneme(word: str) -> str:
    if not word:
        return ""
    if word[0] in {"ṃ", "ḥ"}:
        return word[0]
    for v in sorted(_VOWELS, key=len, reverse=True):
        if word.startswith(v):
            return v
    for c in _DIGRAPH_CONSONANTS:
        if word.startswith(c):
            return c
    if word[0] in _SINGLE_CONSONANTS:
        return word[0]
    return word[0]


class SandhiEngine:
    def __init__(self):
        self.pratyahara = PratyaharaEngine()
        self.siksha = SikshaTensor()

    def combine_svara(self, p1: str, p2: str) -> Optional[str]:
        c1 = self.siksha.get(p1)
        c2 = self.siksha.get(p2)
        if not c1 or not c2 or not c1.is_vowel or not c2.is_vowel:
            return None
        if self.siksha.are_savarṇa(p1, p2):
            if p1 in _LONG_MAP:
                return _LONG_MAP[p1]
            if p1 in _LONG_MAP.values():
                return p1
            return p1
        if p1 in {"a", "ā"} and p2 in _GUNA_MAP:
            return _GUNA_MAP[p2]
        if p1 in {"a", "ā"} and p2 in _VRDDHI_MAP:
            return _VRDDHI_MAP[p2]
        if p1 in _SEMIVOWEL_MAP and c2.is_vowel:
            return _SEMIVOWEL_MAP[p1] + p2
        return None

    def combine_hal(self, consonant: str, following: str) -> Optional[str]:
        c_obj = self.siksha.get(consonant)
        f_obj = self.siksha.get(following)
        if not c_obj or not f_obj:
            return None
        if c_obj.is_vowel or f_obj.is_vowel:
            return None
        if following in _PALATALS and consonant in _DENTAL_TO_PALATAL:
            return _DENTAL_TO_PALATAL[consonant]
        if following in _RETROFLEXES and consonant in _DENTAL_TO_RETROFLEX:
            return _DENTAL_TO_RETROFLEX[consonant]
        return None

    def combine_visarga(self, preceding_vowel: str, following: str) -> Optional[str]:
        if not preceding_vowel or not following:
            return None
        if preceding_vowel in {"a", "ā"} and following == "a":
            return "o'"
        if preceding_vowel == "a" and following in _HAŚ and following != "a":
            return "o"
        if preceding_vowel == "ā" and following in _HAŚ and following != "a":
            return "ār"
        if following in _ŚAR:
            return following
        if following in _KHAR:
            return "ḥ"
        return "ḥ"

    def combine_visarga_with_context(self, word_final: str, following: str):
        if not word_final or not word_final.endswith("ḥ"):
            return None
        m = re.search(r"([aāiīuūṛṝḷḹeoaiau])ḥ$", word_final)
        preceding = m.group(1) if m else "a"
        following_phoneme = _first_phoneme(following)
        result = self.combine_visarga(preceding, following_phoneme)
        if result is None:
            return None
        if preceding in {"a", "ā"} and following_phoneme == "a":
            return (result, "6.1.109")
        if preceding == "a" and following_phoneme in _HAŚ and following_phoneme != "a":
            return (result, "6.1.114")
        if preceding == "ā" and following_phoneme in _HAŚ and following_phoneme != "a":
            return (result, "6.1.113")
        if following_phoneme in _ŚAR:
            return (result, "8.3.12")
        if following_phoneme in _KHAR:
            return (result, "8.3.34")
        return (result, "8.3.15")

    def combine(self, p1: str, p2: str) -> str:
        svara = self.combine_svara(p1, p2)
        if svara is not None:
            return svara
        hal = self.combine_hal(p1, p2)
        if hal is not None:
            return hal
        return p1 + p2


if __name__ == "__main__":
    S = SandhiEngine()
    assert S.combine_svara("a", "a") == "ā"
    assert S.combine_svara("a", "i") == "e"
    assert S.combine_svara("a", "e") == "ai"
    assert S.combine_svara("i", "a") == "ya"
    assert S.combine_hal("t", "c") == "c"
    assert S.combine_hal("t", "ṭ") == "ṭ"
    assert S.combine_visarga_with_context("aḥ", "iti") == ("o'", "6.1.109")
    assert S.combine_visarga_with_context("aḥ", "gacchati") == ("o", "6.1.114")
    print("OK sandhi.py")