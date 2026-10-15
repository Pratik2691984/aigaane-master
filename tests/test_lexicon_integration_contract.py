"""
Phase 0 probe: VidyutKosha.exists() integration contract.

NON-GATING. This module observes and records the shape, semantics, and
latency of the lexicon existence check so Phases 1-3 (morphology, chandas,
sandhi) can be written against a known contract instead of an assumed one.

Invariants allowed to fail the suite:
  1. /exists is reachable and returns a JSON object for every probe input.
  2. At least one boolean verdict field is common to all responses.
  3. p95 local latency is under PROBE_LATENCY_CEILING_MS.

Everything else -- key divergence between hit and miss, the batch endpoint's
existence, the accepted query-parameter name -- is recorded to
tests/fixtures/lexicon_exists_probe.json for human review and NOT asserted.
"""

import json
import time
from pathlib import Path

import pytest

EXISTS_PATH = "/api/v3/lexicon/exists"
BATCH_PATH = "/api/v3/lexicon/exists/batch"

PARAM_CANDIDATES = ("word", "lemma", "form", "surface", "term", "q")

PROBES = (
    ("lemma_iast", "rāma"),
    ("lemma_deva", "राम"),
    ("inflected_iast", "rāmāya"),
    ("sandhi_surface", "rāmo'pi"),
    ("negative_control", "zzzqqqxyz"),
)

LEMMA = "rāma"
PROBE_LATENCY_SAMPLES = 30
PROBE_LATENCY_CEILING_MS = 250.0

PROBE_OUT = Path(__file__).parent / "fixtures" / "lexicon_exists_probe.json"
_PROBE: dict = {}


def _safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {"__non_json__": resp.text[:200]}


def _shape(payload):
    if not isinstance(payload, dict):
        return {"__type__": type(payload).__name__}
    return {k: type(v).__name__ for k, v in sorted(payload.items())}


@pytest.fixture(scope="module")
def exists_param(client):
    """Discover the accepted query-parameter name. Fails loudly if none work."""
    attempts = {}
    for name in PARAM_CANDIDATES:
        r = client.get(EXISTS_PATH, params={name: LEMMA})
        attempts[name] = r.status_code
        if r.status_code == 200:
            return name
    pytest.fail(f"no candidate query parameter accepted by {EXISTS_PATH}: {attempts}")


@pytest.fixture(scope="module", autouse=True)
def _run_probe(client, exists_param):
    """Collect every probe response exactly once, then flush to disk."""
    _PROBE["param"] = exists_param
    _PROBE["responses"] = {}

    for label, word in PROBES:
        r = client.get(EXISTS_PATH, params={exists_param: word})
        payload = _safe_json(r)
        _PROBE["responses"][label] = {
            "word": word,
            "status_code": r.status_code,
            "payload": payload,
            "shape": _shape(payload),
        }

    rb = client.post(BATCH_PATH, json={"words": [w for _, w in PROBES]})
    _PROBE["batch"] = {"status_code": rb.status_code, "payload": _safe_json(rb)}

    samples = []
    for _ in range(PROBE_LATENCY_SAMPLES):
        t0 = time.perf_counter()
        client.get(EXISTS_PATH, params={exists_param: LEMMA})
        samples.append((time.perf_counter() - t0) * 1000.0)
    samples.sort()
    _PROBE["latency_ms"] = {
        "n": len(samples),
        "p50": round(samples[len(samples) // 2], 3),
        "p95": round(samples[max(0, int(len(samples) * 0.95) - 1)], 3),
        "max": round(samples[-1], 3),
    }

    yield

    PROBE_OUT.parent.mkdir(parents=True, exist_ok=True)
    PROBE_OUT.write_text(
        json.dumps(_PROBE, indent=2, ensure_ascii=False, sort_keys=True)
    )


def test_probe_ran():
    assert _PROBE.get("responses"), "probe fixture did not execute"


def test_exists_reachable_for_all_probes():
    for label, rec in _PROBE["responses"].items():
        assert rec["status_code"] == 200, (
            f"{label} ({rec['word']!r}): HTTP {rec['status_code']}"
        )


def test_exists_returns_json_object():
    for label, rec in _PROBE["responses"].items():
        assert isinstance(rec["payload"], dict), (
            f"{label}: expected JSON object, got {rec['shape']}"
        )


def test_boolean_verdict_field_is_common():
    """A single boolean key must be present in every response."""
    bool_keys = {
        label: sorted(k for k, v in rec["payload"].items() if isinstance(v, bool))
        for label, rec in _PROBE["responses"].items()
    }
    _PROBE["boolean_keys"] = bool_keys
    common = set.intersection(*(set(v) for v in bool_keys.values()))
    assert common, f"no boolean field common to all responses: {bool_keys}"


def test_latency_within_local_ceiling():
    p95 = _PROBE["latency_ms"]["p95"]
    assert p95 < PROBE_LATENCY_CEILING_MS, (
        f"local p95 {p95}ms exceeds {PROBE_LATENCY_CEILING_MS}ms "
        f"(full profile: {_PROBE['latency_ms']})"
    )