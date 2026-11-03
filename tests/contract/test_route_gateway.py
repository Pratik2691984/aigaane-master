import pytest
from engine import parse, route

DEFAULT_POLICY = {
    "default_studio": "Studio_I",
    "routing_rules": [
        {"intent_class": "logical_argumentation", "forced_studio": "Studio_II", "rule_id": "R-NYAYA"},
        {"intent_class": "chhandas_meter_validation", "forced_studio": "Studio_III", "rule_id": "R-PROSODY"},
        {"intent_class": "scientific_verification", "forced_studio": "Studio_II", "rule_id": "R-SCI"}
    ],
    "nyaya_reasoning_wrapper": {
        "verifier_mode_by_studio": {
            "Studio_II": "deterministic"
        }
    }
}

def test_route_philology_default():
    doc = parse("rāmo gacchati")
    assert doc is not None
    decision = route(doc, DEFAULT_POLICY)
    assert decision["studio"] == "Studio_I"
    assert "classifier_confidence" in decision

def test_route_nyaya_argumentation():
    # Canonical Nyāya Category F input (F01)
    doc = parse("parvato vahnimān dhūmavattvāt")
    assert doc is not None
    decision = route(doc, DEFAULT_POLICY)
    assert decision["studio"] == "Studio_II"
    assert decision["intent_class"] == "logical_argumentation"
    assert decision.get("rule_id") == "R-NYAYA"
    assert "nyaya_syllogism" in decision or "nyaya_verifier_mode" in decision

def test_route_chhandas_prosody_anustubh():
    # Canonical Category G meter
    doc = parse("anuṣṭubh")
    assert doc is not None
    decision = route(doc, DEFAULT_POLICY)
    assert decision["studio"] == "Studio_III"
    assert decision["intent_class"] == "chhandas_meter_validation"
    assert decision.get("rule_id") == "R-PROSODY"

def test_route_chhandas_prosody_gayatri():
    # Golden Category G01
    doc = parse("gāyatrī")
    assert doc is not None
    decision = route(doc, DEFAULT_POLICY)
    assert decision["studio"] == "Studio_III"
    assert decision["intent_class"] == "chhandas_meter_validation"
    assert decision.get("rule_id") == "R-PROSODY"

def test_route_none_doc_resilience():
    # Resilience check against None input
    decision = route(None, DEFAULT_POLICY)
    assert decision["studio"] == "Studio_I"
