#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import ROOT


DEFAULT_AUTHORIZATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_authorization.v1.json"
)
DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
DEFAULT_SIMULATED_APPROVAL_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval.simulated.v1.json"
)


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Simulated approval source must be a JSON object.")
    return payload


def build_simulated_approval(
    authorization_path: Any = DEFAULT_AUTHORIZATION_PATH,
    readiness_lock_path: Any = DEFAULT_READINESS_LOCK_PATH,
) -> Dict[str, Any]:
    authorization = load_json(authorization_path)
    readiness_lock = load_json(readiness_lock_path)
    authorized_ids = sorted(authorization.get("authorizedRecordIds", []))
    ready_ids = sorted(readiness_lock.get("readyRecordIds", []))
    if authorized_ids != ready_ids:
        raise ValueError("Authorized record ids must match readiness-lock ready ids for simulation.")
    return {
        "schemaVersion": "1.0.0",
        "approvalStatus": "APPROVED",
        "approvedBy": "test-fixture",
        "approvedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "approvedRecordIds": authorized_ids,
        "approvalNotes": "Test-only approval fixture for validating the approval chain without production writes.",
        "requiredBeforeWrite": [
            "This simulated approval must never replace canonical_write_approval.v1.json.",
            "Use only with explicit test validation and command-manifest paths.",
            "Production canonical writes still require human approval and manual environment guards.",
        ],
        "testOnly": True,
    }


def write_simulated_approval(approval: Dict[str, Any], path: Any = DEFAULT_SIMULATED_APPROVAL_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(approval, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(approval: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "approvalStatus": approval["approvalStatus"],
        "approvedCount": len(approval["approvedRecordIds"]),
        "approvedBy": approval["approvedBy"],
        "testOnly": approval["testOnly"],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a test-only canonical write approval fixture.")
    parser.add_argument("--authorization", default=str(DEFAULT_AUTHORIZATION_PATH))
    parser.add_argument("--readiness-lock", default=str(DEFAULT_READINESS_LOCK_PATH))
    parser.add_argument("--output", default=str(DEFAULT_SIMULATED_APPROVAL_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        approval = build_simulated_approval(args.authorization, args.readiness_lock)
        write_simulated_approval(approval, args.output)
        print(json.dumps(build_summary(approval), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu canonical write approval simulation failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
