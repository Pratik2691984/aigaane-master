"""
Unit verification for Ambiguity Candidate Scoring & Ranking Engine.
"""

import _ambiguity
import engine

def test_naresha_primary_and_alternate_ranking():
    res = _ambiguity.resolve_ranked("nareśaḥ")
    assert res is not None
    assert res["ambiguity_type"] == "sandhi_split"
    parts, rule, canon, conf = res["primary"]
    assert parts == ["nara", "īśaḥ"]
    assert rule == "guna"
    assert len(res["alternates"]) >= 1
    alt_parts, amb_type, alt_conf = res["alternates"][0]
    assert alt_parts == ["na", "reśaḥ"]
    assert conf > alt_conf

def test_all_category_b_primary_preservation():
    surfaces = [
        "nareśaḥ", "sarveśvaraḥ", "maharṣiḥ", "seti", "so 'yaṃ",
        "te 'pi", "tadapi", "ityatra", "hariḥ", "guruḥ",
        "rāmaḥ", "somaḥ", "agniḥ", "rājaputraḥ", "kṛṣṇaḥ"
    ]
    for s in surfaces:
        ranked = _ambiguity.resolve_ranked(s)
        assert ranked is not None, f"Surface {s} failed resolution"
        assert len(ranked["primary"][0]) >= 1
        assert ranked["primary"][3] >= 0.35

def test_unknown_surface_returns_none():
    assert _ambiguity.resolve_ranked("completely_unknown_token_xyz") is None

def test_score_candidate_lexical_advantage():
    known_parts = ["nara", "īśaḥ"]
    unknown_parts = ["na", "reśaḥ"]
    score_known = _ambiguity._score_candidate(known_parts, "guna", "6.1.87", 0.90)
    score_unknown = _ambiguity._score_candidate(unknown_parts, "unknown", "na", 0.20)
    assert score_known > score_unknown

def test_engine_parse_emits_ranked_ambiguous_parses():
    doc = engine.parse("nareśaḥ")
    assert doc is not None
    assert "ambiguous_parses" in doc
    assert len(doc["ambiguous_parses"]) >= 1
    for i, alt in enumerate(doc["ambiguous_parses"]):
        assert alt["parse_rank"] == i + 2