import pytest
from engine import parse

@pytest.mark.parametrize("verb,expected_dhatu,expected_gana", [
    ("gacchati", "gam", 1),
    ("asti", "as", 2),
    ("santi", "as", 2),
    ("dadhāti", "dhā", 3),
    ("jāyate", "jan", 4),
    ("śṛṇoti", "śru", 5),
    ("icchati", "iṣ", 6),
    ("karoti", "kṛ", 8),
    ("jānāti", "jñā", 9),
    ("cintayati", "cint", 10),
])
def test_classical_dhatu_coverage(verb, expected_dhatu, expected_gana):
    doc = parse(verb)
    assert doc is not None
    assert doc["schema_version"] == "0.2.0"
    assert len(doc["tokens"]) == 1
    t = doc["tokens"][0]
    assert t["pos"] == "tinanta"
    assert t["dhatu"] == expected_dhatu
    assert t["gana"] == expected_gana
    assert doc["confidence"] >= 0.95
