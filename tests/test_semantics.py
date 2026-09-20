"""
tests/test_semantics.py
Unit test for semantic field profiles and context loader schema validation.
"""
import pytest
from pathlib import Path
import json
from engine.semantics.schema import SemanticFieldProfile

def test_prajna_profile_validation():
    fixture_path = Path("data/sanskrit/semantics/prajna_field.json")
    assert fixture_path.exists(), "Prajñā semantic profile fixture must exist."
    
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    profile = SemanticFieldProfile(**data)
    
    assert profile.lemma == "प्रज्ञा"
    assert len(profile.edges) >= 5
    
    synonyms = [e.target for e in profile.edges if e.relation == "synonym"]
    assert "विद्या" in synonyms
    assert "धी" in synonyms

def test_load_semantic_context_loader():
    from scripts.generate_verse import load_semantic_context
    ctx = load_semantic_context("प्रज्ञा")
    assert "SEMANTIC VOCABULARY CONSTRAINTS" in ctx
    assert "विद्या" in ctx
