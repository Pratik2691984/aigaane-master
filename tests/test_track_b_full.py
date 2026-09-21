"""
tests/test_track_b_full.py
Consolidated integration tests for Track B modules.
"""

import pytest
from fastapi.testclient import TestClient

from engines.phonology.pratyahara import PratyaharaEngine
from engines.phonology.siksha import SikshaTensor
from engines.phonology.sandhi import SandhiEngine
from engines.chandas.scansion import scan
from engines.chandas.anustubh import validate_anustubh

from api.kernel_api import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_pratyahara_ac():
    pe = PratyaharaEngine()
    assert pe.generate("ac") == frozenset(
        {"a", "i", "u", "ṛ", "ḷ", "e", "o", "ai", "au"}
    )

def test_pratyahara_yan():
    pe = PratyaharaEngine()
    assert pe.generate("yaṇ") == frozenset({"y", "v", "r", "l"})

def test_pratyahara_lan():
    pe = PratyaharaEngine()
    assert pe.generate("laṇ") == frozenset({"l"})


def test_siksha_vowel_savarna():
    S = SikshaTensor
    assert S.are_savarṇa("a", "ā")
    assert S.are_savarṇa("i", "ī")

def test_siksha_consonant_not_savarna():
    S = SikshaTensor
    assert not S.are_savarṇa("k", "kh")
    assert not S.are_savarṇa("t", "ṭ")

def test_siksha_closest_match():
    S = SikshaTensor
    assert S.closest_match("i", ["y", "v", "r", "l"]) == "y"
    assert S.closest_match("u", ["y", "v", "r", "l"]) == "v"


def test_sandhi_savarna_dirgha():
    s = SandhiEngine()
    assert s.combine_svara("a", "a") == "ā"

def test_sandhi_guna():
    s = SandhiEngine()
    assert s.combine_svara("a", "i") == "e"
    assert s.combine_svara("a", "u") == "o"

def test_sandhi_vrddhi():
    s = SandhiEngine()
    assert s.combine_svara("a", "e") == "ai"
    assert s.combine_svara("a", "o") == "au"

def test_sandhi_yan():
    s = SandhiEngine()
    assert s.combine_svara("i", "a") == "ya"

def test_sandhi_hal_scutva():
    s = SandhiEngine()
    assert s.combine_hal("t", "c") == "c"

def test_sandhi_hal_stutva():
    s = SandhiEngine()
    assert s.combine_hal("t", "ṭ") == "ṭ"

def test_sandhi_visarga_109():
    s = SandhiEngine()
    # 6.1.109 fires when following phoneme is short 'a'
    assert s.combine_visarga_with_context("aḥ", "a") == ("o'", "6.1.109")
    assert s.combine_visarga_with_context("aḥ", "agni") == ("o'", "6.1.109")

def test_sandhi_visarga_114():
    s = SandhiEngine()
    # 6.1.114 fires when following phoneme is haś (voiced) but not 'a'
    assert s.combine_visarga_with_context("aḥ", "iti") == ("o", "6.1.114")
    assert s.combine_visarga_with_context("aḥ", "gacchati") == ("o", "6.1.114")


def test_scan_simple():
    r = scan("rāma")
    assert r.length == 2 and r.pattern == "GL"

def test_scan_visarga():
    r = scan("rāmaḥ")
    assert r.pattern == "GG"

def test_scan_conjunct():
    r = scan("agni")
    assert r.pattern == "GL"

def test_anustubh_short():
    r = validate_anustubh("rāma")
    assert not r.is_valid
    assert "32" in r.errors[0]


@pytest.mark.parametrize("p1,p2,result,sutra", [
    ("a", "a", "ā",  "6.1.101"),
    ("a", "i", "e",  "6.1.87"),
    ("a", "e", "ai", "6.1.88"),
    ("i", "a", "ya", "6.1.77"),
    ("t", "c", "c",  "8.4.40"),
    ("t", "ṭ", "ṭ",  "8.4.41"),
])
def test_router_sandhi(client, p1, p2, result, sutra):
    r = client.post("/api/v3/sandhi", json={"p1": p1, "p2": p2})
    assert r.status_code == 200
    body = r.json()
    assert body["result"] == result
    assert body["rule_applied"] == sutra


def test_router_sandhi_visarga(client):
    # 6.1.109: following vowel must be short 'a'
    r = client.post("/api/v3/sandhi", json={"p1": "aḥ", "p2": "a"})
    assert r.status_code == 200
    assert r.json()["result"] == "o'"


def test_router_scan(client):
    r = client.post("/api/v3/chandas/scan", json={"text": "rāma"})
    assert r.status_code == 200
    body = r.json()
    assert body["length"] == 2
    assert body["pattern"] == "GL"


def test_router_anustubh_short(client):
    r = client.post("/api/v3/chandas/anustubh", json={"text": "rāma"})
    assert r.status_code == 200
    body = r.json()
    assert body["is_valid"] is False