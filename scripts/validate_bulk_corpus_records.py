import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

EXPECTED_SCHEMA = "sanskrit-bulk-corpus-staging.v1"
MAX_RECORDS = 2000
ALLOWED_TYPES = {"dhatu", "sutra", "stotra"}


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_records(data):
    for batch_index, batch in enumerate(data.get("batches", [])):
        if not isinstance(batch, dict):
            continue

        batch_id = batch.get("batchId") or f"batch-{batch_index}"

        for record_index, record in enumerate(batch.get("records", [])):
            if isinstance(record, dict):
                yield batch_id, record_index, record


def validate_record(batch_id, record_index, record):
    errors = []

    record_id = str(record.get("id") or "").strip()
    record_type = str(record.get("type") or "").strip()
    text = str(record.get("text") or "").strip()
    source = str(record.get("source") or "").strip()

    if not record_id:
        errors.append(f"{batch_id}:{record_index}:missingId")

    if record_type not in ALLOWED_TYPES:
        errors.append(f"{batch_id}:{record_index}:invalidType")

    if not text:
        errors.append(f"{batch_id}:{record_index}:missingText")

    if not source:
        errors.append(f"{batch_id}:{record_index}:missingSource")

    return errors


def validate_bulk_corpus_records(data):
    errors = []

    if data.get("schemaVersion") != EXPECTED_SCHEMA:
        errors.append("schemaVersion")

    if data.get("mode") != "preview-only":
        errors.append("mode")

    if data.get("canonicalWriteAllowed") is not False:
        errors.append("canonicalWriteAllowed")

    batches = data.get("batches")
    if not isinstance(batches, list):
        errors.append("batches")
        batches = []

    record_ids = []
    record_count = 0

    for batch_id, record_index, record in iter_records({"batches": batches}):
        record_count += 1
        record_id = str(record.get("id") or "").strip()
        if record_id:
            record_ids.append(record_id)

        errors.extend(validate_record(batch_id, record_index, record))

    seen = set()
    duplicate_ids = []

    for record_id in record_ids:
        if record_id in seen and record_id not in duplicate_ids:
            duplicate_ids.append(record_id)
        seen.add(record_id)

    if duplicate_ids:
        errors.append("duplicateRecordIds")

    if record_count > MAX_RECORDS:
        errors.append("recordLimitExceeded")

    readiness_score = 100 if not errors else max(0, 100 - len(errors) * 5)

    return {
        "valid": not errors,
        "errors": errors,
        "duplicateIds": duplicate_ids,
        "recordCount": record_count,
        "maxRecords": MAX_RECORDS,
        "readinessScore": readiness_score,
        "previewOnly": True,
        "readOnly": True,
        "canonicalWriteAllowed": False
    }


def main():
    result = validate_bulk_corpus_records(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())