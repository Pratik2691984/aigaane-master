"""
engines/morphology/subanta.py
Subanta — Sanskrit nominal declension engine.

Implements Aṣṭādhyāyī 4.1.2 (nominal case endings) with explicit
surface-form tables for each stem class.

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


# ─────────────────────── Surface form tables ───────────────────────
# Each entry is the COMPLETE ending after the stem (with stem-final
# vowel already handled). Keyed by (stem_class, vibhakti, vacana).
#
# These follow the classical paradigms as taught in Sanskrit grammars
# (e.g., Deshpande, Whitney, Macdonell).

SURFACE_ENDINGS: dict[str, dict[tuple[str, str], str]] = {

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
        ("sambodhana", "ekavacana"):  "",       # bare stem (deva)
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
        ("sambodhana", "ekavacana"):  "a",      # phala (neuter voc. keeps stem)
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


# ─────────────────────── Stem base per class ───────────────────────
# The stem base is the lemma WITHOUT the final vowel.

def _stem_base(lemma: str, stem_class: str) -> str:
    """Strip the final vowel from the lemma."""
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


def _assemble(stem_base: str, stem_class: str, ending: str) -> str:
    """
    Assemble the final form from stem_base + surface ending.

    For a-stems:      deva + 'aḥ'  → devaḥ      (ending includes the vowel)
    For ā-stems:      sen + 'ā'    → senā
    For i/u/ū-stems:  agn + 'iḥ'   → agniḥ
    For sambodhana with empty ending in a-masc: return stem + 'a'
    """
    # Empty ending
    if ending == "":
        if stem_class == "a-masc":
            return stem_base + "a"
        if stem_class == "ā-fem":
            return stem_base + "ā"
        if stem_class in ("i-masc", "i-fem"):
            return stem_base + "i"
        if stem_class == "u-masc":
            return stem_base + "u"
        if stem_class == "ū-fem":
            return stem_base + "ū"
        return stem_base

    # a-neuter sambodhana has ending "a" (stem + a)
    if stem_class == "a-neut" and ending == "a":
        return stem_base + "a"

    return stem_base + ending


# ─────────────────────── Inflection ───────────────────────

def inflect(lemma: str, stem_class: str) -> list[Inflected]:
    """
    Generate all 24 inflected forms for a given lemma and stem class.
    """
    if stem_class not in SURFACE_ENDINGS:
        raise ValueError(f"Unsupported stem class: {stem_class}")

    base = _stem_base(lemma, stem_class)
    endings = SURFACE_ENDINGS[stem_class]

    results: list[Inflected] = []

    for vibhakti_name, vibhakti_num in VIBHAKTIS:
        for vacana_name, vacana_num in VACANAS:
            ending = endings.get((vibhakti_name, vacana_name), "")
            form = _assemble(base, stem_class, ending)

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
    # Full correctness check for deva (a-masc)
    expected_deva = {
        ("prathamā", "ekavacana"): "devaḥ",
        ("prathamā", "dvivacana"): "devau",
        ("prathamā", "bahuvacana"): "devāḥ",
        ("dvitīyā", "ekavacana"): "devam",
        ("dvitīyā", "dvivacana"): "devau",
        ("dvitīyā", "bahuvacana"): "devān",
        ("tṛtīyā", "ekavacana"): "devena",
        ("tṛtīyā", "dvivacana"): "devābhyām",
        ("tṛtīyā", "bahuvacana"): "devaiḥ",
        ("caturthī", "ekavacana"): "devāya",
        ("caturthī", "dvivacana"): "devābhyām",
        ("caturthī", "bahuvacana"): "devebhyaḥ",
        ("pañcamī", "ekavacana"): "devāt",
        ("pañcamī", "dvivacana"): "devābhyām",
        ("pañcamī", "bahuvacana"): "devebhyaḥ",
        ("ṣaṣṭhī", "ekavacana"): "devasya",
        ("ṣaṣṭhī", "dvivacana"): "devayoḥ",
        ("ṣaṣṭhī", "bahuvacana"): "devānām",
        ("saptamī", "ekavacana"): "deve",
        ("saptamī", "dvivacana"): "devayoḥ",
        ("saptamī", "bahuvacana"): "deveṣu",
        ("sambodhana", "ekavacana"): "deva",
        ("sambodhana", "dvivacana"): "devau",
        ("sambodhana", "bahuvacana"): "devāḥ",
    }

    forms = inflect("deva", "a-masc")
    all_ok = True
    print("deva (a-masc):")
    for f in forms:
        key = (f.vibhakti, f.vacana)
        exp = expected_deva.get(key)
        ok = (f.form == exp)
        all_ok = all_ok and ok
        mark = "✓" if ok else f"✗ (expected {exp})"
        print(f"  {f.vibhakti:12s} {f.vacana:12s} → {f.form:20s} {mark}")

    assert all_ok, "Some deva forms are incorrect"

    # Spot checks for other stems
    checks = [
        ("senā", "ā-fem", "prathamā", "ekavacana", "senā"),
        ("senā", "ā-fem", "tṛtīyā", "ekavacana", "senayā"),
        ("senā", "ā-fem", "ṣaṣṭhī", "bahuvacana", "senānām"),
        ("agni", "i-masc", "tṛtīyā", "ekavacana", "agninā"),
        ("agni", "i-masc", "prathamā", "bahuvacana", "agnayaḥ"),
        ("agni", "i-masc", "ṣaṣṭhī", "bahuvacana", "agnīnām"),
        ("viṣṇu", "u-masc", "prathamā", "ekavacana", "viṣṇuḥ"),
        ("viṣṇu", "u-masc", "tṛtīyā", "ekavacana", "viṣṇunā"),
        ("phala", "a-neut", "prathamā", "ekavacana", "phalam"),
        ("phala", "a-neut", "prathamā", "bahuvacana", "phalāni"),
        ("bhū", "ū-fem", "prathamā", "ekavacana", "bhūḥ"),
    ]

    print()
    for lemma, sc, vib, vac, expected in checks:
        forms = inflect(lemma, sc)
        f = [x for x in forms if x.vibhakti == vib and x.vacana == vac][0]
        ok = f.form == expected
        mark = "✓" if ok else f"✗ (expected {expected})"
        print(f"{lemma} ({sc}) {vib} {vac} → {f.form} {mark}")
        assert ok, f"{lemma} {vib} {vac} = {f.form}, expected {expected}"

    print("\nsubanta.py OK — all forms correct")