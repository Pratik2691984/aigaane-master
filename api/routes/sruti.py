from typing import Dict, Any, List
from fastapi import APIRouter, Query, Response
from pydantic import BaseModel, Field
import _sruti

router = APIRouter(prefix="/api/v1", tags=["Gāndharvaveda / 22-Śruti Matrix"])

class SrutiMidiRequest(BaseModel):
    svaras: List[str] = Field(default=["S", "R2", "G2", "M1", "P", "D2", "N2", "S"], description="List of svara symbols")
    sa_hz: float = Field(default=240.0, description="Fundamental Sa frequency in Hz")
    sa_midi_note: int = Field(default=60, description="MIDI base note for Sa (60 = C4)")
    tempo_bpm: int = Field(default=72, description="Tempo in beats per minute")

SrutiMidiRequest.model_rebuild()


@router.get("/sruti", summary="Retrieve 22-Śruti microtonal tuning matrix")
async def get_sruti_matrix(sa_hz: float = Query(240.0, description="Fundamental frequency for Sa in Hz")) -> Dict[str, Any]:
    """
    Returns the complete canonical 22-Śruti tuning matrix including
    integer ratios, frequencies in Hz, exact cents, and 12-TET microtonal deviations.
    """
    table = _sruti.get_sruti_table(sa_hz=sa_hz)
    return {
        "sa_hz": sa_hz,
        "total_srutis": len(table),
        "pramana_sruti_cents": 21.51,
        "tuning_system": "Bharata Natyashastra / Sarangadeva Sangita-Ratnakara (Sa-Pa / Sa-Ma Samvada)",
        "intervals": table
    }


@router.get("/sruti/{svara}", summary="Lookup microtonal properties of an individual svara")
async def get_svara_detail(svara: str, sa_hz: float = Query(240.0, description="Fundamental frequency for Sa in Hz")) -> Dict[str, Any]:
    res = _sruti.lookup_svara(svara, sa_hz=sa_hz)
    if not res:
        return {"error": f"Svara symbol or name '{svara}' not found in 22-Śruti matrix."}
    return res


@router.post("/sruti/midi/export", summary="Export 22-Śruti microtonal melody as standard MIDI file")
async def export_sruti_midi(req: SrutiMidiRequest):
    """
    Encodes an exact 22-Śruti microtonal scale or phrase into a downloadable
    MIDI (.mid) binary payload with embedded pitch-wheel messages.
    """
    midi_bytes = _sruti.generate_sruti_midi(
        svara_sequence=req.svaras,
        sa_midi_note=req.sa_midi_note,
        sa_hz=req.sa_hz,
        tempo_bpm=req.tempo_bpm
    )
    return Response(
        content=midi_bytes,
        media_type="audio/midi",
        headers={"Content-Disposition": "attachment; filename=aigaane_22_sruti_microtonal.mid"}
    )
