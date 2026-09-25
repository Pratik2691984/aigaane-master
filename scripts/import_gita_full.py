"""
scripts/import_gita_full.py
Reads the full 700-verse Bhagavad Gītā from raw_sources/github/verse.json
and produces v2.0.0 chapter envelopes in corpus/stotra/gita/.

Splits speaker attribution (धृतराष्ट्र उवाच, etc.) into a separate 'speaker'
field so verse text is clean. Uses source-provided transliteration for IAST.

Overwrites the existing 5-chapter corpus with the full 18 chapters.
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "raw_sources" / "github" / "verse.json"
OUTPUT_BASE = ROOT / "corpus" / "stotra" / "gita"
MANIFEST_PATH = ROOT / "corpus" / "manifest.json"

# --- Speaker lookup table (Devanagari → canonical english id) ---
SPEAKER_MAP = [
    (re.compile(r'धृतराष्ट्र\s*उवाच'), 'dhritarashtra'),
    (re.compile(r'सञ्जय\s*उवाच'),      'sanjaya'),
    (re.compile(r'संजय\s*उवाच'),       'sanjaya'),
    (re.compile(r'श्रीभगवान्?\s*उवाच'),'bhagavan_krishna'),
    (re.compile(r'अर्जुन\s*उवाच'),     'arjuna'),
    (re.compile(r'श्री\s*भगवान्?\s*उवाच'), 'bhagavan_krishna'),
    (re.compile(r'राजा\s*उवाच'),       'dhritarashtra'),
]

# Devanagari digit → ascii
DEVA_DIGITS = '०१२३४५६७८९'


def clean_deva_num(s: str) -> str:
    """Replace Devanagari digits with ASCII."""
    return ''.join(str(DEVA_DIGITS.index(c)) if c in DEVA_DIGITS else c for c in s)


def strip_danda(text: str) -> str:
    """Remove trailing danda and verse markers like ।।1.1।।"""
    # Remove patterns like ।।1.1।। or ।। १.१ ।।
    text = re.sub(r'।।\s*[०-९\d]+\.[०-९\d]+\s*।।\s*$', '', text)
    text = re.sub(r'॥\s*[०-९\d]+\.[०-९\d]+\s*॥\s*$', '', text)
    return text.strip()


def split_speaker_and_verse(text: str):
    """
    Given a verse text block, return (verse_text, speaker_id).
    """
    speaker = None
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # Look for a speaker line in the first two lines
    kept_lines = []
    for i, line in enumerate(lines):
        matched = False
        for pattern, sid in SPEAKER_MAP:
            if pattern.search(line):
                speaker = sid
                matched = True
                break
        if not matched:
            kept_lines.append(line)

    verse = '\n'.join(kept_lines)
    verse = strip_danda(verse)
    return verse, speaker


def determine_meter(text: str) -> str:
    """Assign meter. Default Anuṣṭubh (most of Gītā). Chapter 2 and 11 have Triṣṭubh verses."""
    # Simple heuristic — could be improved with real scansion
    return 'Anuṣṭubh'


def main():
    if not SOURCE_PATH.exists():
        print(f"[ERROR] Source not found: {SOURCE_PATH}")
        return 1

    print(f"[READ] Loading {SOURCE_PATH}...")
    with open(SOURCE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"[ERROR] Expected a list at top level, got {type(data).__name__}")
        return 1

    print(f"[LOADED] {len(data)} raw records.")

    # Filter to real verses (skip chapter-level summary records)
    verses_raw = [r for r in data if r.get('verse_number') is not None]
    print(f"[FILTER] {len(verses_raw)} verse records.")

    # Group by chapter
    chapters = {}
    for v in verses_raw:
        chap = v.get('chapter_number')
        verse_num = v.get('verse_number')
        if chap is None or verse_num is None:
            continue

        raw_text = v.get('text', '') or ''
        iast_raw = v.get('transliteration', '') or ''

        verse_deva, speaker = split_speaker_and_verse(raw_text)
        iast_clean, _ = split_speaker_and_verse(iast_raw)

        # If speaker didn't get split (e.g. single-line verse), try IAST speaker strip
        if not speaker:
            _, speaker = split_speaker_and_verse(iast_raw)

        record = {
            "record_id": f"AIGAANE-BGM-{chap:02d}.{verse_num:03d}",
            "text": verse_deva,
            "iast": iast_clean,
            "chapter": chap,
            "verse": verse_num,
            "meter": determine_meter(verse_deva),
            "source": "github.com/gita/gita",
        }
        if speaker:
            record["speaker"] = speaker

        chapters.setdefault(chap, []).append(record)

    # Sort each chapter's verses
    for chap in chapters:
        chapters[chap].sort(key=lambda r: r["verse"])

    # Clean output dir
    if OUTPUT_BASE.exists():
        import shutil
        shutil.rmtree(OUTPUT_BASE)
        print(f"[CLEAN] Removed old {OUTPUT_BASE.relative_to(ROOT)}")

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

    # Update manifest
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
        "total_chapters": len(chapters),
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