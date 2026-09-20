import json
from pathlib import Path

from prepare_bulk_corpus_intake import prepare_bulk_corpus_intake


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

DEFAULT_BATCH_SIZE = 250
DEFAULT_SECONDS_PER_RECORD = 0.05


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_bulk_corpus_intake_queue(data):
    intake = prepare_bulk_corpus_intake(data, DEFAULT_BATCH_SIZE)

    queue_items = []
    sequence = 0

    for batch in intake.get("intakeBatches", []):
        for record in batch.get("records", []):
            sequence += 1
            queue_items.append({
                "queueId": f"queue-{sequence:04d}",
                "queueOrder": sequence,
                "intakeBatchId": batch.get("intakeBatchId"),
                "intakeId": record.get("intakeId"),
                "recordId": record.get("recordId"),
                "type": record.get("type"),
                "previewOnly": True
            })

    estimated_seconds = round(
        len(queue_items) * DEFAULT_SECONDS_PER_RECORD,
        3
    )

    valid = (
        intake.get("valid") is True
        and intake.get("importAllowed") is False
        and intake.get("canonicalWriteAllowed") is False
    )

    return {
        "valid": valid,
        "queueItemCount": len(queue_items),
        "queueItems": queue_items,
        "intake": intake,
        "estimatedSeconds": estimated_seconds,
        "secondsPerRecord": DEFAULT_SECONDS_PER_RECORD,
        "previewOnly": True,
        "readOnly": True,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "queueExecutionAllowed": False
    }


def main():
    result = build_bulk_corpus_intake_queue(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())