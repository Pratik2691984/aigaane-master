"""
engines/phonology/sandhi_splitter.py

Sandhi splitter backed by vidyut.sandhi.

Returns candidate two-word splits. Ranking prefers candidates where
the first word is a known Sanskrit word, then longer first words.
The COMMON_WORDS list is small and covers the most frequent forms.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Set

from vidyut.sandhi import Splitter
from vidyut.lipi import Scheme, transliterate


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RULES = ROOT / "data" / "vidyut" / "sandhi" / "rules.csv"
DEFAULT_WORDS = ROOT / "data" / "sanskrit" / "lexicon" / "common_words.txt"


SCHEME_MAP = {
    "iast": Scheme.Iast,
    "slp1": Scheme.Slp1,
    "devanagari": Scheme.Devanagari,
    "deva": Scheme.Devanagari,
    "harvardkyoto": Scheme.HarvardKyoto,
    "hk": Scheme.HarvardKyoto,
    "iso15919": Scheme.Iso15919,
    "itrans": Scheme.Itrans,
}


class SandhiSplitter:
    """Split a joined Sanskrit string into candidate word pairs."""

    def __init__(
        self,
        rules_path: Any = None,
        words_path: Any = None,
    ) -> None:
        path = Path(rules_path) if rules_path else DEFAULT_RULES
        if not path.exists():
            raise FileNotFoundError(
                "sandhi rules not found at %s; run vidyut.download_data()" % path
            )
        self._splitter = Splitter.from_csv(str(path))
        self._rules_path = str(path)

        words_file = Path(words_path) if words_path else DEFAULT_WORDS
        self._common_slp1: Set[str] = set()
        if words_file.exists():
            for line in words_file.read_text(encoding="utf-8").splitlines():
                word = line.strip()
                if not word or word.startswith("#"):
                    continue
                try:
                    self._common_slp1.add(
                        transliterate(word, Scheme.Iast, Scheme.Slp1)
                    )
                except Exception:
                    continue

    def _resolve_scheme(self, name: str) -> Scheme:
        key = (name or "iast").strip().lower().replace("-", "").replace("_", "")
        if key not in SCHEME_MAP:
            raise ValueError(
                "unknown script %r; known: %s" % (name, sorted(SCHEME_MAP))
            )
        return SCHEME_MAP[key]

    def _to_slp1(self, text: str, script: str) -> str:
        if script.strip().lower() == "slp1":
            return text
        return transliterate(text, self._resolve_scheme(script), Scheme.Slp1)

    def _from_slp1(self, text: str, script: str) -> str:
        if script.strip().lower() == "slp1":
            return text
        return transliterate(text, Scheme.Slp1, self._resolve_scheme(script))

    def _is_known(self, slp1: str) -> bool:
        return slp1 in self._common_slp1

    def split(
        self,
        text: str,
        script: str = "iast",
        max_results: int = 20,
        include_invalid: bool = False,
        min_side_length: int = 1,
    ) -> Dict[str, Any]:
        if not text or len(text) < 2:
            raise ValueError("text must be at least two characters")

        slp1 = self._to_slp1(text, script)
        results: List[Dict[str, Any]] = []
        seen = set()

        for index in range(1, len(slp1)):
            try:
                candidates = self._splitter.split_at(slp1, index)
            except Exception:
                continue
            for candidate in candidates:
                if not include_invalid and not candidate.is_valid:
                    continue
                first_slp1 = str(candidate.first)
                second_slp1 = str(candidate.second)
                if len(first_slp1) < min_side_length:
                    continue
                if len(second_slp1) < min_side_length:
                    continue
                key = (first_slp1, second_slp1)
                if key in seen:
                    continue
                seen.add(key)

                first_known = self._is_known(first_slp1)
                second_known = self._is_known(second_slp1)
                results.append(
                    {
                        "first": self._from_slp1(first_slp1, script),
                        "second": self._from_slp1(second_slp1, script),
                        "valid": bool(candidate.is_valid),
                        "split_index": index,
                        "first_len": len(first_slp1),
                        "second_len": len(second_slp1),
                        "first_known": first_known,
                        "second_known": second_known,
                    }
                )

        # Rank: known words first, both sides known highest, then length.
        def _rank_key(r: Dict[str, Any]) -> tuple:
            known_score = int(r["first_known"]) + int(r["second_known"])
            both_known = int(r["first_known"] and r["second_known"])
            return (
                -both_known,
                -known_score,
                -r["first_len"],
                -r["second_len"],
                r["split_index"],
            )

        results.sort(key=_rank_key)
        results = results[:max_results]

        return {
            "text": text,
            "text_slp1": slp1,
            "script": script,
            "rules": self._rules_path,
            "known_words_loaded": len(self._common_slp1),
            "count": len(results),
            "splits": results,
        }