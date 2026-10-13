#!/usr/bin/env python
"""Reconcile write_audit.jsonl against the files currently on disk."""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_LOG = ROOT / "data" / "sanskrit" / "ingestion" / "write_audit.jsonl"


def sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not AUDIT_LOG.exists():
        print(f"no audit log at {AUDIT_LOG}", file=sys.stderr)
        return 1

    last_seen: dict[str, str] = {}
    with AUDIT_LOG.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            after = record.get("after", {})
            for path, digest in after.items():
                if digest:
                    last_seen[path] = digest

    drift = []
    missing = []
    for path, expected in sorted(last_seen.items()):
        p = Path(path)
        if not p.exists():
            missing.append(path)
            continue
        current = sha256(p)
        if current != expected:
            drift.append((path, expected, current))

    for path in missing:
        print(f"MISSING  {path}")
    for path, expected, current in drift:
        print(f"DRIFT    {path}")
        print(f"         expected {expected}")
        print(f"         current  {current}")

    if not drift and not missing:
        print(f"clean: {len(last_seen)} paths match their last logged hashes")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
