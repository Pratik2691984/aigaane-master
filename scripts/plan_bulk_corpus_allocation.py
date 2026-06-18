import json
from pathlib import Path

from plan_bulk_corpus_capacity import plan_bulk_corpus_capacity


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

MAX_RECORDS = 2000
DEFAULT_ALLOCATION = {
    "dhatu": 1400,
    "sutra": 400,
    "stotra": 200
}


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


def plan_bulk_corpus_allocation(data):
    capacity = plan_bulk_corpus_capacity(data)

    type_counts = {
        "dhatu": 0,
        "sutra": 0,
        "stotra": 0
    }

    for record in iter_records(data):
        record_type = str(record.get("type") or "").strip()
        if record_type in type_counts:
            type_counts[record_type] += 1

    allocation = {}
    warnings = []
    errors = []

    for record_type, quota in DEFAULT_ALLOCATION.items():
        used = type_counts[record_type]
        remaining = max(0, quota - used)
        exceeded = used > quota

        if exceeded:
            warnings.append(f"{record_type}:quotaExceeded")

        allocation[record_type] = {
            "quota": quota,
            "used": used,
            "remaining": remaining,
            "exceeded": exceeded
        }

    total_reserved = sum(DEFAULT_ALLOCATION.values())
    total_used = sum(type_counts.values())
    free_capacity = max(0, MAX_RECORDS - total_used)

    if total_reserved > MAX_RECORDS:
        errors.append("allocationExceedsCapacity")

    valid = (
        capacity.get("valid") is True
        and not errors
        and capacity.get("canonicalWriteAllowed") is False
    )

    return {
        "valid": valid,
        "allocation": allocation,
        "typeCounts": type_counts,
        "totalReserved": total_reserved,
        "totalUsed": total_used,
        "maxRecords": MAX_RECORDS,
        "freeCapacity": free_capacity,
        "warnings": warnings,
        "errors": errors,
        "capacity": capacity,
        "previewOnly": True,
        "readOnly": True,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "allocationWriteAllowed": False
    }


def main():
    result = plan_bulk_corpus_allocation(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())