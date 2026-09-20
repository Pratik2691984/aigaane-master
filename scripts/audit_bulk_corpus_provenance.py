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

        batch_id = str(batch.get("batchId") or f"batch-{batch_index}")

        for record_index, record in enumerate(batch.get("records", [])):
            if isinstance(record, dict):
                yield batch_id, record_index, record


def audit_bulk_corpus_provenance(data):
    errors = []
    warnings = []

    if data.get("schemaVersion") != EXPECTED_SCHEMA:
        errors.append("schemaVersion")

    if data.get("mode") != "preview-only":
        errors.append("mode")

    if data.get("canonicalWriteAllowed") is not False:
        errors.append("canonicalWriteAllowed")

    record_ids = []
    sources = []
    batch_ids = []
    record_count = 0
    type_counts = {
        "dhatu": 0,
        "sutra": 0,
        "stotra": 0
    }

    batches = data.get("batches", [])
    if not isinstance(batches, list):
        errors.append("batches")
        batches = []

    for index, batch in enumerate(batches):
        if not isinstance(batch, dict):
            errors.append(f"batch:{index}:invalid")
            continue

        batch_id = str(batch.get("batchId") or "").strip()
        if not batch_id:
            errors.append(f"batch:{index}:missingBatchId")
        else:
            batch_ids.append(batch_id)

    duplicate_batch_ids = sorted({
        batch_id for batch_id in batch_ids if batch_ids.count(batch_id) > 1
    })

    for batch_id, record_index, record in iter_records({"batches": batches}):
        record_count += 1

        record_id = str(record.get("id") or "").strip()
        record_type = str(record.get("type") or "").strip()
        source = str(record.get("source") or "").strip()
        text = str(record.get("text") or "").strip()

        if record_id:
            record_ids.append(record_id)
        else:
            errors.append(f"{batch_id}:{record_index}:missingId")

        if record_type in ALLOWED_TYPES:
            type_counts[record_type] += 1
        else:
            errors.append(f"{batch_id}:{record_index}:invalidType")

        if source:
            sources.append(source)
        else:
            errors.append(f"{batch_id}:{record_index}:missingSource")

        if not text:
            errors.append(f"{batch_id}:{record_index}:missingText")

    duplicate_record_ids = sorted({
        record_id for record_id in record_ids if record_ids.count(record_id) > 1
    })

    duplicate_sources = sorted({
        source for source in sources if sources.count(source) > 1
    })

    if duplicate_record_ids:
        errors.append("duplicateRecordIds")

    if duplicate_batch_ids:
        errors.append("duplicateBatchIds")

    if record_count > MAX_RECORDS:
        errors.append("recordLimitExceeded")

    if duplicate_sources:
        warnings.append("reusedSources")

    confidence_score = 100
    confidence_score -= len(errors) * 7
    confidence_score -= len(warnings) * 3
    confidence_score = max(0, confidence_score)

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "duplicateRecordIds": duplicate_record_ids,
        "duplicateBatchIds": duplicate_batch_ids,
        "reusedSources": duplicate_sources,
        "recordCount": record_count,
        "batchCount": len(batches),
        "typeCounts": type_counts,
        "confidenceScore": confidence_score,
        "previewOnly": True,
        "readOnly": True,
        "canonicalWriteAllowed": False
    }


def main():
    result = audit_bulk_corpus_provenance(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())