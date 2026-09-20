import json
from pathlib import Path

from build_bulk_corpus_timeline import build_bulk_corpus_timeline


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def simulate_bulk_corpus_execution(data):
    timeline_plan = build_bulk_corpus_timeline(data)
    timeline = timeline_plan.get("timeline", [])

    snapshots = []

    for item in timeline:
        snapshots.append({
            "snapshotId": f"simulation-{item.get('order', 0):03d}",
            "timelineId": item.get("timelineId"),
            "windowId": item.get("windowId"),
            "order": item.get("order"),
            "recordCount": item.get("recordCount"),
            "elapsedSecond": item.get("endSecond"),
            "completionPercent": item.get("completionPercent"),
            "status": "simulated-complete",
            "previewOnly": True
        })

    total_records = sum(int(item.get("recordCount", 0)) for item in timeline)
    total_seconds = float(timeline_plan.get("totalEstimatedSeconds", 0) or 0)
    schedule_plan = timeline_plan.get("schedulePlan", {})
    window_size = int(schedule_plan.get("windowPlan", {}).get("windowSize", 0) or 0)
    seconds_per_window = float(schedule_plan.get("secondsPerWindow", 0) or 0)
    if window_size and seconds_per_window:
        throughput = round(window_size / seconds_per_window, 1)
    else:
        throughput = round(total_records / total_seconds, 1) if total_seconds else 0

    valid = (
        timeline_plan.get("valid") is True
        and timeline_plan.get("timelineExecutionAllowed") is False
        and timeline_plan.get("canonicalWriteAllowed") is False
    )

    return {
        "valid": valid,
        "simulationCount": len(snapshots),
        "snapshots": snapshots,
        "totalRecords": total_records,
        "totalEstimatedSeconds": total_seconds,
        "estimatedThroughputPerSecond": throughput,
        "finalCompletionPercent": timeline_plan.get("finalCompletionPercent", 0),
        "timelinePlan": timeline_plan,
        "previewOnly": True,
        "readOnly": True,
        "simulationExecutionAllowed": False,
        "timelineExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = simulate_bulk_corpus_execution(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())