import json
from pathlib import Path

from reserve_bulk_corpus_capacity import reserve_bulk_corpus_capacity


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

DEFAULT_WINDOW_SIZE = 250


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def plan_bulk_corpus_windows(data, window_size=DEFAULT_WINDOW_SIZE):
    reservation = reserve_bulk_corpus_capacity(data)
    total_reserved = int(reservation.get("totalReserved", 0))

    windows = []
    start = 0

    while start < total_reserved:
        end = min(start + window_size, total_reserved)
        windows.append({
            "windowId": f"window-{len(windows) + 1:03d}",
            "windowOrder": len(windows) + 1,
            "startIndex": start,
            "endIndex": end,
            "recordCount": end - start,
            "previewOnly": True
        })
        start = end

    valid = (
        reservation.get("valid") is True
        and reservation.get("canonicalWriteAllowed") is False
        and reservation.get("promotionAllowed") is False
    )

    return {
        "valid": valid,
        "windowSize": window_size,
        "windowCount": len(windows),
        "totalReserved": total_reserved,
        "windows": windows,
        "reservation": reservation,
        "previewOnly": True,
        "readOnly": True,
        "windowExecutionAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = plan_bulk_corpus_windows(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())