import json
from pathlib import Path

from plan_bulk_corpus_schedule import plan_bulk_corpus_schedule


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_bulk_corpus_timeline(data):
    schedule_plan = plan_bulk_corpus_schedule(data)
    schedule = schedule_plan.get("schedule", [])

    timeline = []

    for item in schedule:
        timeline.append({
            "timelineId": f"timeline-{item.get('windowOrder', 0):03d}",
            "scheduleId": item.get("scheduleId"),
            "windowId": item.get("windowId"),
            "order": item.get("windowOrder"),
            "recordCount": item.get("recordCount"),
            "startSecond": item.get("startSecond"),
            "endSecond": item.get("endSecond"),
            "durationSecond": round(
                float(item.get("endSecond", 0)) - float(item.get("startSecond", 0)),
                3
            ),
            "completionPercent": item.get("completionPercent"),
            "previewOnly": True
        })

    valid = (
        schedule_plan.get("valid") is True
        and schedule_plan.get("scheduleExecutionAllowed") is False
        and schedule_plan.get("canonicalWriteAllowed") is False
    )

    return {
        "valid": valid,
        "timelineCount": len(timeline),
        "timeline": timeline,
        "totalEstimatedSeconds": schedule_plan.get("totalEstimatedSeconds", 0),
        "finalCompletionPercent": timeline[-1]["completionPercent"] if timeline else 0,
        "schedulePlan": schedule_plan,
        "previewOnly": True,
        "readOnly": True,
        "timelineExecutionAllowed": False,
        "scheduleExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = build_bulk_corpus_timeline(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())