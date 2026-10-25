"""
Aigaane v0.2.0 â€” Golden Corpus Test Harness

Run from repo root:
    python -m pytest tests/contract/test_contract.py -q -p no:cacheprovider -c NUL --rootdir=.

Target first run:
    13 passed, 82 failed  (A01, E01, F01 green from engine_stub fixtures;
                           remaining 92 = engine TDD backlog)

Requires: pytest>=8, jsonschema>=4.18, referencing>=0.30
"""

import json
import unicodedata
from collections import Counter
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


# ---------------------------------------------------------------------------
# Paths & loading
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]  # tests/contract/ -> repo root
SCHEMAS = ROOT / "schemas"
CORPUS_FILE = ROOT / "corpus" / "golden_corpus_manifest.json"


def _load(path: Path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


if not CORPUS_FILE.exists():
    pytest.skip(
        f"corpus manifest missing at {CORPUS_FILE}", allow_module_level=True
    )

CONTRACT = _load(SCHEMAS / "sanskrit_contract.json")
SAMASA = _load(SCHEMAS / "samasa_node.json")
ROUTER = _load(SCHEMAS / "router_policy.json")
CORPUS = _load(CORPUS_FILE)


# ---------------------------------------------------------------------------
# Cross-file $ref registry
# ---------------------------------------------------------------------------

def _build_registry():
    reg = Registry()
    for schema, path in [
        (CONTRACT, SCHEMAS / "sanskrit_contract.json"),
        (SAMASA, SCHEMAS / "samasa_node.json"),
        (ROUTER, SCHEMAS / "router_policy.json"),
    ]:
        uri = schema.get("$id") or path.as_uri()
        reg = reg.with_resource(
            uri, Resource.from_contents(schema, default_specification=DRAFT202012)
        )
    return reg


REGISTRY = _build_registry()
_FORMAT_CHECKER = FormatChecker()

CONTRACT_VALIDATOR = Draft202012Validator(
    CONTRACT, registry=REGISTRY, format_checker=_FORMAT_CHECKER
)
ROUTER_VALIDATOR = Draft202012Validator(
    ROUTER, registry=REGISTRY, format_checker=_FORMAT_CHECKER
)

# Decision schema: { "$ref": "https://aigaane.in/schemas/router_policy.json#/$defs/RoutingDecision" }
DECISION_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://aigaane.in/schemas/router_decision.json",
    "$ref": "https://aigaane.in/schemas/router_policy.json#/$defs/RoutingDecision",
}
DECISION_VALIDATOR = Draft202012Validator(
    DECISION_SCHEMA, registry=REGISTRY, format_checker=_FORMAT_CHECKER
)


# ---------------------------------------------------------------------------
# Engine loader
# ---------------------------------------------------------------------------

def _get_engine():
    import importlib
    import os

    module_name = os.environ.get("AIGAANE_ENGINE_MODULE", "engine_stub")
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        pytest.fail(
            f"engine module '{module_name}' not importable: {e}. "
            f"Set AIGAANE_ENGINE_MODULE env var or ensure module is on sys.path."
        )


# ---------------------------------------------------------------------------
# Intent hint (stub router doesn't classify; harness supplies a hint)
# ---------------------------------------------------------------------------

INTENT_HINTS = {
    "A_": "creative_narrative",
    "B_": "creative_narrative",
    "C_": "creative_narrative",
    "D_": "creative_narrative",
    "E_": "creative_narrative",
    "F_": "logical_argumentation",
    "G_": "chhandas_meter_validation",
    "H_": "scientific_verification",
}


def _infer_intent(case):
    return INTENT_HINTS.get(case["cat"][:2], "creative_narrative")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _nfc(s):
    return unicodedata.normalize("NFC", s) if isinstance(s, str) else s


def _nfc_list(xs):
    return [_nfc(x) for x in xs]


def _nfc_lower(s):
    return _nfc(s).lower() if isinstance(s, str) else s


def _compound_depth(node):
    if not node or not node.get("type"):
        return 0
    kids = node.get("children") or []
    return 1 + max((_compound_depth(c) for c in kids), default=0)


def _count_nested_compounds(node):
    kids = node.get("children") or []
    return sum(1 for k in kids if k.get("type"))


# ---------------------------------------------------------------------------
# Expectation checker
# ---------------------------------------------------------------------------

def _assert_expectations(case_id, doc, decision, exp):
    def fail(msg):
        pytest.fail(f"[{case_id}] {msg}")

    # --- sandhi (NFC-normalized) ---
    if "split" in exp:
        actual = [_nfc_list(s["parts"]) for s in doc["sandhi_splits"]]
        target = _nfc_list(exp["split"])
        if target not in actual:
            fail(f"sandhi split {target!r} not in {actual!r}")

    if "primary_split" in exp:
        if not doc["sandhi_splits"]:
            fail("expected primary_split but sandhi_splits is empty")
        actual = _nfc_list(doc["sandhi_splits"][0]["parts"])
        target = _nfc_list(exp["primary_split"])
        if actual != target:
            fail(f"primary split {actual!r} != {target!r}")

    if "sandhi_rule" in exp:
        rules = [_nfc(s["rule"]) for s in doc["sandhi_splits"]]
        if _nfc(exp["sandhi_rule"]) not in rules:
            fail(f"sandhi rule {exp['sandhi_rule']!r} not in {rules!r}")

    # --- tokens ---
    if "tokens" in exp and len(doc["tokens"]) != exp["tokens"]:
        fail(f"token count {len(doc['tokens'])} != {exp['tokens']}")

    token_fields = ("pos", "dhatu", "gana", "linga", "vibhakti", "vacana")
    if any(k in exp for k in token_fields):
        if not doc["tokens"]:
            fail("expected token fields but tokens is empty")
        t = doc["tokens"][0]
        for k in token_fields:
            if k in exp and t.get(k) != exp[k]:
                fail(f"token[0].{k}: {t.get(k)!r} != {exp[k]!r}")

    # --- ambiguity ---
    if "ambiguous_parses" in exp:
        n = len(doc["ambiguous_parses"])
        if n != exp["ambiguous_parses"]:
            fail(f"ambiguous_parses count {n} != {exp['ambiguous_parses']}")

    if "ambiguity_type" in exp:
        types = [a.get("ambiguity_type") for a in doc["ambiguous_parses"]]
        if exp["ambiguity_type"] not in types:
            fail(f"ambiguity type {exp['ambiguity_type']!r} not in {types!r}")

    # --- samasa ---
    if "samasa_type" in exp:
        tree = doc.get("samasa_tree") or {}
        if tree.get("type") != exp["samasa_type"]:
            fail(f"samasa type {tree.get('type')!r} != {exp['samasa_type']!r}")

    if "depth" in exp:
        d = _compound_depth(doc.get("samasa_tree"))
        if d != exp["depth"]:
            fail(f"compound depth {d} != {exp['depth']}")

    if "nested_children" in exp:
        n = _count_nested_compounds(doc.get("samasa_tree"))
        if n != exp["nested_children"]:
            fail(f"nested compound children {n} != {exp['nested_children']}")

    # --- prosody ---
    if "chhandas" in exp:
        refs = doc.get("canon_refs") or []
        ch_refs = [r for r in refs if r.get("domain") == "chhandas"]
        if not ch_refs:
            fail(f"no canon_ref with domain='chhandas'; refs={refs!r}")
        haystack = _nfc_lower(
            " ".join(
                f"{r.get('canon_name', '')} {r.get('reference_locator', '')}"
                for r in ch_refs
            )
        )
        if _nfc_lower(exp["chhandas"]) not in haystack:
            fail(
                f"chhandas {exp['chhandas']!r} not present in chhandas "
                f"canon_refs: {haystack!r}"
            )

    # --- cross-domain mapping ---
    if "mapping" in exp:
        refs = doc.get("canon_refs") or []
        haystack = _nfc_lower(
            " ".join(
                f"{r.get('canon_name', '')} {r.get('reference_locator', '')} "
                f"{r.get('domain', '')}"
                for r in refs
            )
        )
        key = _nfc_lower(exp["mapping"].split("/")[0].strip())
        if key not in haystack:
            fail(f"mapping {exp['mapping']!r} not reflected in canon_refs")

    if "canon_domain" in exp:
        domains = [r.get("domain") for r in (doc.get("canon_refs") or [])]
        if exp["canon_domain"] not in domains:
            fail(f"canon_domain {exp['canon_domain']!r} not in {domains!r}")

    # --- routing ---
    if "router_studio" in exp:
        if decision is None:
            fail("router returned None")
        if decision.get("studio") != exp["router_studio"]:
            fail(
                f"router studio {decision.get('studio')!r} "
                f"!= {exp['router_studio']!r}"
            )

    # --- nyaya (STRICTLY on decision) ---
    if "nyaya_template" in exp or "verifier_mode" in exp:
        if decision is None:
            fail("router returned None; expected Nyaya decision payload")

    if "nyaya_template" in exp:
        syl = decision.get("nyaya_syllogism")
        if not syl:
            fail(
                "decision['nyaya_syllogism'] missing â€” Nyaya payload MUST live "
                "on the decision, not on the parse document."
            )
        steps = [s.get("step") for s in syl.get("steps", [])]
        if steps != exp["nyaya_template"]:
            fail(f"nyaya steps {steps!r} != {exp['nyaya_template']!r}")

        required = {"step", "text", "canon_ref", "verifier_status", "confidence"}
        allowed_status = {
            "verified", "flagged_advisory", "rejected_inconsistent", "unverifiable"
        }
        for s in syl.get("steps", []):
            missing = required - set(s.keys())
            if missing:
                fail(f"nyaya step {s.get('step')!r} missing fields {sorted(missing)}")
            if s.get("verifier_status") not in allowed_status:
                fail(
                    f"nyaya step {s.get('step')!r} verifier_status "
                    f"{s.get('verifier_status')!r} not in {sorted(allowed_status)}"
                )

    if "verifier_mode" in exp:
        actual = decision.get("nyaya_verifier_mode")
        if actual is None:
            fail(
                "decision['nyaya_verifier_mode'] missing â€” must be set "
                "directly on the decision."
            )
        if actual != exp["verifier_mode"]:
            fail(f"verifier mode {actual!r} != {exp['verifier_mode']!r}")

        syl = decision.get("nyaya_syllogism")
        if syl:
            expected_on_reject = (
                "block_response_and_return_verifier_trace"
                if actual == "deterministic"
                else "attach_advisory_flag_continue"
            )
            if syl.get("on_reject") != expected_on_reject:
                fail(
                    f"nyaya_syllogism.on_reject {syl.get('on_reject')!r} "
                    f"!= {expected_on_reject!r} for mode {actual!r}"
                )


# ---------------------------------------------------------------------------
# Meta tests â€” schemas themselves must be valid
# ---------------------------------------------------------------------------

class TestSchemasSelfValid:
    def test_contract_schema_valid(self):
        Draft202012Validator.check_schema(CONTRACT)

    def test_samasa_schema_valid(self):
        Draft202012Validator.check_schema(SAMASA)

    def test_router_schema_valid(self):
        Draft202012Validator.check_schema(ROUTER)

    def test_cross_file_ref_resolves(self):
        sample = {
            "schema_version": "0.2.0",
            "trace_id": "00000000-0000-0000-0000-000000000000",
            "script_original": "iast",
            "surface": "x",
            "normalized": "x",
            "transliteration": {"devanagari": "x", "iast": "x"},
            "parse_rank": 1,
            "tokens": [
                {"pada": "x", "stem": "x", "vibhakti": "na", "vacana": "na",
                 "linga": "na", "pos": "avyaya", "confidence": 0.9}
            ],
            "sandhi_splits": [],
            "ambiguous_parses": [],
            "confidence": 0.9,
            "confidence_aggregate": {"min": 0.9, "mean": 0.9},
        }
        errors = list(CONTRACT_VALIDATOR.iter_errors(sample))
        assert not errors, (
            "cross-file $ref failed:\n"
            + "\n".join(
                f"  path={list(e.absolute_path)} msg={e.message}" for e in errors
            )
        )

    def test_recursive_samasa_ref_resolves(self):
        tree = {
            "component_surface": "x",
            "role": "single",
            "type": "tatpurusha",
            "confidence": 0.9,
            "children": [
                {"component_surface": "a", "role": "purva_pada",
                 "type": "tatpurusha", "confidence": 0.9,
                 "children": [
                     {"component_surface": "a1", "role": "purva_pada", "confidence": 0.9},
                     {"component_surface": "a2", "role": "uttara_pada", "confidence": 0.9},
                 ]},
                {"component_surface": "b", "role": "uttara_pada", "confidence": 0.9},
            ],
        }
        sample = {
            "schema_version": "0.2.0",
            "trace_id": "00000000-0000-0000-0000-000000000001",
            "script_original": "iast",
            "surface": "x",
            "normalized": "x",
            "transliteration": {"devanagari": "x", "iast": "x"},
            "parse_rank": 1,
            "tokens": [
                {"pada": "x", "stem": "x", "vibhakti": "na", "vacana": "na",
                 "linga": "na", "pos": "avyaya", "confidence": 0.9}
            ],
            "sandhi_splits": [],
            "samasa_tree": tree,
            "ambiguous_parses": [],
            "confidence": 0.9,
            "confidence_aggregate": {"min": 0.9, "mean": 0.9},
        }
        errors = list(CONTRACT_VALIDATOR.iter_errors(sample))
        assert not errors, (
            "recursive samasa $ref failed:\n"
            + "\n".join(
                f"  path={list(e.absolute_path)} msg={e.message}" for e in errors
            )
        )

    def test_decision_contract_self_validates(self):
        ok = {
            "studio": "Studio_I",
            "intent_class": "creative_narrative",
            "classifier_confidence": 0.9,
        }
        assert not list(DECISION_VALIDATOR.iter_errors(ok))


# ---------------------------------------------------------------------------
# Corpus sanity
# ---------------------------------------------------------------------------

class TestCorpusSanity:
    def test_total_cases(self):
        assert len(CORPUS["cases"]) == CORPUS["total_cases"]
        assert CORPUS["total_cases"] == 106

    def test_category_counts(self):
        actual = Counter(c["cat"] for c in CORPUS["cases"])
        for cat, expected in CORPUS["categories"].items():
            assert actual[cat] == expected, f"{cat}: {actual[cat]} != {expected}"

    def test_case_ids_unique(self):
        ids = [c["id"] for c in CORPUS["cases"]]
        assert len(ids) == len(set(ids)), "duplicate case IDs in corpus"


# ---------------------------------------------------------------------------
# Golden corpus runner
# ---------------------------------------------------------------------------

def _corpus_cases():
    """Yield (id, case, skip_marker) tuples. skip_marker is None or a string."""
    out = []
    for c in CORPUS["cases"]:
        skip = c.get("skip_reason")
        out.append((c["id"], c, skip))
    return out


def _corpus_ids():
    return [c["id"] for c in CORPUS["cases"]]


@pytest.mark.parametrize("case_id,case,skip_reason", _corpus_cases(), ids=_corpus_ids())
def test_golden_case(case_id, case, skip_reason):
    if skip_reason:
        pytest.skip(f"[{case_id}] {skip_reason}")

    engine = _get_engine()

    doc = engine.parse(case["input"])
    if doc is None:
        pytest.fail(
            f"[{case_id}] engine.parse({case['input']!r}) returned None â€” "
            f"not yet implemented for this case."
        )

    errors = sorted(
        CONTRACT_VALIDATOR.iter_errors(doc),
        key=lambda e: list(e.absolute_path),
    )
    if errors:
        pytest.fail(
            f"[{case_id}] schema violations:\n"
            + "\n".join(
                f"  path={list(e.absolute_path)}  msg={e.message}"
                for e in errors
            )
        )

    decision = engine.route(doc, ROUTER, intent_hint=_infer_intent(case))

    if decision is not None:
        dec_errors = sorted(
            DECISION_VALIDATOR.iter_errors(decision),
            key=lambda e: list(e.absolute_path),
        )
        if dec_errors:
            pytest.fail(
                f"[{case_id}] routing decision schema violations:\n"
                + "\n".join(
                    f"  path={list(e.absolute_path)}  msg={e.message}"
                    for e in dec_errors
                )
            )

    _assert_expectations(case_id, doc, decision, case["expect"])
