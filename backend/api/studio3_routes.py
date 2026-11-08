"""
Studio III — Mathematical Acoustics domain routes.

Exposes the 22-śruti Just Intonation table, JI ratio math, MIDI generation,
and (v2.0) tāla congruence validation.

Backed by `_sruti.py`:
  - get_sruti_table()           → 22 entries with name, svara, ratio, cents, hz
  - SRUTI_CANONICAL             → integer ratios (ratio_num/ratio_den)
  - ratio_to_cents(num, den)    → cents conversion (two positional args)
  - lookup_svara(svara_symbol)  → ratio info for a swara
  - generate_sruti_midi(svara_sequence, ...) → MIDI bytes

Backed by `_tala.py` (v2.0):
  - TALA_REGISTRY               → Carnatic tāla registry
  - lookup_tala(name)           → TalaSpec or None
  - list_talas()                → JSON-friendly list
  - check_congruence(...)       → 3P + 2D + L + t_start ≡ 17 (mod C)
  - suggest_correction(...)     → minimal adjustments for non-congruent phrases
"""
import sys
import base64
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List

router = APIRouter(tags=["studio3"])

try:
    import _sruti
    _SRUTI_OK = True
except Exception:
    _sruti = None
    _SRUTI_OK = False

try:
    import _tala
    _TALA_OK = True
except Exception:
    _tala = None
    _TALA_OK = False


# Default verse title.
# NOTE: \u00b7 is the middle dot "·" (U+00B7). Written as an escape so the
# value is correct even if this source file is ever saved as Latin-1/CP1252,
# which would otherwise produce the "Â·" mojibake seen in v1.5.5 output.
DEFAULT_VERSE_TITLE = "Aigaane \u00b7 Gandharvaveda"


# ------------------------------------------------------------------ #
#   GET endpoints — read-only reference data                         #
# ------------------------------------------------------------------ #

@router.get("/sruti/ratios")
async def get_sruti_ratios():
    """
    Returns the complete 22-śruti Just Intonation table.

    Each entry contains:
      index, name (śruti name), svara, svara_symbol,
      ratio (fraction string), frequency_hz, cents, tet_deviation_cents
    """
    if not _SRUTI_OK:
        raise HTTPException(status_code=503, detail="_sruti module unavailable")

    try:
        table = _sruti.get_sruti_table()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"get_sruti_table failed: {e}")

    return {
        "count": len(table),
        "anchor_hz": 240.0,
        "ratios": table,
    }


@router.get("/sruti/canonical")
async def get_sruti_canonical():
    """
    Returns the 22-śruti table with integer ratios (ratio_num / ratio_den)
    for exact arithmetic. Same data as /sruti/ratios but with rational form.
    """
    if not _SRUTI_OK:
        raise HTTPException(status_code=503, detail="_sruti module unavailable")

    try:
        canonical = _sruti.SRUTI_CANONICAL
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SRUTI_CANONICAL failed: {e}")

    return {
        "count": len(canonical),
        "ratios": canonical,
    }


@router.get("/sruti/cents")
async def ratio_to_cents_endpoint(
    ratio: str = Query(..., description="JI ratio as 'num/den', e.g. '256/243'"),
):
    """
    Convert a Just Intonation ratio to cents from Ṣaḍja.

    Accepts fraction string, e.g. ?ratio=256/243
    Example: 256/243 → ~90.22 cents
    """
    if not _SRUTI_OK:
        raise HTTPException(status_code=503, detail="_sruti module unavailable")

    try:
        parts = ratio.split("/")
        if len(parts) != 2:
            raise ValueError(f"Ratio must be 'num/den', got '{ratio}'")
        num = int(parts[0])
        den = int(parts[1])
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid ratio format '{ratio}': {e}")

    try:
        cents = _sruti.ratio_to_cents(num, den)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ratio_to_cents({num}, {den}) failed: {e}")

    return {
        "ratio": ratio,
        "num": num,
        "den": den,
        "cents": round(float(cents), 4),
    }


@router.get("/sruti/lookup")
async def lookup_svara_endpoint(
    svara: str = Query(..., description="Svara symbol, e.g. 'S', 'r1', 'R1', 'P'")
):
    """
    Look up a swara's JI ratio and cents.

    Accepts svara_symbol values: S, r1, r2, R1, R2, g1, g2, G1, G2,
    m1, m2, M1, M2, P, d1, d2, D1, D2, n1, n2, N1, N2.
    """
    if not _SRUTI_OK:
        raise HTTPException(status_code=503, detail="_sruti module unavailable")

    try:
        result = _sruti.lookup_svara(svara)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"lookup_svara failed: {e}")

    if not result:
        return {"svara": svara, "found": False, "analysis": None}

    return {"svara": svara, "found": True, "analysis": result}


# ------------------------------------------------------------------ #
#   POST endpoint — MIDI generation                                  #
# ------------------------------------------------------------------ #

class MidiExportRequest(BaseModel):
    swaras: List[str] = Field(
        ...,
        min_length=1,
        description="List of svara symbols (e.g. ['S', 'R1', 'G1', 'm1', 'P'])",
    )
    sa_midi_note: int = Field(60, ge=0, le=127, description="MIDI note for Sa anchor")
    sa_hz: float = Field(240.0, gt=0.0, description="Reference frequency for Sa (Hz)")
    tempo_bpm: int = Field(80, ge=20, le=400)
    include_tanpura: bool = Field(True, description="Add tanpura drone track")
    verse_title: str = Field(
        DEFAULT_VERSE_TITLE,
        max_length=80,
        description="Title embedded in the MIDI metadata",
    )


@router.post("/midi/export")
async def export_midi(payload: MidiExportRequest):
    """
    Generate a Studio III Type-1 Multi-Track MIDI binary from a swara sequence.

    Returns base64-encoded MIDI bytes so the frontend can download
    or play directly via Web Audio API.

    `_sruti.generate_sruti_midi` returns bytes directly — no temp file needed.
    """
    if not _SRUTI_OK:
        raise HTTPException(status_code=503, detail="_sruti module unavailable")

    if not hasattr(_sruti, "generate_sruti_midi"):
        raise HTTPException(status_code=503, detail="generate_sruti_midi unavailable")

    try:
        midi_bytes = _sruti.generate_sruti_midi(
            svara_sequence=payload.swaras,
            sa_midi_note=payload.sa_midi_note,
            sa_hz=payload.sa_hz,
            tempo_bpm=payload.tempo_bpm,
            include_tanpura=payload.include_tanpura,
            verse_title=payload.verse_title,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MIDI generation failed: {e}")

    if not midi_bytes:
        raise HTTPException(status_code=500, detail="MIDI generation returned empty bytes")

    encoded = base64.b64encode(midi_bytes).decode("ascii")

    return {
        "swaras": payload.swaras,
        "tempo_bpm": payload.tempo_bpm,
        "sa_hz": payload.sa_hz,
        "sa_midi_note": payload.sa_midi_note,
        "include_tanpura": payload.include_tanpura,
        "verse_title": payload.verse_title,
        "size_bytes": len(midi_bytes),
        "encoding": "base64",
        "midi_base64": encoded,
        "download_filename": f"studio3_{len(payload.swaras)}swaras.mid",
    }


# ------------------------------------------------------------------ #
#   v2.0 — Tāla congruence                                           #
# ------------------------------------------------------------------ #

@router.get("/tala/list")
async def tala_list():
    """Full Carnatic tāla registry with cycle lengths."""
    if not _TALA_OK:
        raise HTTPException(status_code=503, detail="_tala module unavailable")
    return {"count": len(_tala.TALA_REGISTRY), "talas": _tala.list_talas()}


@router.get("/tala/lookup")
async def tala_lookup(
    name: str = Query(..., description="Tāla name, e.g. 'adi', 'misra_chapu'")
):
    """Look up a single tāla by name (case-insensitive)."""
    if not _TALA_OK:
        raise HTTPException(status_code=503, detail="_tala module unavailable")
    spec = _tala.lookup_tala(name)
    if spec is None:
        return {"name": name, "found": False, "spec": None}
    return {"name": name, "found": True, "spec": spec.__dict__}


class CongruenceRequest(BaseModel):
    pluta_count: int = Field(..., ge=0, description="P — number of pluta syllables")
    dirgha_count: int = Field(..., ge=0, description="D — number of dīrgha syllables")
    cycle_length: int = Field(
        ..., ge=1, le=64, description="C — tāla cycle length (aksharas)"
    )
    t_start: int = Field(0, ge=0, description="Starting offset within cycle")
    laghu_count: int = Field(
        0, ge=0, description="L — optional extension (default 0 = strict formula)"
    )
    sam_anchor: int = Field(17, description="Anchor constant (canonical: 17)")


class CongruenceByTalaRequest(BaseModel):
    pluta_count: int = Field(..., ge=0)
    dirgha_count: int = Field(..., ge=0)
    tala_name: str = Field(..., description="e.g. 'adi', 'misra_chapu'")
    t_start: int = Field(0, ge=0)
    laghu_count: int = Field(0, ge=0)
    sam_anchor: int = Field(17)


@router.post("/tala/congruence")
async def tala_congruence(payload: CongruenceRequest):
    """
    Check 3P + 2D + L + t_start ≡ sam_anchor (mod C).

    Default `laghu_count=0` and `sam_anchor=17` reproduces the documented
    audit-findings formula exactly.
    """
    if not _TALA_OK:
        raise HTTPException(status_code=503, detail="_tala module unavailable")
    try:
        result = _tala.check_congruence(
            pluta_count=payload.pluta_count,
            dirgha_count=payload.dirgha_count,
            cycle_length=payload.cycle_length,
            t_start=payload.t_start,
            laghu_count=payload.laghu_count,
            sam_anchor=payload.sam_anchor,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result.to_dict()


@router.post("/tala/congruence/by-tala")
async def tala_congruence_by_name(payload: CongruenceByTalaRequest):
    """Same as /tala/congruence, but resolves C from a named tāla."""
    if not _TALA_OK:
        raise HTTPException(status_code=503, detail="_tala module unavailable")
    spec = _tala.lookup_tala(payload.tala_name)
    if spec is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown tāla: '{payload.tala_name}'"
        )
    try:
        result = _tala.check_congruence(
            pluta_count=payload.pluta_count,
            dirgha_count=payload.dirgha_count,
            cycle_length=spec.cycle_length,
            t_start=payload.t_start,
            laghu_count=payload.laghu_count,
            sam_anchor=payload.sam_anchor,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"tala": spec.__dict__, "result": result.to_dict()}


@router.post("/tala/suggest")
async def tala_suggest(payload: CongruenceRequest):
    """
    If the phrase is not congruent, suggest minimal corrections
    (laghu adjustments, t_start shift, or alternative cycle lengths).
    """
    if not _TALA_OK:
        raise HTTPException(status_code=503, detail="_tala module unavailable")
    try:
        return _tala.suggest_correction(
            pluta_count=payload.pluta_count,
            dirgha_count=payload.dirgha_count,
            cycle_length=payload.cycle_length,
            t_start=payload.t_start,
            laghu_count=payload.laghu_count,
            sam_anchor=payload.sam_anchor,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------------------------------------------------------ #
#   Probe                                                            #
# ------------------------------------------------------------------ #

@router.get("/probe")
async def studio3_probe():
    return {
        "sruti_ok": _SRUTI_OK,
        "has_get_sruti_table": _SRUTI_OK and hasattr(_sruti, "get_sruti_table"),
        "has_ratio_to_cents": _SRUTI_OK and hasattr(_sruti, "ratio_to_cents"),
        "has_lookup_svara": _SRUTI_OK and hasattr(_sruti, "lookup_svara"),
        "has_generate_sruti_midi": _SRUTI_OK and hasattr(_sruti, "generate_sruti_midi"),
        "has_cents_to_midi_pitch_bend": _SRUTI_OK and hasattr(_sruti, "cents_to_midi_pitch_bend"),
        "tala_ok": _TALA_OK,
        "has_check_congruence": _TALA_OK and hasattr(_tala, "check_congruence"),
        "tala_congruence": "implemented (v2.0)",
    }