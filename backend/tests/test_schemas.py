"""
Schema validation tests for the Aigaane-Quanta framework.

Validates:
1. All JSON schemas are valid Draft 2020-12
2. Golden corpus validates against seed schema
3. Real response envelope validates against sanskrit_contract schema
"""
import json
from pathlib import Path

import pytest
import jsonschema

ROOT = Path(__file__).resolve().parent.parent  # backend/
SCHEMAS_DIR = ROOT / "schemas"
CORPUS_DIR = ROOT / "corpus"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_registry():
    """Build a referencing registry so $ref across schemas resolve."""
    from referencing import Registry, Resource
    resources = []
    for schema_path in SCHEMAS_DIR.glob("*.schema.json"):
        schema = load_json(schema_path)
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def test_all_schemas_are_valid_draft_2020_12():
    for path in SCHEMAS_DIR.glob("*.schema.json"):
        schema = load_json(path)
        jsonschema.Draft202012Validator.check_schema(schema)


def test_golden_corpus_validates_against_seed_schema():
    corpus = load_json(CORPUS_DIR / "samasa_golden.json")
    seed_schema = load_json(SCHEMAS_DIR / "samasa_golden.seed.schema.json")
    registry = build_registry()
    validator = jsonschema.Draft202012Validator(seed_schema, registry=registry)
    errors = list(validator.iter_errors(corpus))
    assert not errors, f"Corpus failed seed schema: {[e.message for e in errors]}"


def test_contract_schema_accepts_real_rAjaputraH_response():
    """The verified response from v1.1.1-api-cleanup must validate."""
    contract_schema = load_json(SCHEMAS_DIR / "sanskrit_contract.schema.json")
    registry = build_registry()
    validator = jsonschema.Draft202012Validator(contract_schema, registry=registry)

    real_response = {
        "input_triad": {
            "devanagari": "राजपुत्रः",
            "iast": "rājaputraḥ",
            "slp1": "rAjaputraH"
        },
        "candidates": [
            {
                "candidate_id": "cand_01",
                "parse": [
                    {"surface": "rājan", "stem": "rājan", "role": "subanta:sambodhana"},
                    {"surface": "putraḥ", "stem": "putra", "role": "subanta:prathama"}
                ],
                "samasa_type": "tatpurusha",
                "vigraha": "rājñaḥ putraḥ",
                "sutra_chain": ["2.1.22", "2.2.8"],
                "authority": {
                    "recension": "Kasika_Vrtti",
                    "primary_source": "Aṣṭādhyāyī (0.2.0-ambiguity)",
                    "authority_notes": "engine=0.2.0-ambiguity; lexicon=min-v0.2",
                    "disputed_alternatives": []
                },
                "score": 0.95
            }
        ],
        "rejected": [
            {
                "parse": [
                    {"surface": "rājaputraḥ", "stem": "rājaputra", "role": "subanta:prathama"}
                ],
                "reason_code": "UNATTESTED_STEM",
                "violated_sutra": None
            }
        ],
        "engine_version": "1.0.8-adapter"
    }

    errors = list(validator.iter_errors(real_response))
    assert not errors, f"Real envelope failed contract: {[e.message for e in errors]}"


def test_contract_rejects_missing_authority_recension():
    """Ensures the schema enforces authority.recension."""
    contract_schema = load_json(SCHEMAS_DIR / "sanskrit_contract.schema.json")
    registry = build_registry()
    validator = jsonschema.Draft202012Validator(contract_schema, registry=registry)

    bad = {
        "input_triad": {"devanagari": "अ", "iast": "a", "slp1": "a"},
        "candidates": [{
            "candidate_id": "cand_01",
            "parse": [{"surface": "a", "stem": "a", "role": "root"}],
            "sutra_chain": ["1.1.1"],
            "authority": {"primary_source": "Aṣṭādhyāyī 1.1.1"},  # ← missing recension
            "score": 0.9
        }],
        "rejected": [],
        "engine_version": "test"
    }

    errors = list(validator.iter_errors(bad))
    assert errors, "Schema must reject missing authority.recension"