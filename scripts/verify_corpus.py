"""
scripts/verify_corpus.py
Walks corpus/ and validates every envelope against schema v2.0.0.
Reports pass/fail per text. Catches corruption before publish.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"

REQUIRED_ENVELOPE_KEYS = ["schema_version", "file_metadata", "records"]
REQUIRED_META_KEYS = ["book", "section", "cabinet", "room", "record_count"]
REQUIRED_RECORD_KEYS = ["record_id", "text", "chapter", "verse", "meter"]

issues = []
stats = {"files": 0, "records": 0, "books": set()}


def has_devanagari(s):
    return any('\u0900' <= c <= '\u097F' for c in s)


def check_envelope(path):
    stats["files"] += 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        issues.append(f"{path}: invalid JSON — {e}")
        return

    for k in REQUIRED_ENVELOPE_KEYS:
        if k not in data:
            issues.append(f"{path}: missing envelope key '{k}'")

    meta = data.get("file_metadata", {})
    for k in REQUIRED_META_KEYS:
        if k not in meta:
            issues.append(f"{path}: missing file_metadata key '{k}'")

    records = data.get("records", [])
    declared = meta.get("record_count")
    if declared is not None and declared != len(records):
        issues.append(f"{path}: record_count={declared} but found {len(records)} records")

    stats["books"].add(meta.get("book", "UNKNOWN"))

    for i, r in enumerate(records):
        stats["records"] += 1
        for k in REQUIRED_RECORD_KEYS:
            if k not in r:
                issues.append(f"{path}: record {i} missing '{k}'")
        text = r.get("text", "")
        if not text:
            issues.append(f"{path}: record {i} has empty text")
        elif not has_devanagari(text):
            issues.append(f"{path}: record {i} text has no Devanagari: {text[:40]!r}")
        if "à¤" in text:
            issues.append(f"{path}: record {i} contains mojibake: {text[:40]!r}")


def main():
    print(f"=== Verifying corpus at {CORPUS} ===\n")
    for env in sorted(CORPUS.rglob("*.json")):
        # Skip manifest and other control files
        if env.name == "manifest.json":
            continue
        check_envelope(env)

    print(f"Files checked:   {stats['files']}")
    print(f"Records checked: {stats['records']}")
    print(f"Books:           {', '.join(sorted(stats['books']))}")
    print(f"Issues found:    {len(issues)}")

    if issues:
        print("\n--- Issues ---")
        for i in issues[:30]:
            print(f"  {i}")
        if len(issues) > 30:
            print(f"  ... and {len(issues) - 30} more")
        return 1

    print("\n[PASS] All envelopes are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())