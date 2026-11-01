import pytest
from engine import parse

def test_sandhi_dag_tat_iti():
    doc = parse("taditi")
    assert doc is not None
    assert len(doc["tokens"]) == 2
    assert doc["tokens"][0]["pada"] == "tat"
    assert doc["tokens"][1]["pada"] == "iti"
    assert doc["sandhi_splits"][0]["rule"] == "jastva"
    assert "precedence_chain" in doc["sandhi_splits"][0]
    assert doc["sandhi_splits"][0]["precedence_chain"] == ["8.3.30", "6.1.125"]

def test_sandhi_dag_sad_iti():
    doc = parse("saditi")
    assert doc is not None
    assert len(doc["tokens"]) == 2
    assert doc["tokens"][0]["pada"] == "sat"
    assert doc["tokens"][1]["pada"] == "iti"
    assert doc["sandhi_splits"][0]["precedence_chain"] == ["8.3.30", "8.4.55"]
