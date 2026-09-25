"""
scripts/build_public_index.py
Builds public/sqlite/canon.db from corpus/.
Only processes v2.0.0 envelopes (skips dhatu/sutra/stotra seed files).
"""
import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
OUTPUT_DIR = ROOT / "public" / "sqlite"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = OUTPUT_DIR / "canon.db"


def build_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[CLEAN] Removed old {DB_PATH.name}")

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE verses (
            record_id TEXT PRIMARY KEY,
            book TEXT,
            chapter INTEGER,
            verse INTEGER,
            text TEXT,
            iast TEXT,
            meter TEXT,
            source TEXT,
            envelope_path TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE texts (
            book TEXT PRIMARY KEY,
            cabinet TEXT,
            room TEXT,
            total_verses INTEGER,
            total_chapters INTEGER,
            last_updated TEXT
        )
    """)

    cur.execute("""
        CREATE VIRTUAL TABLE verses_fts USING fts5(
            text,
            iast,
            meter,
            content='verses',
            content_rowid='rowid'
        )
    """)

    total_verses = 0
    books = {}
    skipped = 0

    for env in sorted(CORPUS.rglob("*.json")):
        if env.name == "manifest.json":
            continue

        try:
            data = json.loads(env.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[SKIP] {env.name}: {e}")
            skipped += 1
            continue

        # Only process proper v2.0.0 envelopes
        if data.get("schema_version") != "2.0.0":
            skipped += 1
            continue
        if "file_metadata" not in data or "records" not in data:
            skipped += 1
            continue

        meta = data.get("file_metadata", {})
        book = meta.get("book", "UNKNOWN")
        cabinet = meta.get("cabinet", "")
        room = meta.get("room", "")
        rel_path = str(env.relative_to(ROOT)).replace("\\", "/")

        for r in data.get("records", []):
            cur.execute("""
                INSERT OR REPLACE INTO verses
                (record_id, book, chapter, verse, text, iast, meter, source, envelope_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r.get("record_id"),
                book,
                r.get("chapter"),
                r.get("verse"),
                r.get("text", ""),
                r.get("iast", ""),
                r.get("meter", ""),
                r.get("source", ""),
                rel_path,
            ))
            total_verses += 1

        b = books.setdefault(book, {
            "cabinet": cabinet,
            "room": room,
            "chapters": set(),
            "verses": 0,
            "last_updated": meta.get("last_updated", ""),
        })
        b["chapters"].add(meta.get("section"))
        b["verses"] += len(data.get("records", []))

    for book, b in books.items():
        cur.execute("""
            INSERT OR REPLACE INTO texts
            (book, cabinet, room, total_verses, total_chapters, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            book,
            b["cabinet"],
            b["room"],
            b["verses"],
            len(b["chapters"]),
            b["last_updated"],
        ))

    cur.execute(
        "INSERT INTO verses_fts(rowid, text, iast, meter) "
        "SELECT rowid, text, iast, meter FROM verses"
    )

    conn.commit()
    conn.close()

    size_kb = DB_PATH.stat().st_size / 1024
    print(f"[BUILT] {DB_PATH.relative_to(ROOT)}")
    print(f"  Total verses:  {total_verses}")
    print(f"  Texts:         {len(books)}")
    print(f"  Skipped files: {skipped}")
    print(f"  Size:          {size_kb:.1f} KB")


if __name__ == "__main__":
    build_db()