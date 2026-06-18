import json
from pathlib import Path

from validate_bulk_corpus_staging import validate_manifest
from validate_bulk_corpus_records import validate_bulk_corpus_records
from audit_bulk_corpus_provenance import audit_bulk_corpus_provenance


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def compute_bulk_corpus_readiness(data):
    staging = validate_manifest(data)
    validator = validate_bulk_corpus_records(data)
    provenance = audit_bulk_corpus_provenance(data)

    errors = []
    warnings = []

    errors.extend([f"staging:{error}" for error in staging.get("errors", [])])
    errors.extend([f"validator:{error}" for error in validator.get("errors", [])])
    errors.extend([f"provenance:{error}" for error in provenance.get("errors", [])])

    warnings.extend([
        f"provenance:{warning}"
        for warning in provenance.get("warnings", [])
    ])

    record_count = max(
        staging.get("recordCount", 0),
        validator.get("recordCount", 0),
        provenance.get("recordCount", 0)
    )

    readiness_score = min(
        staging.get("recordCount", 0) <= 2000 and 100 or 0,
        validator.get("readinessScore", 0),
        provenance.get("confidenceScore", 0)
    )

    promotion_eligible = (
        not errors
        and staging.get("previewOnly") is True
        and validator.get("previewOnly") is True
        and provenance.get("previewOnly") is True
        and record_count <= 2000
    )

    return {
        "valid": not errors,
        "promotionEligible": promotion_eligible,
        "readinessScore": readiness_score,
        "recordCount": record_count,
        "batchCount": provenance.get("batchCount", staging.get("batchCount", 0)),
        "errors": errors,
        "warnings": warnings,
        "staging": staging,
        "validator": validator,
        "provenance": provenance,
        "previewOnly": True,
        "readOnly": True,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False
    }


def main():
    result = compute_bulk_corpus_readiness(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())