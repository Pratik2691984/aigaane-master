import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

EXPECTED_SCHEMA = "sanskrit-bulk-corpus-staging.v1"
MAX_RECORDS = 2000


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_manifest(data):
    errors = []

    if data.get("schemaVersion") != EXPECTED_SCHEMA:
        errors.append("schemaVersion")

    if data.get("mode") != "preview-only":
        errors.append("mode")

    if data.get("canonicalWriteAllowed") is not False:
        errors.append("canonicalWriteAllowed")

    if data.get("maxRecords") != MAX_RECORDS:
        errors.append("maxRecords")

    batches = data.get("batches")
    if not isinstance(batches, list):
        errors.append("batches")
        batches = []

    seen_ids = set()
    total_records = 0

    for batch in batches:
        if not isinstance(batch, dict):
            errors.append("batch")
            continue

        batch_id = batch.get("batchId")
        if not batch_id:
            errors.append("batchId")
        elif batch_id in seen_ids:
            errors.append(f"duplicateBatchId:{batch_id}")
        else:
            seen_ids.add(batch_id)

        records = batch.get("records", [])
        if not isinstance(records, list):
            errors.append(f"records:{batch_id}")
            continue

        total_records += len(records)

    if total_records > MAX_RECORDS:
        errors.append("recordLimitExceeded")

    return {
        "valid": not errors,
        "errors": errors,
        "batchCount": len(batches),
        "recordCount": total_records,
        "canonicalWriteAllowed": False,
        "previewOnly": True
    }


def main():
    result = validate_manifest(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())