"""Inspect one envelope to verify UTF-8 integrity."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ENVELOPE = ROOT / "corpus" / "stotra" / "gita" / "chapter_01" / "chapter_01.json"

print(f"Reading: {ENVELOPE}")
raw = ENVELOPE.read_text(encoding="utf-8")
print(f"File size: {len(raw)} chars")

# Direct string search
print(f"Contains धर्म: {'धर्म' in raw}")
print(f"Contains à¤: {'à¤' in raw}")

# Parse JSON
data = json.loads(raw)
first = data["records"][0]

print("\n--- First record ---")
print(f"record_id: {first['record_id']}")
print(f"text (repr): {repr(first['text'][:80])}")
print(f"text (raw):  {first['text'][:80]}")
print(f"meter: {first['meter']}")

print("\n--- File metadata ---")
print(f"book: {data['file_metadata']['book']}")