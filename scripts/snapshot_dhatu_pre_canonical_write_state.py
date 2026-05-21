#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import ROOT


DEFAULT_RELEASE_VERIFICATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_release_verification.v1.json"
)
DEFAULT_RELEASE_CHECKLIST_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_release_checklist.v1.json"
)
DEFAULT_DRY_RUN_DIFF_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_dry_run_diff.v1.json"
DEFAULT_COMMAND_MANIFEST_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_command_manifest.v1.json"
)
DEFAULT_APPROVAL_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval.v1.json"
DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_SNAPSHOT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_preflight_snapshot.v1.json"


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def display_path(path: Any) -> str:
    resolved = resolve_path(path)
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Preflight snapshot source must be a JSON object.")
    return payload


def git_value(args: List[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return "UNKNOWN"


def file_sha256(path: Any) -> str:
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def snapshot_status(safe_to_proceed: bool) -> str:
    return "READY_PREWRITE" if safe_to_proceed else "BLOCKED_PREWRITE"


def build_preflight_snapshot(canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH) -> Dict[str, Any]:
    verification = load_json(DEFAULT_RELEASE_VERIFICATION_PATH)
    checklist = load_json(DEFAULT_RELEASE_CHECKLIST_PATH)
    dry_run_diff = load_json(DEFAULT_DRY_RUN_DIFF_PATH)
    command_manifest = load_json(DEFAULT_COMMAND_MANIFEST_PATH)
    approval = load_json(DEFAULT_APPROVAL_PATH)
    readiness_lock = load_json(DEFAULT_READINESS_LOCK_PATH)
    registry = load_json(canonical_registry_path)
    registry_count = len(registry.get("records", {}))
    safe_to_proceed = verification.get("safeToProceed") is True and checklist.get("safeToWriteProduction") is True
    current_head = git_value(["rev-parse", "HEAD"])
    current_branch = git_value(["branch", "--show-current"])
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/snapshot_dhatu_pre_canonical_write_state.py",
        "snapshotStatus": snapshot_status(safe_to_proceed),
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "currentGitHead": current_head,
        "currentBranch": current_branch,
        "canonicalRegistryPath": display_path(canonical_registry_path),
        "canonicalRegistryRecordCount": registry_count,
        "canonicalRegistrySha256": file_sha256(canonical_registry_path),
        "approvalStatus": approval.get("approvalStatus"),
        "approvalValid": checklist.get("gateSummary", {}).get("approvalValid") is True,
        "commandStatus": command_manifest.get("commandStatus"),
        "verificationStatus": verification.get("verificationStatus"),
        "safeToProceed": safe_to_proceed,
        "readyRecordIds": sorted(readiness_lock.get("readyRecordIds", [])),
        "recordsToAdd": dry_run_diff.get("recordsToAdd", []),
        "rollbackReference": {
            "gitHead": current_head,
            "branch": current_branch,
            "canonicalRegistryPath": display_path(canonical_registry_path),
            "canonicalRegistrySha256": file_sha256(canonical_registry_path),
            "canonicalRegistryRecordCount": registry_count,
        },
        "blockingReasons": list(
            dict.fromkeys(
                verification.get("blockingReasons", [])
                + checklist.get("blockingReasons", [])
                + dry_run_diff.get("refusalReasons", [])
            )
        ),
    }


def write_preflight_snapshot(snapshot: Dict[str, Any], path: Any = DEFAULT_SNAPSHOT_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path


def build_summary(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "snapshotStatus": snapshot["snapshotStatus"],
        "safeToProceed": snapshot["safeToProceed"],
        "canonicalRegistryRecordCount": snapshot["canonicalRegistryRecordCount"],
        "blockingReasonCount": len(snapshot["blockingReasons"]),
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snapshot pre-canonical-write state without mutation.")
    parser.add_argument("--canonical-registry", default=str(DEFAULT_CANONICAL_REGISTRY_PATH))
    parser.add_argument("--output", default=str(DEFAULT_SNAPSHOT_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        snapshot = build_preflight_snapshot(args.canonical_registry)
        write_preflight_snapshot(snapshot, args.output)
        print(json.dumps(build_summary(snapshot), ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu pre-canonical-write snapshot failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
