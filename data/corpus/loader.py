"""
engines/corpus/loader.py
Itihāsa corpus loader and search.

Loads structured JSON verse files and provides keyword + metadata search.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ─────────────────────── Data structures ───────────────────────

@dataclass(frozen=True)
class Verse:
    id: str
    source: str
    iast: str
    meter: str
    themes: tuple[str, ...]
    gloss: str
    location: str  # formatted: "Rāmāyaṇa 1.1.1" or "Mahābhārata 1.1.1"


@dataclass(frozen=True)
class SearchResult:
    verse: Verse
    score: float
    matched_terms: tuple[str, ...]


# ─────────────────────── Loader ───────────────────────

class Corpus:
    def __init__(self, corpus_path: Optional[Path] = None):
        if corpus_path is None:
            corpus_path = Path(__file__).parent.parent.parent / "data" / "corpus" / "sample.json"
        self.corpus_path = Path(corpus_path)
        self.verses: list[Verse] = []
        self._load()

    def _load(self) -> None:
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus not found: {self.corpus_path}")

        with open(self.corpus_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for v in data.get("verses", []):
            location = self._format_location(v)
            self.verses.append(Verse(
                id=v["id"],
                source=v["source"],
                iast=v["iast"],
                meter=v.get("meter", "unknown"),
                themes=tuple(v.get("themes", [])),
                gloss=v.get("gloss", ""),
                location=location,
            ))

    @staticmethod
    def _format_location(v: dict) -> str:
        source = v.get("source", "Unknown")
        parts = [source]
        for key in ("kanda", "parva"):
            if key in v:
                parts.append(v[key])
        for key in ("sarga", "adhyaya", "verse"):
            if key in v:
                parts.append(str(v[key]))
        return " ".join(parts)

    # ─────────────────────── Search ───────────────────────

    def search(
        self,
        query: str,
        source: Optional[str] = None,
        meter: Optional[str] = None,
        theme: Optional[str] = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Keyword + metadata search.

        Scoring:
          - Exact IAST match:          10.0
          - Substring in IAST:          5.0
          - Substring in gloss:         3.0
          - Theme tag match:            4.0
          - Source/Meter filter match:  1.0 (filter, not score)

        Only verses matching all provided filters are returned.
        """
        query_lower = query.lower().strip()
        query_terms = [t for t in re.split(r"\W+", query_lower) if t]

        results: list[SearchResult] = []

        for verse in self.verses:
            # Apply filters
            if source and verse.source.lower() != source.lower():
                continue
            if meter and verse.meter.lower() != meter.lower():
                continue
            if theme and theme.lower() not in [t.lower() for t in verse.themes]:
                continue

            # Score
            score = 0.0
            matched: list[str] = []

            iast_lower = verse.iast.lower()
            gloss_lower = verse.gloss.lower()
            themes_lower = [t.lower() for t in verse.themes]

            for term in query_terms:
                if term in iast_lower:
                    if iast_lower.strip() == term:
                        score += 10.0
                    else:
                        score += 5.0
                    matched.append(term)
                elif term in gloss_lower:
                    score += 3.0
                    matched.append(term)
                elif term in themes_lower:
                    score += 4.0
                    matched.append(term)
                elif term in verse.source.lower():
                    score += 2.0
                    matched.append(term)

            if score > 0 or not query_terms:
                # If no query, return all (respecting filters)
                results.append(SearchResult(
                    verse=verse,
                    score=score,
                    matched_terms=tuple(matched),
                ))

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    # ─────────────────────── Stats ───────────────────────

    def stats(self) -> dict:
        sources: dict[str, int] = {}
        meters: dict[str, int] = {}
        theme_counts: dict[str, int] = {}

        for v in self.verses:
            sources[v.source] = sources.get(v.source, 0) + 1
            meters[v.meter] = meters.get(v.meter, 0) + 1
            for t in v.themes:
                theme_counts[t] = theme_counts.get(t, 0) + 1

        return {
            "total_verses": len(self.verses),
            "sources": sources,
            "meters": meters,
            "themes": dict(sorted(theme_counts.items(), key=lambda x: -x[1])),
        }


# ─────────────────────── Self-test ───────────────────────

if __name__ == "__main__":
    corpus = Corpus()
    print(f"Loaded {len(corpus.verses)} verses")

    stats = corpus.stats()
    print(f"Sources: {stats['sources']}")
    print(f"Meters: {stats['meters']}")

    # Search test
    results = corpus.search("rāma", limit=3)
    print(f"\nSearch 'rāma' → {len(results)} results")
    for r in results:
        print(f"  [{r.score:.1f}] {r.verse.location}: {r.verse.iast[:50]}...")

    # Filter test
    results = corpus.search("", source="Rāmāyaṇa", limit=5)
    print(f"\nAll Rāmāyaṇa verses: {len(results)}")

    print("\nloader.py OK")