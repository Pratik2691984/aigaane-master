"""
engines/lexicon/vidyut_kosha.py

Sanskrit lexicon lookup backed by vidyut.kosha.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from vidyut.kosha import Kosha
from vidyut.lipi import Scheme, transliterate


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KOSHA = ROOT / "data" / "vidyut" / "kosha"


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


class VidyutKosha:
    """Lookup for canonical Sanskrit words."""

    def __init__(self, kosha_path: Any = None, preload_dhatus: bool = True) -> None:
        path = Path(kosha_path) if kosha_path else DEFAULT_KOSHA
        if not path.exists():
            raise FileNotFoundError(
                "kosha data not found at %s; run vidyut.download_data()" % path
            )
        self._k = Kosha(str(path))
        self._kosha_path = str(path)

        self._dhatu_glosses: Dict[str, Dict[str, str]] = {}
        if preload_dhatus:
            self._load_dhatu_glosses()

    def _load_dhatu_glosses(self) -> None:
        for d in self._k.dhatus():
            dhatu = getattr(d, "dhatu", None)
            if dhatu is None:
                continue
            aupadeshika = getattr(dhatu, "aupadeshika", None)
            if not aupadeshika:
                continue
            key = str(aupadeshika)
            if key in self._dhatu_glosses:
                continue
            self._dhatu_glosses[key] = {
                "en": str(getattr(d, "artha_en", "") or ""),
                "hi": str(getattr(d, "artha_hi", "") or ""),
                "sa": str(getattr(d, "artha_sa", "") or ""),
            }

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

    def exists(self, word: str, script: str = "iast") -> bool:
        if not word or not word.strip():
            return False
        try:
            slp1 = self._to_slp1(word, script)
        except Exception:
            return False
        try:
            entries = self._k.get(slp1)
        except Exception:
            return False
        return len(entries) > 0

    def lookup(
        self,
        word: str,
        script: str = "iast",
        limit: int = 10,
    ) -> Dict[str, Any]:
        if not word or not word.strip():
            raise ValueError("word must be non-empty")

        slp1 = self._to_slp1(word, script)
        try:
            raw_entries = self._k.get(slp1)
        except Exception:
            raw_entries = []

        entries: List[Dict[str, Any]] = []
        seen_lemmas = set()
        for e in raw_entries:
            lemma_slp1 = str(e.lemma)
            if lemma_slp1 in seen_lemmas:
                continue
            seen_lemmas.add(lemma_slp1)
            entry: Dict[str, Any] = {
                "lemma_slp1": lemma_slp1,
                "lemma": self._from_slp1(lemma_slp1, script),
                "is_avyaya": bool(e.is_avyaya),
            }
            gloss = self._dhatu_glosses.get(lemma_slp1)
            if gloss:
                entry["gloss"] = gloss
            entries.append(entry)
            if len(entries) >= limit:
                break

        return {
            "word": word,
            "word_slp1": slp1,
            "script": script,
            "found": len(entries) > 0,
            "count": len(entries),
            "entries": entries,
        }

    def dhatu_gloss(self, root_slp1: str, lang: str = "en") -> str | None:
        key = (lang or "en").lower()
        if key not in {"en", "hi", "sa"}:
            key = "en"
        gloss = self._dhatu_glosses.get(root_slp1)
        if not gloss:
            return None
        return gloss.get(key) or None

    @property
    def dhatu_count(self) -> int:
        return len(self._dhatu_glosses)