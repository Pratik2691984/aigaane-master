import json
from pathlib import Path

from plan_bulk_corpus_allocation import plan_bulk_corpus_allocation


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_manifest.v1.json"

DEFAULT_RESERVATION = {
    "dhatu": 1400,
    "sutra": 400,
    "stotra": 200
}


def load_manifest():
    with MANIFEST.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def reserve_bulk_corpus_capacity(data):
    allocation = plan_bulk_corpus_allocation(data)

    reservations = {}
    warnings = []
    errors = []

    for record_type, requested in DEFAULT_RESERVATION.items():
        allocation_item = allocation.get("allocation", {}).get(record_type, {})
        available = int(allocation_item.get("remaining", 0))
        reserved = min(requested, available)

        if requested > available:
            warnings.append(f"{record_type}:reservationLimited")

        reservations[record_type] = {
            "requested": requested,
            "available": available,
            "reserved": reserved,
            "unreserved": max(0, requested - reserved)
        }

    total_reserved = sum(item["reserved"] for item in reservations.values())
    total_requested = sum(item["requested"] for item in reservations.values())
    total_unreserved = sum(item["unreserved"] for item in reservations.values())

    valid = (
        allocation.get("valid") is True
        and not errors
        and allocation.get("canonicalWriteAllowed") is False
        and allocation.get("allocationWriteAllowed") is False
    )

    return {
        "valid": valid,
        "reservations": reservations,
        "totalRequested": total_requested,
        "totalReserved": total_reserved,
        "totalUnreserved": total_unreserved,
        "warnings": warnings,
        "errors": errors,
        "allocation": allocation,
        "previewOnly": True,
        "readOnly": True,
        "reservationWriteAllowed": False,
        "allocationWriteAllowed": False,
        "executionAllowed": False,
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False
    }


def main():
    result = reserve_bulk_corpus_capacity(load_manifest())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())