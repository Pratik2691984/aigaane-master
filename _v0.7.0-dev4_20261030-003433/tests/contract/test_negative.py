"""
Aigaane v0.2.1 — Negative Test Suite

Strict rejection tests: every test builds a DELIBERATELY INVALID document
and asserts that the corresponding schema validator returns at least one
error. If any of these pass a validation check, the schema has regressed
to over-permissive and this file catches it.

Target: 17 tests (N01–N17), all passing.

Run:
    python -m pytest tests/contract/test_negative.py -v -p no:cacheprovider -c NUL --rootdir=.
"""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"


def _load(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


CONTRACT = _load(SCHEMAS / "sanskrit_contract.json")
SAMASA = _load(SCHEMAS / "samasa_node.json")
ROUTER = _load(SCHEMAS / "router_policy.json")


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

DECISION_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://aigaane.in/schemas/router_decision_negative.json",
    "$ref": "https://aigaane.in/schemas/router_policy.json#/$defs/RoutingDecision",
}
DECISION_VALIDATOR = Draft202012Validator(
    DECISION_SCHEMA, registry=REGISTRY, format_checker=_FORMAT_CHECKER
)


# ---------------------------------------------------------------------------
# Baseline valid document — every negative test mutates one field
# ---------------------------------------------------------------------------

def _valid_doc():
    """Minimal valid v0.2 document, used as the base for mutation tests."""
    return {
        "schema_version": "0.2.0",
        "trace_id": "00000000-0000-0000-0000-000000000001",
        "script_original": "iast",
        "surface": "ca",
        "normalized": "च",
        "transliteration": {"devanagari": "च", "iast": "ca"},
        "parse_rank": 1,
        "tokens": [
            {
                "token_id": "T0",
                "pada": "ca",
                "stem": "ca",
                "vibhakti": "na",
                "vacana": "na",
                "linga": "na",
                "pos": "nipata",
                "confidence": 0.99,
            }
        ],
        "sandhi_splits": [],
        "ambiguous_parses": [],
        "confidence": 0.99,
        "confidence_aggregate": {"min": 0.99, "mean": 0.99},
        "provenance": ["test"],
    }


def _valid_decision():
    """Minimal valid RoutingDecision."""
    return {
        "studio": "Studio_I",
        "intent_class": "creative_narrative",
        "classifier_confidence": 0.9,
    }


def _assert_rejected(validator, doc, hint):
    errors = list(validator.iter_errors(doc))
    assert errors, (
        f"SCHEMA REGRESSION: schema accepted invalid document. {hint}. "
        f"Document was: {json.dumps(doc, ensure_ascii=False)[:200]}"
    )


def _assert_baseline_valid(validator, doc, hint):
    """Sanity: unmodified baseline must pass (catches false-positive negatives)."""
    errors = list(validator.iter_errors(doc))
    assert not errors, (
        f"BASELINE BROKEN: valid document rejected before mutation. {hint}. "
        f"Errors: {[e.message for e in errors]}"
    )


# ---------------------------------------------------------------------------
# N01–N13: contract-level rejection
# ---------------------------------------------------------------------------

class TestContractRejection:

    def test_N01_missing_ambiguous_parses(self):
        doc = _valid_doc()
        del doc["ambiguous_parses"]
        _assert_rejected(CONTRACT_VALIDATOR, doc, "N01: missing ambiguous_parses")

    def test_N02_missing_trace_id(self):
        doc = _valid_doc()
        del doc["trace_id"]
        _assert_rejected(CONTRACT_VALIDATOR, doc, "N02: missing trace_id")

    def test_N03_malformed_trace_id(self):
        doc = _valid_doc()
        doc["trace_id"] = "not-a-uuid"
        _assert_rejected(
            CONTRACT_VALIDATOR, doc,
            "N03: trace_id='not-a-uuid' — format_checker must reject"
        )

    def test_N04_tinanta_missing_dhatu(self):
        doc = _valid_doc()
        doc["tokens"] = [{
            "token_id": "T0",
            "pada": "bhavati",
            "stem": "bhavat",
            "pos": "tinanta",
            "vibhakti": "na",
            "vacana": "ekavacana",
            "linga": "na",
            # dhatu intentionally omitted
            "gana": 1,
            "confidence": 0.9,
        }]
        _assert_rejected(CONTRACT_VALIDATOR, doc, "N04: tinanta without dhatu")

    def test_N05_tinanta_missing_gana(self):
        doc = _valid_doc()
        doc["tokens"] = [{
            "token_id": "T0",
            "pada": "bhavati",
            "stem": "bhavat",
            "pos": "tinanta",
            "vibhakti": "na",
            "vacana": "ekavacana",
            "linga": "na",
            "dhatu": "bhū",
            # gana intentionally omitted
            "confidence": 0.9,
        }]
        _assert_rejected(CONTRACT_VALIDATOR, doc, "N05: tinanta without gana")

    def test_N06_tinanta_with_vibhakti(self):
        doc = _valid_doc()
        doc["tokens"] = [{
            "token_id": "T0",
            "pada": "bhavati",
            "stem": "bhavat",
            "pos": "tinanta",
            "vibhakti": "prathama",   # must be "na" for tinanta
            "vacana": "ekavacana",
            "linga": "na",
            "dhatu": "bhū",
            "gana": 1,
            "confidence": 0.9,
        }]
        _assert_rejected(
            CONTRACT_VALIDATOR, doc,
            "N06: tinanta with vibhakti='prathama' (must be 'na')"
        )

    def test_N07_subhanta_with_vibhakti_na(self):
        doc = _valid_doc()
        doc["tokens"] = [{
            "token_id": "T0",
            "pada": "rāmaḥ",
            "stem": "rāma",
            "pos": "subhanta",
            "vibhakti": "na",         # subhanta must have real vibhakti
            "vacana": "ekavacana",
            "linga": "pullinga",
            "confidence": 0.9,
        }]
        _assert_rejected(
            CONTRACT_VALIDATOR, doc,
            "N07: subhanta with vibhakti='na' (must be a case)"
        )

    def test_N08_avyaya_with_linga(self):
        doc = _valid_doc()
        doc["tokens"] = [{
            "token_id": "T0",
            "pada": "ca",
            "stem": "ca",
            "pos": "avyaya",
            "vibhakti": "na",
            "vacana": "na",
            "linga": "pullinga",      # avyaya must have linga="na"
            "confidence": 0.9,
        }]
        _assert_rejected(
            CONTRACT_VALIDATOR, doc,
            "N08: avyaya with linga='pullinga' (must be 'na')"
        )

    def test_N09_sandhi_rule_out_of_enum(self):
        doc = _valid_doc()
        doc["sandhi_splits"] = [{
            "parts": ["ca", "api"],
            "rule": "not_a_real_rule",
            "confidence": 0.9,
        }]
        _assert_rejected(
            CONTRACT_VALIDATOR, doc,
            "N09: sandhi_splits[0].rule not in SandhiRule enum"
        )

    def test_N10_samasa_type_out_of_enum(self):
        doc = _valid_doc()
        doc["samasa_tree"] = {
            "component_surface": "rājaputraḥ",
            "role": "single",
            "type": "not_a_compound_type",
            "confidence": 0.9,
        }
        _assert_rejected(
            CONTRACT_VALIDATOR, doc,
            "N10: samasa_tree.type not in SamasaNode.type enum"
        )

    def test_N11_alternative_parse_rank_too_low(self):
        doc = _valid_doc()
        doc["ambiguous_parses"] = [{
            "parse_rank": 1,           # must be >= 2
            "tokens": [doc["tokens"][0]],
            "confidence": 0.5,
            "ambiguity_type": "homonym",
        }]
        _assert_rejected(
            CONTRACT_VALIDATOR, doc,
            "N11: AlternativeParse.parse_rank=1 (must be >= 2)"
        )

    def test_N12_confidence_out_of_range(self):
        doc = _valid_doc()
        doc["confidence"] = 1.5
        _assert_rejected(
            CONTRACT_VALIDATOR, doc,
            "N12: confidence=1.5 (must be 0.0-1.0)"
        )

    def test_N13_wrong_schema_version(self):
        doc = _valid_doc()
        doc["schema_version"] = "0.1.9"
        _assert_rejected(
            CONTRACT_VALIDATOR, doc,
            "N13: schema_version='0.1.9' (must be '0.2.0')"
        )


# ---------------------------------------------------------------------------
# N14: RoutingDecision intent_class enum enforcement
# ---------------------------------------------------------------------------

class TestDecisionRejection:

    def test_N14_bad_intent_class(self):
        dec = _valid_decision()
        dec["intent_class"] = "logical_argument"   # typo — not in enum
        _assert_rejected(
            DECISION_VALIDATOR, dec,
            "N14: intent_class='logical_argument' (should be 'logical_argumentation')"
        )


# ---------------------------------------------------------------------------
# N15–N17: NyayaSyllogism structural rejection
# ---------------------------------------------------------------------------

def _valid_nyaya_decision():
    dec = _valid_decision()
    dec["studio"] = "Studio_II"
    dec["intent_class"] = "logical_argumentation"
    dec["nyaya_verifier_mode"] = "deterministic"
    dec["nyaya_syllogism"] = {
        "steps": [
            {"step": "pratijna",  "text": "parvato vahnimān",
             "canon_ref": "NS 1.1.33", "verifier_status": "verified",
             "confidence": 0.95},
            {"step": "hetu",      "text": "dhūmavattvāt",
             "canon_ref": "NS 1.1.34", "verifier_status": "verified",
             "confidence": 0.95},
            {"step": "udaharana", "text": "yathā pākāśālā",
             "canon_ref": "NS 1.1.36", "verifier_status": "verified",
             "confidence": 0.90},
            {"step": "upanaya",   "text": "tathā ayam parvatas",
             "canon_ref": "NS 1.1.38", "verifier_status": "verified",
             "confidence": 0.93},
            {"step": "nigamana",  "text": "tasmāt parvato vahnimān",
             "canon_ref": "NS 1.1.39", "verifier_status": "verified",
             "confidence": 0.95},
        ],
        "on_reject": "block_response_and_return_verifier_trace",
        "on_unverifiable": "escalate_to_human_expert",
        "verifier_trace_id": "00000000-0000-0000-0000-000000000002",
    }
    return dec


class TestNyayaSyllogismRejection:

    def test_baseline_valid_nyaya_decision(self):
        """Sanity: the Nyaya decision we mutate below must be valid first."""
        dec = _valid_nyaya_decision()
        _assert_baseline_valid(DECISION_VALIDATOR, dec,
                               "Nyaya baseline decision must be valid")

    def test_N15_nyaya_only_4_steps(self):
        dec = _valid_nyaya_decision()
        dec["nyaya_syllogism"]["steps"] = dec["nyaya_syllogism"]["steps"][:4]
        _assert_rejected(
            DECISION_VALIDATOR, dec,
            "N15: nyaya_syllogism.steps has only 4 entries (minItems=5)"
        )

    def test_N16_nyaya_bad_verifier_status(self):
        dec = _valid_nyaya_decision()
        dec["nyaya_syllogism"]["steps"][0]["verifier_status"] = "ok"
        _assert_rejected(
            DECISION_VALIDATOR, dec,
            "N16: verifier_status='ok' (must be one of the 4 enum values)"
        )

    def test_N17_nyaya_bad_step_name(self):
        dec = _valid_nyaya_decision()
        dec["nyaya_syllogism"]["steps"][0]["step"] = "pratijna2"
        _assert_rejected(
            DECISION_VALIDATOR, dec,
            "N17: step='pratijna2' (must be one of the 5 enum values)"
        )