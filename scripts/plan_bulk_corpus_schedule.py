import json
from pathlib import Path

from plan_bulk_corpus_windows import plan_bulk_corpus_windows


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

SECONDS_PER_WINDOW = 12.5


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def plan_bulk_corpus_schedule(data):
    window_plan = plan_bulk_corpus_windows(data)
    windows = window_plan.get("windows", [])

    schedule = []
    elapsed = 0.0

    for window in windows:
        start = round(elapsed, 3)
        elapsed += SECONDS_PER_WINDOW
        end = round(elapsed, 3)

        schedule.append({
            "scheduleId": f"schedule-{window.get('windowOrder', 0):03d}",
            "windowId": window.get("windowId"),
            "windowOrder": window.get("windowOrder"),
            "recordCount": window.get("recordCount"),
            "startSecond": start,
            "endSecond": end,
            "completionPercent": round((window.get("windowOrder", 0) / len(windows)) * 100, 3) if windows else 0,
            "previewOnly": True
        })

    valid = (
        window_plan.get("valid") is True
        and window_plan.get("windowExecutionAllowed") is False
        and window_plan.get("canonicalWriteAllowed") is False
    )

    return {
        "valid": valid,
        "scheduleCount": len(schedule),
        "schedule": schedule,
        "totalEstimatedSeconds": round(elapsed, 3),
        "secondsPerWindow": SECONDS_PER_WINDOW,
        "windowPlan": window_plan,
        "previewOnly": True,
        "readOnly": True,
        "scheduleExecutionAllowed": False,
        "windowExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = plan_bulk_corpus_schedule(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())