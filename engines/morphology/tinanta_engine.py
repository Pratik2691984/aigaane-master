"""
engines/morphology/tinanta_engine.py

Tiṅanta (finite verb) generator backed by vidyut-prakriya.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from vidyut.prakriya import (
    Dhatu,
    Gana,
    Lakara,
    Pada,
    Prayoga,
    Purusha,
    Vacana,
    Vyakarana,
)
from vidyut.lipi import Scheme, transliterate


GANA_MAP = {
    1: Gana.Bhvadi,
    2: Gana.Adadi,
    3: Gana.Juhotyadi,
    4: Gana.Divadi,
    5: Gana.Svadi,
    6: Gana.Tudadi,
    7: Gana.Rudhadi,
    8: Gana.Tanadi,
    9: Gana.Kryadi,
    10: Gana.Curadi,
}

LAKARA_MAP = {
    "lat": Lakara.Lat,
    "lit": Lakara.Lit,
    "lut": Lakara.Lut,
    "lrt": Lakara.Lrt,
    "lot": Lakara.Lot,
    "lan": Lakara.Lan,
    "vidhiling": Lakara.VidhiLin,
    "ashirling": Lakara.AshirLin,
    "lun": Lakara.Lun,
    "lrn": Lakara.Lrn,
}

PRAYOGA_MAP = {
    "kartari": Prayoga.Kartari,
    "karmani": Prayoga.Karmani,
    "bhave": Prayoga.Bhave,
}

PURUSHA_MAP = [
    ("prathama", Purusha.Prathama),
    ("madhyama", Purusha.Madhyama),
    ("uttama", Purusha.Uttama),
]

VACANA_MAP = [
    ("eka", Vacana.Eka),
    ("dvi", Vacana.Dvi),
    ("bahu", Vacana.Bahu),
]

SCHEME_MAP = {
    "iast": Scheme.Iast,
    "slp1": Scheme.Slp1,
    "devanagari": Scheme.Devanagari,
    "deva": Scheme.Devanagari,
    "harvardkyoto": Scheme.HarvardKyoto,
    "hk": Scheme.HarvardKyoto,
    "iso15919": Scheme.Iso15919,
    "itrans": Scheme.Itrans,
    "velthuis": Scheme.Velthuis,
    "wx": Scheme.Wx,
}


class TinantaEngine:
    """Generate finite verb paradigms using vidyut-prakriya."""

    def __init__(self) -> None:
        self._v = Vyakarana()

    def _resolve_scheme(self, name: str) -> Scheme:
        key = (name or "iast").strip().lower().replace("-", "").replace("_", "")
        if key not in SCHEME_MAP:
            raise ValueError(
                "unknown script %r; known: %s" % (name, sorted(SCHEME_MAP))
            )
        return SCHEME_MAP[key]

    def to_slp1(self, text: str, source: str = "iast") -> str:
        if source.strip().lower() == "slp1":
            return text
        return transliterate(text, self._resolve_scheme(source), Scheme.Slp1)

    def from_slp1(self, text: str, target: str = "iast") -> str:
        if target.strip().lower() == "slp1":
            return text
        return transliterate(text, Scheme.Slp1, self._resolve_scheme(target))

    def _step_to_dict(self, step: Any) -> Dict[str, str]:
        raw = getattr(step, "result", []) or []
        return {
            "code": str(getattr(step, "code", "")),
            "result": " ".join(str(x) for x in raw),
            "source": str(getattr(step, "source", "")),
        }

    def conjugate_grid(
        self,
        root: str,
        gana: int = 1,
        lakara: str = "lat",
        prayoga: str = "kartari",
        input_script: str = "iast",
        output_script: str = "iast",
        include_traces: bool = True,
        strict: bool = False,
    ) -> Dict[str, Any]:
        if gana not in GANA_MAP:
            raise ValueError("gana must be 1..10, got %r" % (gana,))

        lakara_key = (lakara or "lat").strip().lower()
        if lakara_key not in LAKARA_MAP:
            raise ValueError(
                "unknown lakara %r; known: %s" % (lakara, sorted(LAKARA_MAP))
            )

        prayoga_key = (prayoga or "kartari").strip().lower()
        if prayoga_key not in PRAYOGA_MAP:
            raise ValueError(
                "unknown prayoga %r; known: %s" % (prayoga, sorted(PRAYOGA_MAP))
            )

        root_slp1 = self.to_slp1(root, input_script)
        gana_enum = GANA_MAP[gana]
        lakara_enum = LAKARA_MAP[lakara_key]
        prayoga_enum = PRAYOGA_MAP[prayoga_key]

        paradigm = {}
        traces = {}
        counts = {}
        errors = []

        for p_label, p_enum in PURUSHA_MAP:
            paradigm[p_label] = {}
            for v_label, v_enum in VACANA_MAP:
                key = "%s_%s" % (p_label, v_label)
                try:
                    prakriyas = self._v.derive(
                        Pada.Tinanta(
                            dhatu=Dhatu.mula(
                                aupadeshika=root_slp1, gana=gana_enum
                            ),
                            prayoga=prayoga_enum,
                            lakara=lakara_enum,
                            purusha=p_enum,
                            vacana=v_enum,
                        )
                    )
                except Exception as exc:
                    errors.append(
                        {
                            "cell": key,
                            "stage": "derive",
                            "error": "%s: %s" % (type(exc).__name__, exc),
                        }
                    )
                    if strict:
                        raise
                    paradigm[p_label][v_label] = None
                    counts[key] = 0
                    continue

                if not prakriyas:
                    paradigm[p_label][v_label] = None
                    counts[key] = 0
                    continue

                best = prakriyas[0]
                counts[key] = len(prakriyas)

                try:
                    paradigm[p_label][v_label] = self.from_slp1(
                        best.text, output_script
                    )
                except Exception as exc:
                    errors.append(
                        {
                            "cell": key,
                            "stage": "transliterate",
                            "slp1": str(best.text),
                            "error": "%s: %s" % (type(exc).__name__, exc),
                        }
                    )
                    if strict:
                        raise
                    paradigm[p_label][v_label] = None
                    continue

                if include_traces:
                    traces[key] = [self._step_to_dict(s) for s in best.history]

        return {
            "root": root,
            "root_slp1": root_slp1,
            "gana": gana,
            "lakara": lakara_key,
            "prayoga": prayoga_key,
            "input_script": input_script,
            "output_script": output_script,
            "paradigm": paradigm,
            "alternate_counts": counts,
            "sutra_traces": traces if include_traces else {},
            "errors": errors,
        }