"""
engines/phonology/siksha.py
Śikṣā Articulation Tensor — Aṣṭādhyāyī 1.1.9, 1.1.50
"""

from typing import Dict, FrozenSet, NamedTuple, Optional, Tuple

STHANA_ORDER: Tuple[str, ...] = (
    "kaṇṭhya", "tālavya", "mūrdhanya", "dantya", "oṣṭhya",
    "dantoṣṭhya", "kaṇṭha-tālavya", "kaṇṭhoṣṭhya",
)
STHANA_INDEX: Dict[str, int] = {s: i for i, s in enumerate(STHANA_ORDER)}

ABHYANTARA_ORDER: Tuple[str, ...] = (
    "spṛṣṭa", "īṣat-spṛṣṭa", "īṣat-vivṛta", "vivṛta", "saṁvṛta",
)


class Phoneme(NamedTuple):
    symbol: str
    sthana: FrozenSet[str]
    abhyantara: str
    voiced: bool
    aspirated: bool
    nasal: bool
    is_vowel: bool
    is_short: bool


PHONEMES: Dict[str, Phoneme] = {
    # Vowels
    "a":  Phoneme("a",  frozenset({"kaṇṭhya"}),   "vivṛta", True, False, False, True, True),
    "ā":  Phoneme("ā",  frozenset({"kaṇṭhya"}),   "vivṛta", True, False, False, True, False),
    "i":  Phoneme("i",  frozenset({"tālavya"}),   "vivṛta", True, False, False, True, True),
    "ī":  Phoneme("ī",  frozenset({"tālavya"}),   "vivṛta", True, False, False, True, False),
    "u":  Phoneme("u",  frozenset({"oṣṭhya"}),    "vivṛta", True, False, False, True, True),
    "ū":  Phoneme("ū",  frozenset({"oṣṭhya"}),    "vivṛta", True, False, False, True, False),
    "ṛ":  Phoneme("ṛ",  frozenset({"mūrdhanya"}), "vivṛta", True, False, False, True, True),
    "ṝ":  Phoneme("ṝ",  frozenset({"mūrdhanya"}), "vivṛta", True, False, False, True, False),
    "ḷ":  Phoneme("ḷ",  frozenset({"dantya"}),    "vivṛta", True, False, False, True, True),
    "ḹ":  Phoneme("ḹ",  frozenset({"dantya"}),    "vivṛta", True, False, False, True, False),
    "e":  Phoneme("e",  frozenset({"kaṇṭhya", "tālavya"}),  "vivṛta", True, False, False, True, False),
    "ai": Phoneme("ai", frozenset({"kaṇṭhya", "tālavya"}),  "vivṛta", True, False, False, True, False),
    "o":  Phoneme("o",  frozenset({"kaṇṭhya", "oṣṭhya"}),   "vivṛta", True, False, False, True, False),
    "au": Phoneme("au", frozenset({"kaṇṭhya", "oṣṭhya"}),   "vivṛta", True, False, False, True, False),
    # Stops — velar
    "k":  Phoneme("k",  frozenset({"kaṇṭhya"}), "spṛṣṭa", False, False, False, False, False),
    "kh": Phoneme("kh", frozenset({"kaṇṭhya"}), "spṛṣṭa", False, True,  False, False, False),
    "g":  Phoneme("g",  frozenset({"kaṇṭhya"}), "spṛṣṭa", True,  False, False, False, False),
    "gh": Phoneme("gh", frozenset({"kaṇṭhya"}), "spṛṣṭa", True,  True,  False, False, False),
    "ṅ":  Phoneme("ṅ",  frozenset({"kaṇṭhya"}), "spṛṣṭa", True,  False, True,  False, False),
    # Palatal
    "c":  Phoneme("c",  frozenset({"tālavya"}), "spṛṣṭa", False, False, False, False, False),
    "ch": Phoneme("ch", frozenset({"tālavya"}), "spṛṣṭa", False, True,  False, False, False),
    "j":  Phoneme("j",  frozenset({"tālavya"}), "spṛṣṭa", True,  False, False, False, False),
    "jh": Phoneme("jh", frozenset({"tālavya"}), "spṛṣṭa", True,  True,  False, False, False),
    "ñ":  Phoneme("ñ",  frozenset({"tālavya"}), "spṛṣṭa", True,  False, True,  False, False),
    # Retroflex
    "ṭ":  Phoneme("ṭ",  frozenset({"mūrdhanya"}), "spṛṣṭa", False, False, False, False, False),
    "ṭh": Phoneme("ṭh", frozenset({"mūrdhanya"}), "spṛṣṭa", False, True,  False, False, False),
    "ḍ":  Phoneme("ḍ",  frozenset({"mūrdhanya"}), "spṛṣṭa", True,  False, False, False, False),
    "ḍh": Phoneme("ḍh", frozenset({"mūrdhanya"}), "spṛṣṭa", True,  True,  False, False, False),
    "ṇ":  Phoneme("ṇ",  frozenset({"mūrdhanya"}), "spṛṣṭa", True,  False, True,  False, False),
    # Dental
    "t":  Phoneme("t",  frozenset({"dantya"}), "spṛṣṭa", False, False, False, False, False),
    "th": Phoneme("th", frozenset({"dantya"}), "spṛṣṭa", False, True,  False, False, False),
    "d":  Phoneme("d",  frozenset({"dantya"}), "spṛṣṭa", True,  False, False, False, False),
    "dh": Phoneme("dh", frozenset({"dantya"}), "spṛṣṭa", True,  True,  False, False, False),
    "n":  Phoneme("n",  frozenset({"dantya"}), "spṛṣṭa", True,  False, True,  False, False),
    # Labial
    "p":  Phoneme("p",  frozenset({"oṣṭhya"}), "spṛṣṭa", False, False, False, False, False),
    "ph": Phoneme("ph", frozenset({"oṣṭhya"}), "spṛṣṭa", False, True,  False, False, False),
    "b":  Phoneme("b",  frozenset({"oṣṭhya"}), "spṛṣṭa", True,  False, False, False, False),
    "bh": Phoneme("bh", frozenset({"oṣṭhya"}), "spṛṣṭa", True,  True,  False, False, False),
    "m":  Phoneme("m",  frozenset({"oṣṭhya"}), "spṛṣṭa", True,  False, True,  False, False),
    # Semivowels
    "y":  Phoneme("y", frozenset({"tālavya"}),   "īṣat-spṛṣṭa", True, False, False, False, False),
    "r":  Phoneme("r", frozenset({"mūrdhanya"}), "īṣat-spṛṣṭa", True, False, False, False, False),
    "l":  Phoneme("l", frozenset({"dantya"}),    "īṣat-spṛṣṭa", True, False, False, False, False),
    "v":  Phoneme("v", frozenset({"dantoṣṭhya"}),"īṣat-spṛṣṭa", True, False, False, False, False),
    # Sibilants + h
    "ś":  Phoneme("ś", frozenset({"tālavya"}),   "īṣat-vivṛta", False, False, False, False, False),
    "ṣ":  Phoneme("ṣ", frozenset({"mūrdhanya"}), "īṣat-vivṛta", False, False, False, False, False),
    "s":  Phoneme("s", frozenset({"dantya"}),    "īṣat-vivṛta", False, False, False, False, False),
    "h":  Phoneme("h", frozenset({"kaṇṭhya"}),   "īṣat-vivṛta", True,  False, False, False, False),
    # Anusvāra / visarga
    "ṃ":  Phoneme("ṃ", frozenset({"oṣṭhya"}),  "spṛṣṭa", True, False, True,  False, False),
    "ṁ":  Phoneme("ṁ", frozenset({"oṣṭhya"}),  "spṛṣṭa", True, False, True,  False, False),
    "ḥ":  Phoneme("ḥ", frozenset({"kaṇṭhya"}), "īṣat-vivṛta", False, True, False, False, False),
}


class SikshaTensor:
    COORDINATES: Dict[str, Phoneme] = PHONEMES

    @classmethod
    def get(cls, phoneme: str) -> Optional[Phoneme]:
        if not phoneme:
            return None
        return cls.COORDINATES.get(phoneme.strip())

    @classmethod
    def are_savarṇa(cls, p1: str, p2: str) -> bool:
        c1, c2 = cls.get(p1), cls.get(p2)
        if c1 is None or c2 is None:
            return False
        # EXACT sthāna set match (not overlap) — per Kāśikā on 1.1.9
        if c1.sthana != c2.sthana:
            return False
        if c1.abhyantara != c2.abhyantara:
            return False
        if c1.is_vowel and c2.is_vowel:
            return True
        if c1.is_vowel != c2.is_vowel:
            return False
        return (c1.voiced == c2.voiced and
                c1.aspirated == c2.aspirated and
                c1.nasal == c2.nasal)

    @classmethod
    def phonetic_distance(cls, p1: str, p2: str) -> float:
        c1, c2 = cls.get(p1), cls.get(p2)
        if c1 is None or c2 is None:
            return float("inf")
        s1 = min(STHANA_INDEX[s] for s in c1.sthana)
        s2 = min(STHANA_INDEX[s] for s in c2.sthana)
        s_dist = abs(s1 - s2)
        a1 = ABHYANTARA_ORDER.index(c1.abhyantara)
        a2 = ABHYANTARA_ORDER.index(c2.abhyantara)
        return (4.0 * s_dist + 2.0 * abs(a1 - a2)
                + 1.0 * abs(int(c1.voiced) - int(c2.voiced))
                + 1.0 * abs(int(c1.aspirated) - int(c2.aspirated)))

    @classmethod
    def closest_match(cls, target: str, candidates):
        if not candidates:
            return None
        return min(candidates, key=lambda c: cls.phonetic_distance(target, c))


if __name__ == "__main__":
    S = SikshaTensor
    assert S.are_savarṇa("a", "ā")
    assert S.are_savarṇa("i", "ī")
    assert S.are_savarṇa("k", "kh") is False
    assert S.are_savarṇa("k", "g") is False
    assert S.are_savarṇa("t", "ṭ") is False
    assert S.closest_match("i", ["y", "v", "r", "l"]) == "y"
    assert S.closest_match("u", ["y", "v", "r", "l"]) == "v"
    print("✓ siksha.py OK")
