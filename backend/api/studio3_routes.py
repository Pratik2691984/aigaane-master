"""
Studio III — Mathematical Acoustics domain routes.

Exposes the 22-śruti Just Intonation table, JI ratio math, and MIDI generation.

Backed by `_sruti.py`:
  - get_sruti_table()           → 22 entries with name, svara, ratio, cents, hz
  - SRUTI_CANONICAL             → integer ratios (ratio_num/ratio_den)
  - ratio_to_cents(num, den)    → cents conversion (two positional args)
  - lookup_svara(svara_symbol)  → ratio info for a swara
  - generate_sruti_midi(svara_sequence, ...) → MIDI bytes

NOTE: Tāla congruence (3P + 2D + t_start ≡ 17 mod C) is NOT in the current
codebase. Deferred to v2.0 as a documented target — see audit-findings.md.
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
        "Aigaane · Gandharvaveda",
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
        "tala_congruence": "not implemented (deferred to v2.0)",
    }