"""
Aigaane v0.3.0 — Generative Samasa Compound Generalization Test Suite
Tests compound parsing on novel compounds not present in golden_corpus_manifest.json.
"""

import _samasa
import engine

def test_unseen_compound_devaputra():
    # "devaputraḥ" is NOT in golden corpus (only "rājaputraḥ" is)
    tree = _samasa.build_tree("devaputraḥ")
    assert tree is not None
    assert tree["type"] == "tatpurusha"
    assert tree["role"] == "single"
    assert len(tree["children"]) == 2
    assert tree["children"][0]["component_surface"] == "deva"
    assert tree["children"][0]["role"] == "purva_pada"

def test_unseen_compound_engine_parse_and_schema():
    # Verify end-to-end parse and schema compliance on an unseen compound
    doc = engine.parse("devaputraḥ")
    assert doc is not None
    assert "samasa_tree" in doc
    assert doc["samasa_tree"]["type"] == "tatpurusha"
    assert doc["tokens"][0]["pada"] == "devaputraḥ"
