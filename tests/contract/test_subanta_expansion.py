import pytest
from engine import parse

def test_subanta_lata_strilinga():
    res = parse("latā")
    assert res is not None
    token = res["tokens"][0]
    assert token["stem"] in ("latā", "lata")
    assert token["pos"] == "subhanta"
    assert token["linga"] == "strilinga"
    assert token["vibhakti"] == "prathama"
    assert token["vacana"] == "ekavacana"

def test_subanta_phalam_neuter():
    res = parse("phalam")
    assert res is not None
    token = res["tokens"][0]
    assert token["stem"] in ("phala", "phalam")
    assert token["pos"] == "subhanta"
    assert token["linga"] == "napumsakalinga"
    assert token["vacana"] == "ekavacana"

def test_sarvanama_tad_declension():
    for surface, expected_linga, exp_vibh, exp_vac in [
        ("saḥ", "pullinga", "prathama", "ekavacana"),
        ("sā", "strilinga", "prathama", "ekavacana"),
        ("tat", "napumsakalinga", "prathama", "ekavacana"),
        ("tam", "pullinga", "dvitiya", "ekavacana"),
        ("tena", "pullinga", "trtiya", "ekavacana"),
    ]:
        res = parse(surface)
        assert res is not None, f"Failed on {surface}"
        tok = res["tokens"][0]
        assert tok["stem"] == "tad", f"Expected stem 'tad' for surface '{surface}', got '{tok['stem']}'"
        assert tok["pos"] == "subhanta"
        assert tok["linga"] == expected_linga
        assert tok["vibhakti"] == exp_vibh
        assert tok["vacana"] == exp_vac

def test_sarvanama_asmad_yushmad():
    for surface, exp_stem, exp_vibh, exp_vac in [
        ("aham", "asmad", "prathama", "ekavacana"),
        ("mām", "asmad", "dvitiya", "ekavacana"),
        ("tvam", "yuṣmad", "prathama", "ekavacana"),
        ("tvayā", "yuṣmad", "trtiya", "ekavacana"),
    ]:
        res = parse(surface)
        assert res is not None, f"Failed on {surface}"
        tok = res["tokens"][0]
        assert tok["stem"] == exp_stem
        assert tok["pos"] == "subhanta"
        assert tok["vibhakti"] == exp_vibh
        assert tok["vacana"] == exp_vac
