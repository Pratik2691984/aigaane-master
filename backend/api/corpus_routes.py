"""
Corpus Search API — searches 701 Gītā verses via FTS5.

Backed by `canon.db` (568 KB, 701 verses, IAST + Devanagari + meter).
"""
from fastapi import APIRouter, Query, HTTPException
import sqlite3
from pathlib import Path

router = APIRouter()

CANON_DB_PATH = Path("C:/aigaane-master/frontend/public/sqlite/canon.db")


@router.get("/search")
def search_verses(q: str = Query(..., min_length=2), limit: int = 10):
    """Search Gītā verses by Sanskrit term. FTS5 prefix match."""
    if not CANON_DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=f"canon.db not found at {CANON_DB_PATH}"
        )
    try:
        conn = sqlite3.connect(str(CANON_DB_PATH))
        cur = conn.cursor()
        cur.execute(
            "SELECT v.chapter, v.verse, v.text, v.iast, v.meter, v.source "
            "FROM verses_fts f JOIN verses v ON v.rowid = f.rowid "
            "WHERE verses_fts MATCH ? LIMIT ?",
            (f"{q}*", limit)
        )
        rows = cur.fetchall()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"corpus search failed: {e}")

    return {
        "query": q,
        "count": len(rows),
        "verses": [
            {
                "chapter": r[0],
                "verse": r[1],
                "text": r[2],
                "iast": r[3],
                "meter": r[4],
                "source": r[5],
            }
            for r in rows
        ],
    }