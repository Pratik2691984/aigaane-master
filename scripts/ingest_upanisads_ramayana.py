# scripts/ingest_upanisads_ramayana.py
import os
import json
import re
from pathlib import Path

RAW_DIR = Path("./raw_sources/gretil")
OUT_DIR = Path("./frontend/public/data/canon")

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def parse_gretil_file(filepath, category, subcategory, source_name):
    """Parses a GRETIL plain-text file into structured verse records."""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by verse markers (e.g., "|| 1.1 ||" or "1.1")
    verses = re.split(r'\|+', content)
    
    for i, verse in enumerate(verses):
        verse = clean_text(verse)
        if not verse or len(verse) < 10:
            continue
        
        record_id = f"{category[:3]}_{subcategory[:4]}_{i+1:03d}"
        
        records.append({
            "record_id": record_id,
            "devanagari": verse,
            "iast": "", # To be auto-transliterated
            "padapatha": "",
            "translation_hindi": {"source": "Pending", "type": "literal", "text": ""},
            "translation_english": {"source": "Pending", "type": "scholarly", "text": ""},
            "filters": {
                "tradition": "shruti" if category == "upanishad" else "smriti",
                "category": category,
                "subcategory": subcategory,
                "text": source_name,
                "language": "sanskrit",
                "script": "devanagari",
                "meter_verified": False, # Track B will verify later
                "record_type": "verse",
                "verification_status": "PENDING_VERIFY_CI",
                "license": "public_domain"
            }
        })
    return records

def build_envelope(records, title):
    return {
        "schema_version": "2.0.0",
        "file_metadata": {
            "book": title,
            "section": "Complete",
            "cabinet": "CABINET_VEDA" if "upanishad" in title.lower() else "CABINET_SMRITI_ITIHASA",
            "room": "UPANISHADS" if "upanishad" in title.lower() else "RAMAYANA",
            "record_count": len(records),
            "generated_at": "2026-10-23T00:00:00Z",
            "line_endings": "LF",
            "encoding": "UTF-8-NOBOM"
        },
        "records": records
    }

def main():
    # Example: Process Isha Upanishad
    isha_path = RAW_DIR / "isha_upanishad.txt"
    if isha_path.exists():
        isha_records = parse_gretil_file(isha_path, "upanishad", "isha", "Īśāvāsya Upaniṣad")
        envelope = build_envelope(isha_records, "Isha Upanishad")
        
        out_path = OUT_DIR / "veda" / "upanishads" / "isha_upanishad.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(envelope, f, ensure_ascii=False, indent=2)
            
        print(f"[✓] Processed {len(isha_records)} verses into {out_path}")

if __name__ == "__main__":
    main()