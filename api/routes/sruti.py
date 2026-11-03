from fastapi import APIRouter, Query
from typing import Dict, Any
import _sruti

router = APIRouter(prefix="/api/v1", tags=["Gāndharvaveda / 22-Śruti Matrix"])

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
