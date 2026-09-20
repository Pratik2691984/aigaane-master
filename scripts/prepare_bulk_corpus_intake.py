import json
from pathlib import Path

from preview_bulk_corpus_import import preview_bulk_corpus_import


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

MAX_RECORDS = 2000
DEFAULT_BATCH_SIZE = 250


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


def prepare_bulk_corpus_intake(data, batch_size=DEFAULT_BATCH_SIZE):
    preview = preview_bulk_corpus_import(data)
    records = list(iter_records(data))

    intake_records = []
    skipped_records = []

    seen = set()

    for sequence, (source_batch_id, record_index, record) in enumerate(records):
        record_id = str(record.get("id") or "").strip()

        intake_id = f"intake-{sequence + 1:04d}"

        item = {
            "intakeId": intake_id,
            "sourceBatchId": source_batch_id,
            "sourceRecordIndex": record_index,
            "recordId": record_id,
            "type": str(record.get("type") or "").strip(),
            "previewOnly": True
        }

        if not record_id:
            item["skipReason"] = "missingId"
            skipped_records.append(item)
            continue

        if record_id in seen:
            item["skipReason"] = "duplicateId"
            skipped_records.append(item)
            continue

        seen.add(record_id)
        intake_records.append(item)

    intake_batches = []
    for start in range(0, len(intake_records), batch_size):
        part = intake_records[start:start + batch_size]
        intake_batches.append({
            "intakeBatchId": f"intake-batch-{len(intake_batches) + 1:03d}",
            "startIndex": start,
            "recordCount": len(part),
            "records": part
        })

    valid = (
        preview.get("valid") is True
        and len(records) <= MAX_RECORDS
    )

    return {
        "valid": valid,
        "sourceRecordCount": len(records),
        "intakeRecordCount": len(intake_records),
        "skippedRecordCount": len(skipped_records),
        "intakeBatchCount": len(intake_batches),
        "intakeBatches": intake_batches,
        "skippedRecords": skipped_records,
        "preview": preview,
        "batchSize": batch_size,
        "maxRecords": MAX_RECORDS,
        "previewOnly": True,
        "readOnly": True,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = prepare_bulk_corpus_intake(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())