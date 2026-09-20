import json
from pathlib import Path

from compute_bulk_corpus_readiness import compute_bulk_corpus_readiness


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_records(data):
    for batch in data.get("batches", []):
        if not isinstance(batch, dict):
            continue

        for record in batch.get("records", []):
            if isinstance(record, dict):
                yield record


def preview_bulk_corpus_import(data):
    readiness = compute_bulk_corpus_readiness(data)
    records = list(iter_records(data))

    seen = set()
    duplicate_ids = set()
    inserted_count = 0
    skipped_count = 0

    type_counts = {
        "dhatu": 0,
        "sutra": 0,
        "stotra": 0
    }

    estimated_bytes = 0

    for record in records:
        record_id = str(record.get("id") or "").strip()
        record_type = str(record.get("type") or "").strip()

        estimated_bytes += len(
            json.dumps(record, ensure_ascii=False).encode("utf-8")
        )

        if record_type in type_counts:
            type_counts[record_type] += 1

        if not record_id:
            skipped_count += 1
            continue

        if record_id in seen:
            duplicate_ids.add(record_id)
            skipped_count += 1
            continue

        seen.add(record_id)
        inserted_count += 1

    preview_valid = (
        readiness.get("valid") is True
        and readiness.get("promotionEligible") is True
        and not duplicate_ids
    )

    return {
        "valid": preview_valid,
        "readiness": readiness,
        "recordCount": len(records),
        "estimatedInsertCount": inserted_count,
        "estimatedSkipCount": skipped_count,
        "duplicateIds": sorted(duplicate_ids),
        "typeCounts": type_counts,
        "estimatedBytes": estimated_bytes,
        "estimatedKilobytes": round(estimated_bytes / 1024, 3),
        "previewOnly": True,
        "readOnly": True,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = preview_bulk_corpus_import(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())