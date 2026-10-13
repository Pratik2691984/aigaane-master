"""
engines/chandas/vidyut_chandas.py

Chandas (meter) classifier backed by vidyut.chandas.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from vidyut.chandas import Chandas
from vidyut.lipi import Scheme, transliterate


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METERS = ROOT / "data" / "vidyut" / "chandas" / "meters.tsv"


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


class VidyutChandas:
    """Classify Sanskrit text against a catalog of vṛttas and jātis."""

    def __init__(self, meters_path: Any = None) -> None:
        path = Path(meters_path) if meters_path else DEFAULT_METERS
        if not path.exists():
            raise FileNotFoundError(
                "meters data not found at %s; run vidyut.download_data()" % path
            )
        self._c = Chandas(str(path))
        self._meters_path = str(path)

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

    def _scan_one(self, pada_slp1: str, script: str) -> Dict[str, Any]:
        m = self._c.classify(pada_slp1)
        aksharas = m.aksharas[0] if m.aksharas else []
        weights = "".join(str(a.weight) for a in aksharas)
        return {
            "padya": m.padya,
            "akshara_count": len(aksharas),
            "weights": weights,
            "aksharas": [
                {
                    "text": self._from_slp1(a.text, script),
                    "weight": str(a.weight),
                }
                for a in aksharas
            ],
        }

    def scan(
        self,
        text: str,
        script: str = "iast",
        include_aksharas: bool = True,
    ) -> Dict[str, Any]:
        if not text or not text.strip():
            raise ValueError("text must be non-empty")

        slp1 = self._to_slp1(text, script)
        pada_texts = [p.strip() for p in slp1.split("|") if p.strip()]
        if not pada_texts:
            raise ValueError("no padas found after splitting on '|'")

        padas: List[Dict[str, Any]] = []
        for i, pada_slp1 in enumerate(pada_texts):
            entry = self._scan_one(pada_slp1, script)
            entry["index"] = i
            entry["text"] = self._from_slp1(pada_slp1, script)
            if not include_aksharas:
                entry.pop("aksharas", None)
            padas.append(entry)

        matched_meters = [p["padya"] for p in padas if p["padya"]]
        unique_meters = sorted(set(matched_meters))

        return {
            "text": text,
            "text_slp1": slp1,
            "script": script,
            "pada_count": len(padas),
            "matched_meters": unique_meters,
            "all_padas_matched": len(matched_meters) == len(padas),
            "padas": padas,
            "known_vrttas": len(self._c.vrttas),
            "known_jatis": len(self._c.jatis),
        }