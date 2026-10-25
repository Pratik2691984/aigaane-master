"""
Aigaane v0.3.0 — Generative Sandhi Generalization Test Suite
Tests unseen inputs that do not exist in golden_corpus_manifest.json.
"""

import _sandhi

def test_unseen_savarna_dirgha_generative():
    # "mahālayaḥ" is NOT in the golden corpus
    # Should resolve to ["maha", "alayaḥ"] via rule 6.1.101
    res = _sandhi.split_surface("mahālayaḥ")
    assert res is not None
    parts, rule, ref, conf = res
    assert parts == ["maha", "alayaḥ"]
    assert rule == "savarna_dirgha"
    assert ref == "6.1.101"

def test_unseen_visarga_o_generative():
    # "devo gacchati" is NOT in the golden corpus (corpus only has "rāmo gacchati")
    res = _sandhi.split_surface("devo gacchati")
    assert res is not None
    parts, rule, ref, conf = res
    assert parts == ["devaḥ", "gacchati"]
    assert rule == "visarga_o"
    assert ref == "8.2.66"

def test_unseen_scutva_generative():
    # "rājaputracca" is NOT in the golden corpus
    res = _sandhi.split_surface("rājaputracca")
    assert res is not None
    parts, rule, ref, conf = res
    assert parts == ["rājaputrat", "ca"]
    assert rule == "ścutva"
