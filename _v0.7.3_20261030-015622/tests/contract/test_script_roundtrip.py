"""
Transliteration Engine Generalization Test Suite
Tests character-wise Devanagari to IAST conversion and engine integration.
"""

import _script
import engine

def test_deva_to_iast_simple_word():
    assert _script.deva_to_iast("राम") == "rāma"

def test_deva_to_iast_with_visarga():
    assert _script.deva_to_iast("रामः") == "rāmaḥ"

def test_deva_to_iast_full_sentence():
    assert _script.deva_to_iast("रामो गच्छति") == "rāmo gacchati"

def test_engine_parse_devanagari_matches_iast():
    deva_doc = engine.parse("रामो गच्छति")
    iast_doc = engine.parse("rāmo gacchati")
    assert deva_doc is not None
    assert iast_doc is not None
    assert deva_doc["sandhi_splits"][0]["rule"] == iast_doc["sandhi_splits"][0]["rule"]

def test_deva_to_iast_already_curated_still_wins():
    assert _script.deva_to_iast("गायत्री") == "gāyatrī"