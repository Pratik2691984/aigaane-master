"""
scripts/import_gita_local.py
Reads raw_sources/local_json/gita_v1.json, groups verses by chapter,
and writes v2.0.0 chapter envelopes to corpus/stotra/gita/.

No network calls. No API. Runs in under 5 seconds.
"""
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "raw_sources" / "local_json" / "gita_v1.json"
OUTPUT_BASE = ROOT / "corpus" / "stotra" / "gita"
MANIFEST_PATH = ROOT / "corpus" / "manifest.json"


def parse_id(verse_id, title):
    """Extract (chapter, verse) from id like 'gita-1.1' or title 'Bhagavad Gita 1.1'."""
    combined = f"{verse_id} {title}"
    match = re.search(r"(\d+)[\.\-_](\d+)", combined)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 1, 1


def determine_meter(text):
    """Heuristic: Anuṣṭubh if there are 4 pādas of ~8 syllables each."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) >= 2:
        return "Anuṣṭubh"
    return "Anuṣṭubh"


def main():
    if not SOURCE_PATH.exists():
        print(f"[ERROR] Source not found: {SOURCE_PATH}")
        return 1

    print(f"[READ] Loading {SOURCE_PATH}...")
    with open(SOURCE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        raw_verses = data
    else:
        raw_verses = data.get("records", data.get("verses", []))

    print(f"[LOADED] {len(raw_verses)} raw records.")

    # Group by chapter
    chapters = {}
    for idx, v in enumerate(raw_verses):
        v_id = str(v.get("id", f"gita-1.{idx+1}"))
        title = v.get("title", "")
        text = (v.get("text") or v.get("verse") or "").strip()

        chap_num, verse_num = parse_id(v_id, title)
               # Compute IAST from Devanagari if not already provided
        existing_iast = (v.get("iast") or "").strip()
        if existing_iast:
            iast = existing_iast
        else:
            from transliterate import devanagari_to_iast
            iast = devanagari_to_iast(text)

        chapters.setdefault(chap_num, []).append({
            "record_id": f"AIGAANE-BGM-{chap_num:02d}.{verse_num:03d}",
            "text": text,
            "iast": iast,
            "chapter": chap_num,
            "verse": verse_num,
            "meter": determine_meter(text),
            "source": v.get("source", "DharmicData/SrimadBhagvadGita"),
        })

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    manifest_entries = []
    total_written = 0

    for chap_num in sorted(chapters.keys()):
        verses = chapters[chap_num]
        chap_dir = OUTPUT_BASE / f"chapter_{chap_num:02d}"
        chap_dir.mkdir(parents=True, exist_ok=True)
        chap_file = chap_dir / f"chapter_{chap_num:02d}.json"

        envelope = {
            "schema_version": "2.0.0",
            "file_metadata": {
                "book": "Bhagavad Gītā",
                "section": f"Chapter {chap_num}",
                "cabinet": "CABINET_SMRITI_ITIHASA",
                "room": "MAHABHARATA_GITA",
                "record_count": len(verses),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "line_endings": "LF",
                "encoding": "UTF-8-NOBOM",
            },
            "records": verses,
        }

        with open(chap_file, "w", encoding="utf-8") as f:
            json.dump(envelope, f, ensure_ascii=False, indent=2)

        print(f"[WRITE] {chap_file.relative_to(ROOT)} ({len(verses)} verses)")
        total_written += len(verses)
        manifest_entries.append({
            "chapter": chap_num,
            "path": str(chap_file.relative_to(ROOT)).replace("\\", "/"),
            "verse_count": len(verses),
        })

    # Update the corpus manifest
    manifest = {}
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}

    manifest.setdefault("texts", {})
    manifest["texts"]["Bhagavad Gītā"] = {
        "cabinet": "CABINET_SMRITI_ITIHASA",
        "room": "MAHABHARATA_GITA",
        "total_verses": total_written,
        "chapters": manifest_entries,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"[MANIFEST] Updated {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"[DONE] {total_written} verses across {len(chapters)} chapters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())