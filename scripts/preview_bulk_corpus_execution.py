import json
from pathlib import Path

from build_bulk_corpus_intake_queue import build_bulk_corpus_intake_queue


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

DEFAULT_SECONDS_PER_RECORD = 0.05


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def preview_bulk_corpus_execution(data):
    queue = build_bulk_corpus_intake_queue(data)
    queue_items = queue.get("queueItems", [])

    timeline = []
    elapsed = 0.0

    for item in queue_items:
        start = round(elapsed, 3)
        elapsed += DEFAULT_SECONDS_PER_RECORD
        end = round(elapsed, 3)

        timeline.append({
            "queueId": item.get("queueId"),
            "queueOrder": item.get("queueOrder"),
            "recordId": item.get("recordId"),
            "type": item.get("type"),
            "startSecond": start,
            "endSecond": end,
            "previewOnly": True
        })

    estimated_seconds = round(elapsed, 3)
    throughput = (
        round(len(queue_items) / estimated_seconds, 3)
        if estimated_seconds > 0
        else 0
    )

    valid = (
        queue.get("valid") is True
        and queue.get("queueExecutionAllowed") is False
        and queue.get("canonicalWriteAllowed") is False
    )

    return {
        "valid": valid,
        "queueItemCount": len(queue_items),
        "timeline": timeline,
        "estimatedSeconds": estimated_seconds,
        "estimatedThroughputPerSecond": throughput,
        "queue": queue,
        "previewOnly": True,
        "readOnly": True,
        "executionAllowed": False,
        "queueExecutionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = preview_bulk_corpus_execution(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())