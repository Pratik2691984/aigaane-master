"""
Node 38C: Bulk Corpus Promotion Certification Assurance
Independent read-only check that the 38B certification packet is consistent
and is not an execution / promotion / import / canonical-write authorization.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
CERT_PATH = (
    ROOT_DIR / "data" / "sanskrit" / "corpus-staging" / "bulk_corpus_certification.v1.json"
)
OUTPUT_PATH = (
    ROOT_DIR
    / "data"
    / "sanskrit"
    / "corpus-staging"
    / "bulk_corpus_certification_assurance.v1.json"
)

EXPECTED_TOTAL = 2000
EXPECTED_SCHEMA = "sanskrit-bulk-corpus-certification.v1"
EXPECTED_STATUS = "certified-read-only"

LOCKED_FALSE = (
    "canonicalWriteAllowed",
    "promotionAllowed",
    "importAllowed",
    "executionAllowed",
    "certificationExecutionAllowed",
)
LOCKED_TRUE = ("previewOnly", "readOnly")


def _failures(packet: Dict[str, Any]) -> List[str]:
    found: List[str] = []
    if packet.get("schemaVersion") != EXPECTED_SCHEMA:
        found.append("schemaVersion-mismatch")
    if packet.get("status") != EXPECTED_STATUS:
        found.append("status-mismatch")

    invariants = packet.get("invariants") or {}
    guarantees = packet.get("guarantees") or {}
    target = packet.get("targetCorpus") or {}

    if invariants.get("acceptedRecords") != EXPECTED_TOTAL:
        found.append("acceptedRecords-mismatch")
    if invariants.get("rejectedRecords") != 0:
        found.append("rejectedRecords-nonzero")
    if target.get("totalCount") != EXPECTED_TOTAL:
        found.append("target-total-mismatch")
    if target.get("dhatuCount") != 1400:
        found.append("dhatu-count-mismatch")
    if target.get("sutraCount") != 400:
        found.append("sutra-count-mismatch")
    if target.get("stotraCount") != 200:
        found.append("stotra-count-mismatch")

    for key in LOCKED_TRUE:
        if packet.get(key) is not True:
            found.append(f"{key}-not-true")
    for key in LOCKED_FALSE:
        if packet.get(key) is not False:
            found.append(f"{key}-not-false")

    if invariants.get("canonicalWriteEnabled") is not False:
        found.append("canonicalWriteEnabled-exposed")
    if invariants.get("promotionExecutionEnabled") is not False:
        found.append("promotionExecutionEnabled-exposed")
    if invariants.get("importExecutionEnabled") is not False:
        found.append("importExecutionEnabled-exposed")
    if invariants.get("unsafeWriteRefused") is not True:
        found.append("unsafeWriteRefused-missing")

    for key in ("noMutationPaths", "noCanonicalWrites", "noImports", "noPromotions"):
        if guarantees.get(key) is not True:
            found.append(f"guarantee-{key}-failed")

    return found


def build_assurance_record(packet: Dict[str, Any]) -> Dict[str, Any]:
    failures = _failures(packet)
    assured = len(failures) == 0
    return {
        "schemaVersion": "sanskrit-bulk-corpus-certification-assurance.v1",
        "status": "assurance-ready" if assured else "assurance-blocked",
        "mode": "preview-only",
        "previewOnly": True,
        "readOnly": True,
        "assured": assured,
        "hardStop": True,
        "authorization": {
            "certificationIsAuthorization": False,
            "canonicalWrite": False,
            "promotion": False,
            "import": False,
            "execution": False,
        },
        "checked": {
            "acceptedRecords": (packet.get("invariants") or {}).get("acceptedRecords"),
            "rejectedRecords": (packet.get("invariants") or {}).get("rejectedRecords"),
            "schemaVersion": packet.get("schemaVersion"),
            "status": packet.get("status"),
        },
        "failures": failures,
        "nextGate": "MANUAL REVIEW / CERTIFIED",
        "canonicalWriteAllowed": False,
        "promotionAllowed": False,
        "importAllowed": False,
        "executionAllowed": False,
        "assuranceExecutionAllowed": False,
        "certificationExecutionAllowed": False,
    }


def main() -> int:
    if not CERT_PATH.exists():
        raise FileNotFoundError(f"Missing 38B packet: {CERT_PATH}")
    with CERT_PATH.open("r", encoding="utf-8") as handle:
        packet = json.load(handle)
    record = build_assurance_record(packet)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"written": str(OUTPUT_PATH), "status": record["status"], "assured": record["assured"]}, indent=2))
    return 0 if record["assured"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
