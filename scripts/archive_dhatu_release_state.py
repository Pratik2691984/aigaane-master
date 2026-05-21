#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from validate_large_scale_ingestion import ROOT


RELEASE_TAG = "sanskrit-v50-canonical-write-state-fixtures-stable"
DEFAULT_RELEASE_DIR = ROOT / "data" / "sanskrit" / "ingestion" / "releases" / "v50"
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_POST_AUDIT_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_write_post_audit_verification.v1.json"

ARCHIVE_SOURCES: Dict[str, Path] = {
    "canonical_registry.v50.json": DEFAULT_CANONICAL_REGISTRY_PATH,
    "canonical_promotion_audit.v50.json": ROOT / "data" / "sanskrit" / "ingestion" / "canonical_promotion_audit.v1.json",
    "canonical_write_release_verification.v50.json": ROOT
    / "data"
    / "sanskrit"
    / "ingestion"
    / "canonical_write_release_verification.v1.json",
    "canonical_write_post_audit_verification.v50.json": DEFAULT_POST_AUDIT_PATH,
    "canonical_write_preflight_snapshot.v50.json": ROOT
    / "data"
    / "sanskrit"
    / "ingestion"
    / "canonical_write_preflight_snapshot.v1.json",
    "canonical_promotion_closeout_index.v50.json": ROOT
    / "data"
    / "sanskrit"
    / "ingestion"
    / "canonical_promotion_closeout_index.v1.json",
}


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def run_git(args: List[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Archive source must be a JSON object: {path}")
    return payload


def sha256_file(path: Any) -> str:
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def display_path(path: Any) -> str:
    resolved = resolve_path(path)
    try:
        return str(resolved.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def canonical_record_count(registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH) -> int:
    return len(load_json(registry_path).get("records", {}))


def has_duplicate_canonical_ids(registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH) -> bool:
    records = list(load_json(registry_path).get("records", {}).keys())
    return len(records) != len(set(records))


def v50_tag_exists(release_tag: str = RELEASE_TAG) -> bool:
    return release_tag in run_git(["tag", "--list", release_tag]).splitlines()


def build_merge_readiness_checks(
    registry_path: Any,
    post_audit: Dict[str, Any],
    release_tag: str,
    branch_clean: bool,
) -> Dict[str, Any]:
    promoted_count = int(post_audit.get("promotedCount", 0))
    record_count = canonical_record_count(registry_path)
    return {
        "releaseBranchClean": branch_clean,
        "currentBranch": run_git(["branch", "--show-current"]),
        "v50TagExists": v50_tag_exists(release_tag),
        "canonicalRegistryCountIs13": record_count == 13,
        "promotedCountIs3": promoted_count == 3,
        "noDuplicateCanonicalIds": not has_duplicate_canonical_ids(registry_path),
        "testSuitePassingExpectation": {
            "command": 'python -m unittest discover -s api -p "test_*.py"',
            "expectedPassingTests": 712,
            "status": "expected-passing",
        },
    }


def build_archive_manifest(
    output_dir: Any = DEFAULT_RELEASE_DIR,
    release_tag: str = RELEASE_TAG,
    registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    post_audit_path: Any = DEFAULT_POST_AUDIT_PATH,
    artifact_hashes: Optional[Dict[str, str]] = None,
    branch_clean: Optional[bool] = None,
) -> Dict[str, Any]:
    post_audit = load_json(post_audit_path)
    if branch_clean is None:
        branch_clean = run_git(["status", "--short"]) == ""
    release_commit = run_git(["rev-parse", "HEAD"])
    promoted_ids = list(post_audit.get("promotedRecordIds", []))
    return {
        "schemaVersion": "1.0.0",
        "releaseTag": release_tag,
        "releaseCommit": release_commit,
        "canonicalRegistryRecordCount": canonical_record_count(registry_path),
        "promotedRecordIds": promoted_ids,
        "artifactHashes": artifact_hashes or {},
        "archivedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "archivedByScript": "scripts/archive_dhatu_release_state.py",
        "productionWriteExecuted": post_audit.get("canonicalWriteAttempted") is True and int(post_audit.get("promotedCount", 0)) == 3,
        "postWriteVerificationStatus": post_audit.get("verificationStatus"),
        "mergeReadinessChecks": build_merge_readiness_checks(registry_path, post_audit, release_tag, branch_clean),
        "sourceArtifacts": {
            archive_name: str(source.relative_to(ROOT)).replace("\\", "/")
            for archive_name, source in ARCHIVE_SOURCES.items()
        },
        "archiveDirectory": display_path(output_dir),
    }


def planned_destinations(output_dir: Any = DEFAULT_RELEASE_DIR) -> List[Path]:
    directory = resolve_path(output_dir)
    return [directory / name for name in [*ARCHIVE_SOURCES.keys(), "release_archive_manifest.v50.json"]]


def ensure_can_write_archive(output_dir: Any = DEFAULT_RELEASE_DIR, force: bool = False) -> None:
    existing = [path for path in planned_destinations(output_dir) if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(f"Refusing to overwrite existing release archive files without --force: {names}")


def archive_release_state(output_dir: Any = DEFAULT_RELEASE_DIR, force: bool = False) -> Dict[str, Any]:
    output = resolve_path(output_dir)
    registry_before = sha256_file(DEFAULT_CANONICAL_REGISTRY_PATH)
    branch_clean = run_git(["status", "--short"]) == ""
    ensure_can_write_archive(output, force)
    output.mkdir(parents=True, exist_ok=True)

    artifact_hashes: Dict[str, str] = {}
    for archive_name, source in ARCHIVE_SOURCES.items():
        destination = output / archive_name
        shutil.copy2(source, destination)
        artifact_hashes[archive_name] = sha256_file(destination)

    manifest = build_archive_manifest(
        output_dir=output,
        artifact_hashes=artifact_hashes,
        branch_clean=branch_clean,
    )
    manifest_path = output / "release_archive_manifest.v50.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    registry_after = sha256_file(DEFAULT_CANONICAL_REGISTRY_PATH)
    if registry_before != registry_after:
        raise RuntimeError("Canonical registry changed during archive generation.")
    return manifest


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive dhatu canonical promotion release state.")
    parser.add_argument("--output-dir", default=str(DEFAULT_RELEASE_DIR), help="Directory to write v50 release archive snapshots.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing archive files.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        manifest = archive_release_state(args.output_dir, force=args.force)
        print(json.dumps({
            "releaseTag": manifest["releaseTag"],
            "canonicalRegistryRecordCount": manifest["canonicalRegistryRecordCount"],
            "promotedCount": len(manifest["promotedRecordIds"]),
            "postWriteVerificationStatus": manifest["postWriteVerificationStatus"],
        }, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Dhatu release archive failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
