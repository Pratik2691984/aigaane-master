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


# --- 5. Laṅ Paradigm for bhū (Parasmaipada, 9 forms) ---
BHU_LAN_PARADIGM = [
    ("abhavat",    "ekavacana"),
    ("abhavatām",  "dvivacana"),
    ("abhavan",    "bahuvacana"),
    ("abhavaḥ",    "ekavacana"),
    ("abhavatam",  "dvivacana"),
    ("abhavata",   "bahuvacana"),
    ("abhavam",    "ekavacana"),
    ("abhavāva",   "dvivacana"),
    ("abhavāma",   "bahuvacana"),
]

@pytest.mark.parametrize("surface, expected_vacana", BHU_LAN_PARADIGM)
def test_bhu_lan_exhaustive_paradigm(surface, expected_vacana):
    res = _lexicon.lookup(surface)
    assert res is not None, f"Failed lookup for bhū Laṅ form: {surface}"
    assert res["dhatu"] == "bhū"
    assert res["pos"] == "tinanta"
    assert res["vacana"] == expected_vacana


# --- 6. Laṅ Paradigm for labh (Ātmanepada, 9 forms) ---
LABH_LAN_PARADIGM = [
    ("alabhata",    "ekavacana"),
    ("alabhetām",   "dvivacana"),
    ("alabhanta",   "bahuvacana"),
    ("alabhathāḥ",  "ekavacana"),
    ("alabhethām",  "dvivacana"),
    ("alabhadhvam", "bahuvacana"),
    ("alabhe",      "ekavacana"),
    ("alabhāvahi",  "dvivacana"),
    ("alabhāmahi",  "bahuvacana"),
]

@pytest.mark.parametrize("surface, expected_vacana", LABH_LAN_PARADIGM)
def test_labh_lan_exhaustive_paradigm(surface, expected_vacana):
    res = _lexicon.lookup(surface)
    assert res is not None, f"Failed lookup for labh Laṅ form: {surface}"
    assert res["dhatu"] == "labh"
    assert res["pos"] == "tinanta"
    assert res["vacana"] == expected_vacana


# --- 7. Lṛṭ Paradigm for bhū (Parasmaipada, 9 forms) ---
BHU_LRT_PARADIGM = [
    ("bhaviṣyati",   "ekavacana"),
    ("bhaviṣyataḥ",  "dvivacana"),
    ("bhaviṣyanti",  "bahuvacana"),
    ("bhaviṣyasi",   "ekavacana"),
    ("bhaviṣyathaḥ", "dvivacana"),
    ("bhaviṣyatha",  "bahuvacana"),
    ("bhaviṣyāmi",   "ekavacana"),
    ("bhaviṣyāvaḥ",  "dvivacana"),
    ("bhaviṣyāmaḥ",  "bahuvacana"),
]

@pytest.mark.parametrize("surface, expected_vacana", BHU_LRT_PARADIGM)
def test_bhu_lrt_exhaustive_paradigm(surface, expected_vacana):
    res = _lexicon.lookup(surface)
    assert res is not None, f"Failed lookup for bhū Lṛṭ form: {surface}"
    assert res["dhatu"] == "bhū"
    assert res["pos"] == "tinanta"
    assert res["vacana"] == expected_vacana


# --- 8. Lṛṭ Paradigm for labh (Ātmanepada, 9 forms) ---
LABH_LRT_PARADIGM = [
    ("lapsyate",    "ekavacana"),
    ("lapsyete",    "dvivacana"),
    ("lapsyante",   "bahuvacana"),
    ("lapsyase",    "ekavacana"),
    ("lapsyethe",   "dvivacana"),
    ("lapsyadhve",  "bahuvacana"),
    ("lapsye",      "ekavacana"),
    ("lapsyāvahe",  "dvivacana"),
    ("lapsyāmahe",  "bahuvacana"),
]

@pytest.mark.parametrize("surface, expected_vacana", LABH_LRT_PARADIGM)
def test_labh_lrt_exhaustive_paradigm(surface, expected_vacana):
    res = _lexicon.lookup(surface)
    assert res is not None, f"Failed lookup for labh Lṛṭ form: {surface}"
    assert res["dhatu"] == "labh"
    assert res["pos"] == "tinanta"
    assert res["vacana"] == expected_vacana
