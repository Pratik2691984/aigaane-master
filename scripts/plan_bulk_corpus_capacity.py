import json
from pathlib import Path

from preview_bulk_corpus_execution import preview_bulk_corpus_execution


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

MAX_RECORDS = 2000
DEFAULT_BATCH_SIZE = 250


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def plan_bulk_corpus_capacity(data):
    execution = preview_bulk_corpus_execution(data)
    record_count = int(execution.get("queueItemCount", 0))

    remaining_capacity = max(0, MAX_RECORDS - record_count)
    utilization_percent = round((record_count / MAX_RECORDS) * 100, 3)

    projected_batch_count = (
        (record_count + DEFAULT_BATCH_SIZE - 1) // DEFAULT_BATCH_SIZE
        if record_count else 0
    )

    valid = (
        execution.get("valid") is True
        and record_count <= MAX_RECORDS
        and execution.get("canonicalWriteAllowed") is False
        and execution.get("executionAllowed") is False
    )

    return {
        "valid": valid,
        "recordCount": record_count,
        "maxRecords": MAX_RECORDS,
        "remainingCapacity": remaining_capacity,
        "utilizationPercent": utilization_percent,
        "defaultBatchSize": DEFAULT_BATCH_SIZE,
        "projectedBatchCount": projected_batch_count,
        "execution": execution,
        "previewOnly": True,
        "readOnly": True,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = plan_bulk_corpus_capacity(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())