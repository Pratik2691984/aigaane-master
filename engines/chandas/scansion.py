"""
engines/chandas/scansion.py
Deterministic laghu/guru scanner for IAST Sanskrit.
"""

import re
from typing import List, NamedTuple

SHORT_VOWELS = frozenset({"a", "i", "u", "ṛ", "ḷ"})
LONG_VOWELS = frozenset({"ā", "ī", "ū", "ṝ", "ḹ", "e", "ai", "o", "au"})
ALL_VOWELS = SHORT_VOWELS | LONG_VOWELS

CONSONANTS = (
    "kh", "gh", "ch", "jh", "ṭh", "ḍh", "th", "dh", "ph", "bh",
    "k", "g", "ṅ", "c", "j", "ñ", "ṭ", "ḍ", "ṇ", "t", "d", "n",
    "p", "b", "m", "y", "r", "l", "v", "ś", "ṣ", "s", "h",
)
ANUSVARA = "ṃ"
VISARGA = "ḥ"
AVAGRAHA = "'"


class Syllable(NamedTuple):
    text: str
    weight: str
    position: int


class ScansionResult(NamedTuple):
    input: str
    syllables: List[Syllable]
    pattern: str
    length: int
    is_valid_anuṣṭubh: bool


def _tokenize_iast(text: str) -> List[str]:
    tokens: List[str] = []
    i, n = 0, len(text)
    while i < n:
        matched = False
        for length in (2, 1):
            chunk = text[i:i + length]
            if (chunk in CONSONANTS or chunk in ALL_VOWELS
                    or chunk in (ANUSVARA, VISARGA, AVAGRAHA)):
                tokens.append(chunk)
                i += length
                matched = True
                break
        if not matched:
            i += 1
    return tokens


def _syllabify(tokens: List[str]) -> List[str]:
    """
    Syllabify a linear stream of IAST phones.
    Rule: a consonant cluster between two vowels assigns all but its last
    member to the preceding syllable.
    """
    syllables: List[str] = []
    current = ""
    i, n = 0, len(tokens)
    while i < n:
        tok = tokens[i]
        if tok in CONSONANTS:
            current += tok
            i += 1
            continue
        if tok in ALL_VOWELS:
            current += tok
            i += 1
            # Absorb anusvāra / visarga
            if i < n and tokens[i] in (ANUSVARA, VISARGA):
                current += tokens[i]
                i += 1
            # Peek ahead: gather consonants before next vowel
            k = i
            consonants: List[str] = []
            while k < n and tokens[k] in CONSONANTS:
                consonants.append(tokens[k])
                k += 1
            # If we hit another vowel, split the consonant cluster
            if k < n and tokens[k] in ALL_VOWELS:
                if consonants:
                    # All but the last consonant go to current syllable
                    current += "".join(consonants[:-1])
                    syllables.append(current)
                    current = consonants[-1]
                    i = k
                    continue
            # No following vowel: close syllable, keep consonants
            current += "".join(consonants)
            i = k
            syllables.append(current)
            current = ""
            continue
        if tok in (ANUSVARA, VISARGA):
            if current:
                current += tok
                syllables.append(current)
                current = ""
            elif syllables:
                syllables[-1] += tok
            i += 1
            continue
        if tok == AVAGRAHA:
            if syllables:
                syllables[-1] += tok
            i += 1
            continue
        i += 1
    if current:
        syllables.append(current)
    return syllables

def _weight(syllable: str) -> str:
    if syllable.endswith(VISARGA):
        return "G"
    if syllable.endswith(ANUSVARA):
        return "G"
    vowel = None
    for ch in syllable:
        if ch in ALL_VOWELS:
            vowel = ch
    if vowel is None:
        return "G"
    if vowel in LONG_VOWELS:
        return "G"
    vowel_index = syllable.rfind(vowel)
    tail = syllable[vowel_index + len(vowel):]
    if tail:
        return "G"
    return "L"


def scan(text: str) -> ScansionResult:
    tokens = _tokenize_iast(text)
    sylls = _syllabify(tokens)
    syllables = [
        Syllable(text=s, weight=_weight(s), position=i + 1)
        for i, s in enumerate(sylls)
    ]
    pattern = "".join(s.weight for s in syllables)
    return ScansionResult(
        input=text,
        syllables=syllables,
        pattern=pattern,
        length=len(syllables),
        is_valid_anuṣṭubh=(len(syllables) == 32),
    )


if __name__ == "__main__":
    r = scan("rāma")
    assert r.length == 2 and r.pattern == "GL"
    r = scan("agni")
    assert r.length == 2 and r.pattern == "GL"
    r = scan("rāmaḥ")
    assert r.length == 2 and r.pattern == "GG"
    print("✓ scansion.py OK")
