from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_LOG = ROOT / "data" / "sanskrit" / "ingestion" / "write_audit.jsonl"


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_audit_log(record: Dict[str, Any], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


@contextmanager
def unchanged(*paths: Path, log_path: Path = DEFAULT_AUDIT_LOG):
    resolved = [Path(p) for p in paths]
    before = {p: (sha256(p) if p.exists() else None) for p in resolved}
    try:
        yield
    finally:
        after = {p: (sha256(p) if p.exists() else None) for p in resolved}
        changed = [str(p) for p in resolved if before[p] != after[p]]
        _append_audit_log(
            {
                "kind": "unchanged",
                "at": _now(),
                "paths": [str(p) for p in resolved],
                "before": {str(p): before[p] for p in resolved},
                "after": {str(p): after[p] for p in resolved},
                "changed": changed,
            },
            Path(log_path),
        )
        if changed:
            raise RuntimeError(f"unchanged() violated: {changed}")


@contextmanager
def authorized_write(*paths: Path, token: Optional[str], log_path: Path = DEFAULT_AUDIT_LOG):
    if not token:
        raise RuntimeError("authorized_write() requires a non-empty authorization token")
    resolved = [Path(p) for p in paths]
    before = {p: (sha256(p) if p.exists() else None) for p in resolved}
    try:
        yield
    finally:
        after = {p: (sha256(p) if p.exists() else None) for p in resolved}
        _append_audit_log(
            {
                "kind": "authorized_write",
                "at": _now(),
                "token": token,
                "paths": [str(p) for p in resolved],
                "before": {str(p): before[p] for p in resolved},
                "after": {str(p): after[p] for p in resolved},
            },
            Path(log_path),
        )

@contextmanager
def audited_write(*paths: Path, reason: str = "", log_path: Path = DEFAULT_AUDIT_LOG):
    resolved = [Path(p) for p in paths]
    before = {p: (sha256(p) if p.exists() else None) for p in resolved}
    try:
        yield
    finally:
        after = {p: (sha256(p) if p.exists() else None) for p in resolved}
        _append_audit_log(
            {
                "kind": "audited_write",
                "at": _now(),
                "reason": reason,
                "paths": [str(p) for p in resolved],
                "before": {str(p): before[p] for p in resolved},
                "after": {str(p): after[p] for p in resolved},
            },
            Path(log_path),
        )

@contextmanager
def audited_write(*paths: Path, reason: str = "", log_path: Path = DEFAULT_AUDIT_LOG):
    resolved = [Path(p) for p in paths]
    before = {p: (sha256(p) if p.exists() else None) for p in resolved}
    try:
        yield
    finally:
        after = {p: (sha256(p) if p.exists() else None) for p in resolved}
        _append_audit_log(
            {
                "kind": "audited_write",
                "at": _now(),
                "reason": reason,
                "paths": [str(p) for p in resolved],
                "before": {str(p): before[p] for p in resolved},
                "after": {str(p): after[p] for p in resolved},
            },
            Path(log_path),
        )
