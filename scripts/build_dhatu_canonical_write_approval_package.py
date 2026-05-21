#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from validate_large_scale_ingestion import ROOT


DEFAULT_RELEASE_CHECKLIST_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_release_checklist.v1.json"
)
DEFAULT_DRY_RUN_DIFF_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_dry_run_diff.v1.json"
DEFAULT_AUTHORIZATION_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_authorization.v1.json"
)
DEFAULT_READINESS_LOCK_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "promotion_readiness_lock.v1.json"
DEFAULT_EVIDENCE_REPORT_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "dhatu_promotion_evidence_report.v1.json"
)
DEFAULT_APPROVAL_PACKAGE_PATH = (
    ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_approval_package.v1.md"
)


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Approval package source must be a JSON object.")
    return payload


def bullet_list(values: Iterable[Any], empty: str = "None") -> List[str]:
    items = list(values)
    if not items:
        return [f"- {empty}"]
    return [f"- `{value}`" for value in items]


def records_to_add_lines(records: List[Dict[str, Any]]) -> List[str]:
    if not records:
        return ["- None in the current default package."]
    lines = []
    for record in records:
        canonical = record.get("canonicalRecord", {})
        lines.append(
            f"- `{record.get('canonicalId')}` from `{record.get('sourceRootId')}`: "
            f"{canonical.get('rootIast', '')} / {canonical.get('gloss', '')}"
        )
    return lines


def build_markdown(
    release_checklist: Dict[str, Any],
    dry_run_diff: Dict[str, Any],
    authorization: Dict[str, Any],
    readiness_lock: Dict[str, Any],
    evidence_report: Dict[str, Any],
) -> str:
    required_commands = release_checklist.get("requiredCommands", {})
    lines = [
        "# Canonical Write Approval Package",
        "",
        "## Current Release Status",
        "",
        f"- Release status: `{release_checklist.get('releaseStatus')}`",
        f"- Safe to write production: `{str(release_checklist.get('safeToWriteProduction')).lower()}`",
        f"- Evidence release gate: `{evidence_report.get('releaseGateStatus')}`",
        f"- Command status: `{dry_run_diff.get('commandStatus')}`",
        "",
        "## Authorized Record IDs",
        "",
        *bullet_list(authorization.get("authorizedRecordIds", [])),
        "",
        "## Ready Record IDs",
        "",
        *bullet_list(readiness_lock.get("readyRecordIds", [])),
        "",
        "## Records That Would Be Added",
        "",
        *records_to_add_lines(dry_run_diff.get("recordsToAdd", [])),
        "",
        "## Records Blocked Or Skipped",
        "",
        *bullet_list(dry_run_diff.get("recordsBlocked", [])),
        "",
        "## Exact Manual Approval Instructions",
        "",
        "1. Do not run any command yet.",
        "2. Inspect this package, `canonical_write_release_checklist.v1.json`, and `canonical_write_dry_run_diff.v1.json`.",
        "3. If and only if approving production write, edit `data/sanskrit/ingestion/canonical_write_approval.v1.json`.",
        "4. Set `approvalStatus` to `APPROVED`, set `approvedBy`, set `approvedAt`, and set `approvedRecordIds` to exactly the authorized ready IDs.",
        "5. Commit the approval edit before running any production write command.",
        "6. Regenerate approval validation, command manifest, dry-run diff, release checklist, and this package.",
        "",
        "## Exact Command Sequence After Approval",
        "",
        "```powershell",
        required_commands.get("approvalValidation", "python scripts/validate_dhatu_canonical_write_approval.py"),
        required_commands.get("commandManifest", "python scripts/prepare_dhatu_canonical_write_command.py"),
        required_commands.get("dryRunDiff", "python scripts/diff_dhatu_canonical_write_dry_run.py"),
        "python scripts/build_dhatu_canonical_write_release_checklist.py",
        "python scripts/build_dhatu_canonical_write_approval_package.py",
        required_commands.get("productionWritePreview", ""),
        "```",
        "",
        "## Warning",
        "",
        "No command should be run until human approval is edited, reviewed, and committed. This package does not approve or execute a canonical write.",
        "",
        "## Blocking Reasons",
        "",
        *bullet_list(release_checklist.get("blockingReasons", [])),
        "",
    ]
    return "\n".join(lines)


def build_approval_package() -> str:
    return build_markdown(
        load_json(DEFAULT_RELEASE_CHECKLIST_PATH),
        load_json(DEFAULT_DRY_RUN_DIFF_PATH),
        load_json(DEFAULT_AUTHORIZATION_PATH),
        load_json(DEFAULT_READINESS_LOCK_PATH),
        load_json(DEFAULT_EVIDENCE_REPORT_PATH),
    )


def write_approval_package(markdown: str, path: Any = DEFAULT_APPROVAL_PACKAGE_PATH) -> Path:
    output_path = resolve_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(markdown)
    return output_path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical dhatu write approval package.")
    parser.add_argument("--output", default=str(DEFAULT_APPROVAL_PACKAGE_PATH))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        markdown = build_approval_package()
        write_approval_package(markdown, args.output)
        print(json.dumps({"output": str(resolve_path(args.output)), "lines": len(markdown.splitlines())}, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu canonical write approval package failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
