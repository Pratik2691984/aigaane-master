"""Quick sanity test — query the new SQLite DB."""
import sqlite3
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "public" / "sqlite" / "canon.db"

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

print("=== Texts in DB ===")
for row in cur.execute("SELECT book, total_verses, total_chapters FROM texts"):
    print(f"  {row[0]}: {row[1]} verses across {row[2]} chapters")

print("\n=== First 3 verses of chapter 1 ===")
for row in cur.execute("SELECT record_id, chapter, verse, substr(text, 1, 60) FROM verses WHERE book LIKE 'Bhagavad%' AND chapter=1 ORDER BY verse LIMIT 3"):
    print(f"  {row[0]} (ch {row[1]}.{row[2]}): {row[3]}…")

print("\n=== Full-text search for 'कर्म' ===")
for row in cur.execute("""
    SELECT v.record_id, substr(v.text, 1, 60)
    FROM verses_fts fts
    JOIN verses v ON v.rowid = fts.rowid
    WHERE verses_fts MATCH 'कर्म'
    LIMIT 5
"""):
    print(f"  {row[0]}: {row[1]}…")

print("\n=== Chapter 2, verse 47 (the famous one) ===")
for row in cur.execute("SELECT record_id, text FROM verses WHERE chapter=2 AND verse=47"):
    print(f"  {row[0]}: {row[1]}")

conn.close()