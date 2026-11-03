import pytest
from engine import parse
import _neural_fallback

def test_neural_fallback_schema_compliance():
    # Synthetic out-of-vocabulary form
    doc = parse("xyzunknownsanskritpada")
    assert doc is not None
    assert doc["schema_version"] == "0.2.0"
    assert "tokens" in doc
    assert len(doc["tokens"]) >= 1
    tok = doc["tokens"][0]
    assert "stem" in tok
    assert "pos" in tok
    assert "confidence" in tok
    assert doc["confidence"] <= 0.75
    assert any("fallback" in p for p in doc["provenance"])

def test_is_llm_available_boolean():
    res = _neural_fallback.is_llm_available()
    assert isinstance(res, bool)
