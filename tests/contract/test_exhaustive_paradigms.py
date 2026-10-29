import pytest
import _lexicon

# --- 1. Laṭ Paradigm for bhū (Parasmaipada, 9 forms) ---
BHU_LAT_PARADIGM = [
    ("bhavati",   "ekavacana"),
    ("bhavataḥ",  "dvivacana"),
    ("bhavanti",  "bahuvacana"),
    ("bhavasi",   "ekavacana"),
    ("bhavathaḥ", "dvivacana"),
    ("bhavatha",  "bahuvacana"),
    ("bhavāmi",   "ekavacana"),
    ("bhavāvaḥ",  "dvivacana"),
    ("bhavāmaḥ",  "bahuvacana"),
]

@pytest.mark.parametrize("surface, expected_vacana", BHU_LAT_PARADIGM)
def test_bhu_lat_exhaustive_paradigm(surface, expected_vacana):
    res = _lexicon.lookup(surface)
    assert res is not None, f"Failed lookup for bhū Laṭ form: {surface}"
    assert res["dhatu"] == "bhū"
    assert res["pos"] == "tinanta"
    assert res["vacana"] == expected_vacana


# --- 2. Laṭ Paradigm for labh (Ātmanepada, 9 forms) ---
LABH_LAT_PARADIGM = [
    ("labhate",   "ekavacana"),
    ("labhete",   "dvivacana"),
    ("labhante",  "bahuvacana"),
    ("labhase",   "ekavacana"),
    ("labhethe",  "dvivacana"),
    ("labhadhve", "bahuvacana"),
    ("labhe",     "ekavacana"),
    ("labhāvahe", "dvivacana"),
    ("labhāmahe", "bahuvacana"),
]

@pytest.mark.parametrize("surface, expected_vacana", LABH_LAT_PARADIGM)
def test_labh_lat_exhaustive_paradigm(surface, expected_vacana):
    res = _lexicon.lookup(surface)
    assert res is not None, f"Failed lookup for labh Laṭ form: {surface}"
    assert res["dhatu"] == "labh"
    assert res["pos"] == "tinanta"
    assert res["vacana"] == expected_vacana


# --- 3. Liṭ Paradigm for bhū (Parasmaipada, 9 forms) ---
BHU_LIT_PARADIGM = [
    ("babhūva",     "ekavacana"),
    ("babhūvatuḥ",  "dvivacana"),
    ("babhūvuḥ",    "bahuvacana"),
    ("babhūvitha",  "ekavacana"),
    ("babhūvathuḥ", "dvivacana"),
    ("babhūviva",   "dvivacana"),
    ("babhūvima",   "bahuvacana"),
]

@pytest.mark.parametrize("surface, expected_vacana", BHU_LIT_PARADIGM)
def test_bhu_lit_exhaustive_paradigm(surface, expected_vacana):
    res = _lexicon.lookup(surface)
    assert res is not None, f"Failed lookup for bhū Liṭ form: {surface}"
    assert res["dhatu"] == "bhū"
    assert res["pos"] == "tinanta"
    assert res["vacana"] == expected_vacana


# --- 4. Liṭ Paradigm for labh (Ātmanepada, 9 forms) ---
LABH_LIT_PARADIGM = [
    ("lebhe",      "ekavacana"),
    ("lebhāte",    "dvivacana"),
    ("lebhire",    "bahuvacana"),
    ("lebhiṣe",    "ekavacana"),
    ("lebhāthe",   "dvivacana"),
    ("lebhidhve",  "bahuvacana"),
    ("lebhivahe",  "dvivacana"),
    ("lebhimahe",  "bahuvacana"),
]

@pytest.mark.parametrize("surface, expected_vacana", LABH_LIT_PARADIGM)
def test_labh_lit_exhaustive_paradigm(surface, expected_vacana):
    res = _lexicon.lookup(surface)
    assert res is not None, f"Failed lookup for labh Liṭ form: {surface}"
    assert res["dhatu"] == "labh"
    assert res["pos"] == "tinanta"
    assert res["vacana"] == expected_vacana
