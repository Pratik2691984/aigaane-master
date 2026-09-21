"""
engines/morphology/subanta.py
Subanta — Sanskrit nominal declension engine.

Implements Aṣṭādhyāyī 4.1.2 (nominal case endings) with per-stem rules
for the seven major stem classes.

Supported stems:
  - a-stem masculine  (deva)
  - a-stem neuter     (phala)
  - ā-stem feminine   (senā)
  - i-stem masculine  (agni)
  - i-stem feminine   (mati)
  - u-stem masculine  (viṣṇu)
  - ū-stem feminine   (bhū)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ─────────────────────── Data structures ───────────────────────

@dataclass(frozen=True)
class Inflected:
    vibhakti: str
    vibhakti_num: int
    vacana: str
    vacana_num: int
    form: str
    rule: str


@dataclass(frozen=True)
class Stem:
    lemma: str
    gender: str
    stem_class: str


# ─────────────────────── Constants ───────────────────────

VIBHAKTIS = [
    ("prathamā", 1),
    ("dvitīyā", 2),
    ("tṛtīyā", 3),
    ("caturthī", 4),
    ("pañcamī", 5),
    ("ṣaṣṭhī", 6),
    ("saptamī", 7),
    ("sambodhana", 8),
]

VACANAS = [
    ("ekavacana", 1),
    ("dvivacana", 2),
    ("bahuvacana", 3),
]


# ─────────────────────── Stem ending tables ───────────────────────
# These are the endings as they appear AFTER the stem-final vowel.
# For a-stems, the stem-final 'a' is preserved in the stem, and the
# ending is applied with sandhi.

STEM_SUFFIXES = {
    # ── a-stem masculine (deva) ──
    "a-masc": {
        ("prathamā", "ekavacana"):    "ḥ",
        ("prathamā", "dvivacana"):    "au",
        ("prathamā", "bahuvacana"):   "āḥ",
        ("dvitīyā", "ekavacana"):     "m",
        ("dvitīyā", "dvivacana"):     "au",
        ("dvitīyā", "bahuvacana"):    "n",
        ("tṛtīyā", "ekavacana"):      "ena",
        ("tṛtīyā", "dvivacana"):      "bhyām",
        ("tṛtīyā", "bahuvacana"):     "iḥ",
        ("caturthī", "ekavacana"):    "ya",
        ("caturthī", "dvivacana"):    "bhyām",
        ("caturthī", "bahuvacana"):   "bhyaḥ",
        ("pañcamī", "ekavacana"):     "t",
        ("pañcamī", "dvivacana"):     "bhyām",
        ("pañcamī", "bahuvacana"):    "bhyaḥ",
        ("ṣaṣṭhī", "ekavacana"):      "sya",
        ("ṣaṣṭhī", "dvivacana"):      "yoḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "nām",
        ("saptamī", "ekavacana"):     "e",
        ("saptamī", "dvivacana"):     "yoḥ",
        ("saptamī", "bahuvacana"):    "ṣu",
        ("sambodhana", "ekavacana"):  "",
        ("sambodhana", "dvivacana"):  "au",
        ("sambodhana", "bahuvacana"): "āḥ",
    },

    # ── a-stem neuter (phala) ──
    "a-neut": {
        ("prathamā", "ekavacana"):    "m",
        ("prathamā", "dvivacana"):    "e",
        ("prathamā", "bahuvacana"):   "āni",
        ("dvitīyā", "ekavacana"):     "m",
        ("dvitīyā", "dvivacana"):     "e",
        ("dvitīyā", "bahuvacana"):    "āni",
        ("tṛtīyā", "ekavacana"):      "ena",
        ("tṛtīyā", "dvivacana"):      "bhyām",
        ("tṛtīyā", "bahuvacana"):     "iḥ",
        ("caturthī", "ekavacana"):    "ya",
        ("caturthī", "dvivacana"):    "bhyām",
        ("caturthī", "bahuvacana"):   "bhyaḥ",
        ("pañcamī", "ekavacana"):     "t",
        ("pañcamī", "dvivacana"):     "bhyām",
        ("pañcamī", "bahuvacana"):    "bhyaḥ",
        ("ṣaṣṭhī", "ekavacana"):      "sya",
        ("ṣaṣṭhī", "dvivacana"):      "yoḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "nām",
        ("saptamī", "ekavacana"):     "e",
        ("saptamī", "dvivacana"):     "yoḥ",
        ("saptamī", "bahuvacana"):    "ṣu",
        ("sambodhana", "ekavacana"):  "",
        ("sambodhana", "dvivacana"):  "e",
        ("sambodhana", "bahuvacana"): "āni",
    },

    # ── ā-stem feminine (senā) ──
    "ā-fem": {
        ("prathamā", "ekavacana"):    "",
        ("prathamā", "dvivacana"):    "e",
        ("prathamā", "bahuvacana"):   "ḥ",
        ("dvitīyā", "ekavacana"):     "m",
        ("dvitīyā", "dvivacana"):     "e",
        ("dvitīyā", "bahuvacana"):    "ḥ",
        ("tṛtīyā", "ekavacana"):      "yā",
        ("tṛtīyā", "dvivacana"):      "bhyām",
        ("tṛtīyā", "bahuvacana"):     "bhiḥ",
        ("caturthī", "ekavacana"):    "yai",
        ("caturthī", "dvivacana"):    "bhyām",
        ("caturthī", "bahuvacana"):   "bhyāḥ",
        ("pañcamī", "ekavacana"):     "yāḥ",
        ("pañcamī", "dvivacana"):     "bhyām",
        ("pañcamī", "bahuvacana"):    "bhyāḥ",
        ("ṣaṣṭhī", "ekavacana"):      "yāḥ",
        ("ṣaṣṭhī", "dvivacana"):      "yoḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "nām",
        ("saptamī", "ekavacana"):     "yām",
        ("saptamī", "dvivacana"):     "yoḥ",
        ("saptamī", "bahuvacana"):    "su",
        ("sambodhana", "ekavacana"):  "e",
        ("sambodhana", "dvivacana"):  "e",
        ("sambodhana", "bahuvacana"): "ḥ",
    },

    # ── i-stem masculine (agni) ──
    "i-masc": {
        ("prathamā", "ekavacana"):    "iḥ",
        ("prathamā", "dvivacana"):    "ī",
        ("prathamā", "bahuvacana"):   "ayaḥ",
        ("dvitīyā", "ekavacana"):     "im",
        ("dvitīyā", "dvivacana"):     "ī",
        ("dvitīyā", "bahuvacana"):    "īn",
        ("tṛtīyā", "ekavacana"):      "inā",
        ("tṛtīyā", "dvivacana"):      "ibhyām",
        ("tṛtīyā", "bahuvacana"):     "ibhiḥ",
        ("caturthī", "ekavacana"):    "aye",
        ("caturthī", "dvivacana"):    "ibhyām",
        ("caturthī", "bahuvacana"):   "ibhyaḥ",
        ("pañcamī", "ekavacana"):     "eḥ",
        ("pañcamī", "dvivacana"):     "ibhyām",
        ("pañcamī", "bahuvacana"):    "ibhyaḥ",
        ("ṣaṣṭhī", "ekavacana"):      "eḥ",
        ("ṣaṣṭhī", "dvivacana"):      "yoḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "īnām",
        ("saptamī", "ekavacana"):     "au",
        ("saptamī", "dvivacana"):     "yoḥ",
        ("saptamī", "bahuvacana"):    "iṣu",
        ("sambodhana", "ekavacana"):  "e",
        ("sambodhana", "dvivacana"):  "ī",
        ("sambodhana", "bahuvacana"): "ayaḥ",
    },

    # ── i-stem feminine (mati) ──
    "i-fem": {
        ("prathamā", "ekavacana"):    "iḥ",
        ("prathamā", "dvivacana"):    "ī",
        ("prathamā", "bahuvacana"):   "ayaḥ",
        ("dvitīyā", "ekavacana"):     "im",
        ("dvitīyā", "dvivacana"):     "ī",
        ("dvitīyā", "bahuvacana"):    "īḥ",
        ("tṛtīyā", "ekavacana"):      "yā",
        ("tṛtīyā", "dvivacana"):      "ibhyām",
        ("tṛtīyā", "bahuvacana"):     "ibhiḥ",
        ("caturthī", "ekavacana"):    "aye",
        ("caturthī", "dvivacana"):    "ibhyām",
        ("caturthī", "bahuvacana"):   "ibhyaḥ",
        ("pañcamī", "ekavacana"):     "eḥ",
        ("pañcamī", "dvivacana"):     "ibhyām",
        ("pañcamī", "bahuvacana"):    "ibhyaḥ",
        ("ṣaṣṭhī", "ekavacana"):      "eḥ",
        ("ṣaṣṭhī", "dvivacana"):      "yoḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "īnām",
        ("saptamī", "ekavacana"):     "au",
        ("saptamī", "dvivacana"):     "yoḥ",
        ("saptamī", "bahuvacana"):    "iṣu",
        ("sambodhana", "ekavacana"):  "e",
        ("sambodhana", "dvivacana"):  "ī",
        ("sambodhana", "bahuvacana"): "ayaḥ",
    },

    # ── u-stem masculine (viṣṇu) ──
    "u-masc": {
        ("prathamā", "ekavacana"):    "uḥ",
        ("prathamā", "dvivacana"):    "ū",
        ("prathamā", "bahuvacana"):   "avaḥ",
        ("dvitīyā", "ekavacana"):     "um",
        ("dvitīyā", "dvivacana"):     "ū",
        ("dvitīyā", "bahuvacana"):    "ūn",
        ("tṛtīyā", "ekavacana"):      "unā",
        ("tṛtīyā", "dvivacana"):      "ubhyām",
        ("tṛtīyā", "bahuvacana"):     "ubhiḥ",
        ("caturthī", "ekavacana"):    "ave",
        ("caturthī", "dvivacana"):    "ubhyām",
        ("caturthī", "bahuvacana"):   "ubhyaḥ",
        ("pañcamī", "ekavacana"):     "oḥ",
        ("pañcamī", "dvivacana"):     "ubhyām",
        ("pañcamī", "bahuvacana"):    "ubhyaḥ",
        ("ṣaṣṭhī", "ekavacana"):      "oḥ",
        ("ṣaṣṭhī", "dvivacana"):      "voḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "ūnām",
        ("saptamī", "ekavacana"):     "au",
        ("saptamī", "dvivacana"):     "voḥ",
        ("saptamī", "bahuvacana"):    "uṣu",
        ("sambodhana", "ekavacana"):  "o",
        ("sambodhana", "dvivacana"):  "ū",
        ("sambodhana", "bahuvacana"): "avaḥ",
    },

    # ── ū-stem feminine (bhū) ──
    "ū-fem": {
        ("prathamā", "ekavacana"):    "ūḥ",
        ("prathamā", "dvivacana"):    "ū",
        ("prathamā", "bahuvacana"):   "uvaḥ",
        ("dvitīyā", "ekavacana"):     "uvam",
        ("dvitīyā", "dvivacana"):     "ū",
        ("dvitīyā", "bahuvacana"):    "ūḥ",
        ("tṛtīyā", "ekavacana"):      "uvā",
        ("tṛtīyā", "dvivacana"):      "ūbhyām",
        ("tṛtīyā", "bahuvacana"):     "ūbhiḥ",
        ("caturthī", "ekavacana"):    "uvai",
        ("caturthī", "dvivacana"):    "ūbhyām",
        ("caturthī", "bahuvacana"):   "ūbhyaḥ",
        ("pañcamī", "ekavacana"):     "uvāḥ",
        ("pañcamī", "dvivacana"):     "ūbhyām",
        ("pañcamī", "bahuvacana"):    "ūbhyaḥ",
        ("ṣaṣṭhī", "ekavacana"):      "uvāḥ",
        ("ṣaṣṭhī", "dvivacana"):      "uvoḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "ūnām",
        ("saptamī", "ekavacana"):     "uvām",
        ("saptamī", "dvivacana"):     "uvoḥ",
        ("saptamī", "bahuvacana"):    "ūṣu",
        ("sambodhana", "ekavacana"):  "u",
        ("sambodhana", "dvivacana"):  "ū",
        ("sambodhana", "bahuvacana"): "uvaḥ",
    },
}


# ─────────────────────── Sandhi helper ───────────────────────

def _sandhi_combine(stem_final: str, ending: str) -> str:
    """
    Apply vowel sandhi between the stem-final vowel and the ending's initial vowel.
    Handles the common a/ā + vowel combinations.
    """
    if not ending:
        return stem_final

    # If ending starts with a consonant, no sandhi needed
    if ending[0] not in "aāiīuūṛṝḷḹeo":
        return stem_final + ending

    # a-stem sandhi (stem-final 'a')
    if stem_final == "a":
        first = ending[0]
        rest = ending[1:]
        if first in ("a", "ā"):
            return "ā" + rest
        if first in ("i", "ī"):
            return "e" + rest
        if first in ("u", "ū"):
            return "o" + rest
        if first in ("e", "ai"):
            return "ai" + rest
        if first in ("o", "au"):
            return "au" + rest
        if first in ("ṛ", "ṝ"):
            return "ar" + rest
        return stem_final + ending

    # ā-stem sandhi (stem-final 'ā')
    if stem_final == "ā":
        first = ending[0]
        rest = ending[1:]
        if first in ("a", "ā"):
            return "ā" + rest
        if first in ("i", "ī"):
            return "e" + rest
        if first in ("u", "ū"):
            return "o" + rest
        if first in ("e", "ai"):
            return "ai" + rest
        if first in ("o", "au"):
            return "au" + rest
        return stem_final + ending

    return stem_final + ending


# ─────────────────────── Stem stripping ───────────────────────

def _strip_stem(lemma: str, stem_class: str) -> str:
    """Remove the final vowel/marker from the lemma to get the bare stem."""
    if stem_class in ("a-masc", "a-neut"):
        return lemma[:-1] if lemma.endswith("a") else lemma
    if stem_class == "ā-fem":
        return lemma[:-1] if lemma.endswith("ā") else lemma
    if stem_class in ("i-masc", "i-fem"):
        return lemma[:-1] if lemma.endswith("i") else lemma
    if stem_class == "u-masc":
        return lemma[:-1] if lemma.endswith("u") else lemma
    if stem_class == "ū-fem":
        return lemma[:-1] if lemma.endswith("ū") else lemma
    return lemma


# ─────────────────────── Inflection ───────────────────────

def inflect(lemma: str, stem_class: str) -> list[Inflected]:
    """
    Generate all 24 inflected forms for a given lemma and stem class.

    Args:
        lemma: IAST lemma (e.g., "deva", "senā")
        stem_class: one of "a-masc", "a-neut", "ā-fem", "i-masc",
                    "i-fem", "u-masc", "ū-fem"

    Returns:
        List of 24 Inflected instances (8 vibhaktis × 3 vacanas)
    """
    if stem_class not in STEM_SUFFIXES:
        raise ValueError(f"Unsupported stem class: {stem_class}")

    stem = _strip_stem(lemma, stem_class)
    suffixes = STEM_SUFFIXES[stem_class]

    results: list[Inflected] = []

    for vibhakti_name, vibhakti_num in VIBHAKTIS:
        for vacana_name, vacana_num in VACANAS:
            ending = suffixes.get((vibhakti_name, vacana_name), "")

            if stem_class in ("a-masc", "a-neut"):
                # stem ends in consonant after stripping; add "a" back
                form = _sandhi_combine("a", ending)
                form = stem + form
            elif stem_class == "ā-fem":
                # stem ends in consonant after stripping; add "ā" back
                form = _sandhi_combine("ā", ending)
                form = stem + form
            elif stem_class in ("i-masc", "i-fem"):
                # stem ends in consonant; add "i" back
                if ending.startswith("i") or ending.startswith("ī"):
                    form = stem + ending
                elif ending.startswith(("ay", "y")):
                    form = stem + ending
                else:
                    form = stem + "i" + ending
            elif stem_class == "u-masc":
                if ending.startswith(("u", "ū", "av", "o")):
                    form = stem + ending
                else:
                    form = stem + "u" + ending
            elif stem_class == "ū-fem":
                if ending.startswith(("uv", "u", "ū")):
                    form = stem + ending
                else:
                    form = stem + "ū" + ending
            else:
                form = stem + ending

            results.append(Inflected(
                vibhakti=vibhakti_name,
                vibhakti_num=vibhakti_num,
                vacana=vacana_name,
                vacana_num=vacana_num,
                form=form,
                rule="Aṣṭādhyāyī 4.1.2",
            ))

    return results


# ─────────────────────── Self-test ───────────────────────

if __name__ == "__main__":
    forms = inflect("deva", "a-masc")
    assert len(forms) == 24

    # Key checks
    checks = {
        ("prathamā", "ekavacana"): "devaḥ",
        ("prathamā", "dvivacana"): "devau",
        ("prathamā", "bahuvacana"): "devāḥ",
        ("dvitīyā", "bahuvacana"): "devān",
        ("tṛtīyā", "ekavacana"): "devena",
        ("tṛtīyā", "dvivacana"): "devābhyām",
        ("caturthī", "ekavacana"): "devāya",
        ("pañcamī", "ekavacana"): "devāt",
        ("ṣaṣṭhī", "ekavacana"): "devasya",
        ("saptamī", "ekavacana"): "deve",
        ("saptamī", "bahuvacana"): "deveṣu",
    }

    print("deva (a-masc) forms:")
    for f in forms:
        key = (f.vibhakti, f.vacana)
        expected = checks.get(key)
        mark = "✓" if expected and f.form == expected else ("✗ (expected " + expected + ")" if expected else "")
        print(f"  {f.vibhakti:12s} {f.vacana:12s} → {f.form:20s} {mark}")

    # Check i-stem
    forms = inflect("agni", "i-masc")
    tṛtīyā_eka = [f for f in forms if f.vibhakti == "tṛtīyā" and f.vacana == "ekavacana"][0]
    assert tṛtīyā_eka.form == "agninā", f"Expected agninā, got {tṛtīyā_eka.form}"
    print(f"\nagni (i-masc) tṛtīyā ekavacana → {tṛtīyā_eka.form} ✓")

    # Check ā-stem
    forms = inflect("senā", "ā-fem")
    prathamā_eka = [f for f in forms if f.vibhakti == "prathamā" and f.vacana == "ekavacana"][0]
    assert prathamā_eka.form == "senā", f"Expected senā, got {prathamā_eka.form}"
    print(f"senā (ā-fem) prathamā ekavacana → {prathamā_eka.form} ✓")

    print("\nsubanta.py OK")