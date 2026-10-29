"""
Aigaane v0.3.0 — Generative Morphology Generalization Test Suite
Asserts that unseen tinanta and subanta inflected forms parse correctly.
"""

import _lexicon
import engine

def test_unseen_tinanta_plural_bhavanti():
    # "bhavanti" is NOT in golden corpus (corpus only has "bhavati")
    hit = _lexicon.lookup("bhavanti")
    assert hit is not None
    assert hit["pos"] == "tinanta"
    assert hit["dhatu"] == "bhū"
    assert hit["gana"] == 1
    assert hit["vibhakti"] == "na"
    assert hit["vacana"] == "bahuvacana"
    assert hit["linga"] == "na"

def test_unseen_tinanta_dual_gacchataḥ():
    # "gacchataḥ" (they two go) is NOT in golden corpus
    hit = _lexicon.lookup("gacchataḥ")
    assert hit is not None
    assert hit["pos"] == "tinanta"
    assert hit["dhatu"] == "gam"
    assert hit["gana"] == 1
    assert hit["vacana"] == "dvivacana"

def test_unseen_subanta_genitive_rāmasya():
    # "rāmasya" is NOT in golden corpus
    hit = _lexicon.lookup("rāmasya")
    assert hit is not None
    assert hit["pos"] == "subhanta"
    assert hit["stem"] == "rāma"
    assert hit["vibhakti"] == "shasthi"
    assert hit["vacana"] == "ekavacana"

def test_unseen_sentence_engine_parse():
    # Full unseen sentence: "rāmasya bhavati"
    doc = engine.parse("rāmasya bhavati")
    assert doc is not None
    assert len(doc["tokens"]) == 2
    tok0 = doc["tokens"][0]
    tok1 = doc["tokens"][1]
    assert tok0["stem"] == "rāma"
    assert tok0["vibhakti"] == "shasthi"
    assert tok1["pos"] == "tinanta"
    assert tok1["dhatu"] == "bhū"
    assert tok1["vibhakti"] == "na"
