import engine
"""
Test suite for _sandhi_gen.py (Standalone Paninian Sandhi Inverter)
Verifies Savarna-dirgha, Guna, Yan, Scutva, Visarga, and Purvarupa inversions
alongside determinism, diagnostics, rank-1 alignment, and deferral safety fences.
"""

import json
from pathlib import Path
import pytest
import _sandhi_gen

# 1. Savarna-Dirgha Inversion
def test_savarna_dirgha_a():
    cands, reason = _sandhi_gen.invert_sandhi("himālayaḥ")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["hima", "ālayaḥ"] in splits
    assert cands[0][1] == "savarna_dirgha"

def test_savarna_dirgha_i():
    cands, reason = _sandhi_gen.invert_sandhi("kavīndraḥ")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["kavi", "indraḥ"] in splits

def test_savarna_dirgha_u():
    cands, reason = _sandhi_gen.invert_sandhi("bhānūdayaḥ")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["bhānu", "udayaḥ"] in splits

# 2. Guna Inversion
def test_guna_e():
    cands, reason = _sandhi_gen.invert_sandhi("devendraḥ")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["deva", "indraḥ"] in splits
    assert cands[0][1] == "guna"

def test_guna_o():
    cands, reason = _sandhi_gen.invert_sandhi("sūryodayaḥ")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["sūrya", "udayaḥ"] in splits
    assert cands[0][1] == "guna"

def test_guna_ar():
    cands, reason = _sandhi_gen.invert_sandhi("maharṣiḥ")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["maha", "ṛṣiḥ"] in splits

# 3. Yan Inversion
def test_yan_y():
    cands, reason = _sandhi_gen.invert_sandhi("ityāha")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["iti", "āha"] in splits
    assert cands[0][1] == "iko_yan_aci"

def test_yan_v():
    cands, reason = _sandhi_gen.invert_sandhi("madhvariḥ")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["madhu", "ariḥ"] in splits

# 4. Scutva & Hal Inversion
def test_scutva_cc():
    cands, reason = _sandhi_gen.invert_sandhi("rājaputracca")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["rājaputrat", "ca"] in splits
    assert cands[0][1] == "ścutva"

# 5. Visarga Inversion
def test_visarga_o_space():
    cands, reason = _sandhi_gen.invert_sandhi("devo gacchati")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["devaḥ", "gacchati"] in splits
    assert cands[0][1] == "visarga_o"

# 6. Purvarupa Inversion
def test_purvarupa_avagraha():
    cands, reason = _sandhi_gen.invert_sandhi("so 'yam")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["saḥ", "ayam"] in splits
    assert cands[0][1] == "visarga_o_with_avagraha"

def test_purvarupa_e_avagraha():
    cands, reason = _sandhi_gen.invert_sandhi("te 'pi")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["te", "api"] in splits
    assert cands[0][1] == "pūrvarūpa"

# 7. Diagnostics & Determinism
def test_surface_too_short():
    cands, reason = _sandhi_gen.invert_sandhi("a")
    assert cands == []
    assert reason == "surface_too_short"

def test_no_rule_matches():
    cands, reason = _sandhi_gen.invert_sandhi("kptm")
    assert cands == []
    assert reason == "no_rule_matches"

def test_determinism_identical_runs():
    res1, r1 = _sandhi_gen.invert_sandhi("himālayaḥ")
    res2, r2 = _sandhi_gen.invert_sandhi("himālayaḥ")
    assert r1 == r2
    assert res1 == res2

def test_contract_rule_enums_valid():
    valid_enums = {
        "savarna_dirgha", "guna", "vṛddhi", "visarga_o",
        "visarga_o_with_avagraha", "visarga_r", "jastva",
        "ścutva", "iko_yan_aci", "ṛ_varṇa_sandhi", "pūrvarūpa",
        "para_rūpa", "anunāsika", "other"
    }
    sample_surfaces = ["himālayaḥ", "devendraḥ", "ityāha", "rājaputracca", "devo gacchati"]
    for s in sample_surfaces:
        cands, _ = _sandhi_gen.invert_sandhi(s)
        for _, rule, canon, conf in cands:
            assert rule in valid_enums
            assert canon != ""
            assert 0.0 < conf <= 1.0

# 8. Jastva and Yan-r Deferral Safety Fence (Risk 2)
def test_deferred_surfaces_remain_empty_in_v060():
    deferred = ["vāgīśaḥ", "tadapi"]
    for s in deferred:
        cands, reason = _sandhi_gen.invert_sandhi(s)
        assert cands == [], (
            f"Deferred surface {s!r} produced {cands}. "
            f"v0.6.1 scope requires these to remain empty until jastva/yan-r land."
        )

# 9. Golden Corpus Rank-1 Non-Contradiction Fence (Risk 1)
def _load_manifest_cases():
    p = Path(__file__).resolve().parents[2] / "corpus" / "golden_corpus_manifest.json"
    if not p.exists():
        return []
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    cases = []
    for c in data.get("cases", []):
        inp = c.get("input")
        exp = c.get("expect", {})
        split = exp.get("split") or exp.get("primary_split")
        if inp and split:
            cases.append((c["id"], inp, split))
    return cases

_MANIFEST_CASES = _load_manifest_cases()

@pytest.mark.parametrize("case_id,surface,expected_split", _MANIFEST_CASES)
def test_no_false_positives_on_golden_corpus_surfaces(case_id, surface, expected_split):
    cands, reason = _sandhi_gen.invert_sandhi(surface)
    if not cands:
        return
    # Risk 1 Check: Must align at rank-1 when generator engages
    assert cands[0][0] == expected_split, (
        f"[{case_id}] invert_sandhi({surface!r}) rank-1 split is {cands[0][0]}, "
        f"which contradicts golden expected split {expected_split}"
    )
# 4b. Explicit Hal & Yan-r Unit Verification (v0.6.3 additions)
def test_yan_r_inversion_pitrajna():
    cands, reason = _sandhi_gen.invert_sandhi("pitrājñā")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["pitṛ", "ājñā"] in splits
    assert cands[0][1] == "ṛ_varṇa_sandhi"

def test_scutva_jja_sajjanah():
    cands, reason = _sandhi_gen.invert_sandhi("sajjanaḥ")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["sat", "janaḥ"] in splits
    assert cands[0][1] == "jastva"

def test_scutva_ttva_tattvam():
    cands, reason = _sandhi_gen.invert_sandhi("tattvam")
    assert reason is None
    splits = [c[0] for c in cands]
    assert ["tat", "tvam"] in splits

# 10. End-to-End Engine Wiring Verification
def test_engine_parse_uses_generator_for_a_cases():
    active_a_cases = [
        ("rāmo gacchati", ["rāmaḥ", "gacchati"]),
        ("himālayaḥ", ["hima", "alayaḥ"]),
        ("nāsti", ["na", "asti"]),
        ("tacca", ["tat", "ca"]),
        ("sajjanaḥ", ["sat", "janaḥ"]),
        ("rāmāyeti", ["rāmāya", "iti"]),
        ("ityapi", ["iti", "api"]),
        ("madhvari", ["madhu", "ari"]),
        ("devendraḥ", ["deva", "indraḥ"]),
        ("gaṇeśaḥ", ["gaṇa", "īśaḥ"]),
        ("pitrājñā", ["pitṛ", "ājñā"]),
        ("tattvam", ["tat", "tvam"]),
        ("naro 'pi", ["naraḥ", "api"])
    ]
    for surface, expected_split in active_a_cases:
        gen_cands, _ = _sandhi_gen.invert_sandhi(surface)
        assert gen_cands, f"{surface} must fire in _sandhi_gen"
        doc = engine.parse(surface)
        assert doc is not None, f"engine.parse({surface!r}) returned None"
        produced_split = doc["sandhi_splits"][0]["parts"]
        assert produced_split == expected_split, (
            f"{surface}: engine.parse split is {produced_split}, "
            f"expected generator rank-1 {expected_split}"
        )
# 11. Corpus Coverage Audit Invariant (v0.6.4)
def test_corpus_coverage_audit_metrics():
    doc_path = Path(__file__).resolve().parents[2] / "docs" / "corpus_coverage.md"
    assert doc_path.exists(), "docs/corpus_coverage.md must exist"
    content = doc_path.read_text(encoding="utf-8")
    assert "106" in content and "fires_1" in content and "fallback" in content
    assert "fires_1" in content
    assert "fallback" in content

    # Empirical assertion against live manifest
    p = Path(__file__).resolve().parents[2] / "corpus" / "golden_corpus_manifest.json"
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    fires = 0
    fallback = 0
    for c in data.get("cases", []):
        cands, _ = _sandhi_gen.invert_sandhi(c["input"])
        if cands:
            fires += 1
        else:
            fallback += 1
            
    assert fires == 22, f"Expected 22 firing cases, got {fires}"
    assert fallback == 84, f"Expected 84 fallback cases, got {fallback}"
