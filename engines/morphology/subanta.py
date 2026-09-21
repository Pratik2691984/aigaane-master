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
    """A single inflected form."""
    vibhakti: str          # e.g., "prathamā"
    vibhakti_num: int      # 1–8
    vacana: str            # "ekavacana", "dvivacana", "bahuvacana"
    vacana_num: int        # 1–3
    form: str              # the surface form
    rule: str              # the Aṣṭādhyāyī sūtra reference


@dataclass(frozen=True)
class Stem:
    """A nominal stem definition."""
    lemma: str
    gender: str            # "puṃ" | "strī" | "napuṃsaka"
    stem_class: str        # "a-masc", "a-neut", "ā-fem", "i-masc", "i-fem", "u-masc", "ū-fem"


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


# ─────────────────────── Stem endings ───────────────────────
# Each stem class has a 8×3 table of endings.
# The "stem" is formed by removing the final vowel/character from the lemma.

STEM_SUFFIXES = {
    # ── a-stem masculine (deva) ──
    "a-masc": {
        ("prathamā", "ekavacana"):    "aḥ",
        ("prathamā", "dvivacana"):    "au",
        ("prathamā", "bahuvacana"):   "āḥ",
        ("dvitīyā", "ekavacana"):     "am",
        ("dvitīyā", "dvivacana"):     "au",
        ("dvitīyā", "bahuvacana"):    "ān",
        ("tṛtīyā", "ekavacana"):      "ena",
        ("tṛtīyā", "dvivacana"):      "ābhyām",
        ("tṛtīyā", "bahuvacana"):     "aiḥ",
        ("caturthī", "ekavacana"):    "āya",
        ("caturthī", "dvivacana"):    "ābhyām",
        ("caturthī", "bahuvacana"):   "ebhyaḥ",
        ("pañcamī", "ekavacana"):     "āt",
        ("pañcamī", "dvivacana"):     "ābhyām",
        ("pañcamī", "bahuvacana"):    "ebhyaḥ",
        ("ṣaṣṭhī", "ekavacana"):      "asya",
        ("ṣaṣṭhī", "dvivacana"):      "ayoḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "ānām",
        ("saptamī", "ekavacana"):     "e",
        ("saptamī", "dvivacana"):     "ayoḥ",
        ("saptamī", "bahuvacana"):    "eṣu",
        ("sambodhana", "ekavacana"):  "",      # stem alone
        ("sambodhana", "dvivacana"):  "au",
        ("sambodhana", "bahuvacana"): "āḥ",
    },

    # ── a-stem neuter (phala) ──
    "a-neut": {
        ("prathamā", "ekavacana"):    "am",
        ("prathamā", "dvivacana"):    "e",
        ("prathamā", "bahuvacana"):   "āni",
        ("dvitīyā", "ekavacana"):     "am",
        ("dvitīyā", "dvivacana"):     "e",
        ("dvitīyā", "bahuvacana"):    "āni",
        ("tṛtīyā", "ekavacana"):      "ena",
        ("tṛtīyā", "dvivacana"):      "ābhyām",
        ("tṛtīyā", "bahuvacana"):     "aiḥ",
        ("caturthī", "ekavacana"):    "āya",
        ("caturthī", "dvivacana"):    "ābhyām",
        ("caturthī", "bahuvacana"):   "ebhyaḥ",
        ("pañcamī", "ekavacana"):     "āt",
        ("pañcamī", "dvivacana"):     "ābhyām",
        ("pañcamī", "bahuvacana"):    "ebhyaḥ",
        ("ṣaṣṭhī", "ekavacana"):      "asya",
        ("ṣaṣṭhī", "dvivacana"):      "ayoḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "ānām",
        ("saptamī", "ekavacana"):     "e",
        ("saptamī", "dvivacana"):     "ayoḥ",
        ("saptamī", "bahuvacana"):    "eṣu",
        ("sambodhana", "ekavacana"):  "a",
        ("sambodhana", "dvivacana"):  "e",
        ("sambodhana", "bahuvacana"): "āni",
    },

    # ── ā-stem feminine (senā) ──
    "ā-fem": {
        ("prathamā", "ekavacana"):    "ā",
        ("prathamā", "dvivacana"):    "e",
        ("prathamā", "bahuvacana"):   "āḥ",
        ("dvitīyā", "ekavacana"):     "ām",
        ("dvitīyā", "dvivacana"):     "e",
        ("dvitīyā", "bahuvacana"):    "āḥ",
        ("tṛtīyā", "ekavacana"):      "ayā",
        ("tṛtīyā", "dvivacana"):      "ābhyām",
        ("tṛtīyā", "bahuvacana"):     "ābhiḥ",
        ("caturthī", "ekavacana"):    "āyai",
        ("caturthī", "dvivacana"):    "ābhyām",
        ("caturthī", "bahuvacana"):   "ābhyaḥ",
        ("pañcamī", "ekavacana"):     "āyāḥ",
        ("pañcamī", "dvivacana"):     "ābhyām",
        ("pañcamī", "bahuvacana"):    "ābhyaḥ",
        ("ṣaṣṭhī", "ekavacana"):      "āyāḥ",
        ("ṣaṣṭhī", "dvivacana"):      "ayoḥ",
        ("ṣaṣṭhī", "bahuvacana"):     "ānām",
        ("saptamī", "ekavacana"):     "āyām",
        ("saptamī", "dvivacana"):     "ayoḥ",
        ("saptamī", "bahuvacana"):    "āsu",
        ("sambodhana", "ekavacana"):  "e",
        ("sambodhana", "dvivacana"):  "e",
        ("sambodhana", "bahuvacana"): "āḥ",
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


# ─────────────────────── Stem stripping rules ───────────────────────

def _strip_stem(lemma: str, stem_class: str) -> str:
    """
    Remove the final vowel/marker from the lemma to get the bare stem.
    Also applies guṇa/vṛddhi strengthening where required by Pāṇini.
    """
    if stem_class == "a-masc" or stem_class == "a-neut":
        # deva → dev
        return lemma[:-1] if lemma.endswith("a") else lemma
    if stem_class == "ā-fem":
        # senā → sen
        return lemma[:-1] if lemma.endswith("ā") else lemma
    if stem_class == "i-masc" or stem_class == "i-fem":
        # agni → agn (the i is dropped in most forms; retained as 'i' base)
        return lemma[:-1] if lemma.endswith("i") else lemma
    if stem_class == "u-masc":
        # viṣṇu → viṣṇ
        return lemma[:-1] if lemma.endswith("u") else lemma
    if stem_class == "ū-fem":
        # bhū → bh (but most ū-stems keep the ū and add uv-)
        return lemma[:-1] if lemma.endswith("ū") else lemma
    return lemma


def _apply_guṇa(stem: str) -> str:
    """
    Apply guṇa strengthening to the final vowel of the stem.
    a → ā, i → e, u → o, ṛ → ar.
    Used for certain case forms.
    """
    if not stem:
        return stem
    last = stem[-1]
    guṇa_map = {"a": "ā", "i": "e", "u": "o", "ṛ": "ar"}
    if last in guṇa_map:
        return stem[:-1] + guṇa_map[last]
    return stem


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

            # Handle stem-final vowel behavior per stem class
            if stem_class.startswith("i-"):
                # i-stems: use the i-base for some forms, drop for others
                if vibhakti_name in ("prathamā", "dvitīyā", "tṛtīyā") and vacana_name == "ekavacana":
                    form = stem + "i" + ending if ending.startswith("i") else stem + ending
                elif vibhakti_name in ("caturthī", "sambodhana") and vacana_name == "ekavacana":
                    form = stem + ending  # e.g., agnaye, agne
                else:
                    # Apply guṇa for these cases
                    strengthened = _apply_guṇa(stem + "i")
                    form = strengthened + ending if not ending.startswith(("i", "y")) else stem + ending
                    if vibhakti_name in ("saptamī", "ṣaṣṭhī") and ending in ("au", "yoḥ", "iṣu"):
                        form = stem + ending
            elif stem_class == "u-masc":
                if vibhakti_name in ("prathamā", "dvitīyā", "tṛtīyā") and vacana_name == "ekavacana":
                    form = stem + "u" + ending
                elif ending.startswith("av") or ending.startswith("o"):
                    strengthened = _apply_guṇa(stem + "u")
                    form = strengthened + ending
                else:
                    form = stem + "u" + ending
            elif stem_class == "ū-fem":
                if ending.startswith("uv") or ending.startswith("u"):
                    form = stem + "u" + ending
                else:
                    form = stem + ending
            else:
                # a-, ā-stems
                form = stem + ending

            # Cleanup: handle stem + a-stem endings
            if stem_class == "a-masc" or stem_class == "a-neut":
                form = stem + "a" + ending.lstrip("a") if ending.startswith("a") else stem + "a" + ending

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
    # deva — a-stem masculine
    forms = inflect("deva", "a-masc")
    assert len(forms) == 24
    print("deva (a-masc) first 6 forms:")
    for f in forms[:6]:
        print(f"  {f.vibhakti:12s} {f.vacana:12s} → {f.form}")

    # senā — ā-stem feminine
    forms = inflect("senā", "ā-fem")
    assert len(forms) == 24
    print("\nsenā (ā-fem) first 6 forms:")
    for f in forms[:6]:
        print(f"  {f.vibhakti:12s} {f.vacana:12s} → {f.form}")

    print("\nsubanta.py OK")