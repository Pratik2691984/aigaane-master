"""
Chandas (meter) domain routes.

Exposes Piṅgala-style L/G scansion and meter classification:

  POST /chandas/scan   → full scansion: L/G pattern + mātrā + meter
  POST /chandas/analyze → meter classification only (lighter)
  GET  /chandas/probe   → module availability

Backed by `_chhandas.analyze_verse` and `_chhandas_scanner.scan_iast`.
"""
import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(tags=["chandas"])

try:
    import _chhandas
    _CHHANDAS_OK = True
except Exception:
    _chhandas = None
    _CHHANDAS_OK = False

try:
    import _chhandas_scanner
    _SCANNER_OK = True
except Exception:
    _chhandas_scanner = None
    _SCANNER_OK = False

try:
    import _script
    _SCRIPT_OK = True
except Exception:
    _script = None
    _SCRIPT_OK = False


class ChandasScanRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Verse in IAST with diacritics, or Devanagari")


def _to_iast(text: str) -> str:
    """Convert input to IAST (required by chandas modules)."""
    if not _SCRIPT_OK or not hasattr(_script, "to_canonical_iast"):
        return text
    try:
        result = _script.to_canonical_iast(text)
        if isinstance(result, tuple):
            return result[1] if len(result) > 1 else text
        return str(result)
    except Exception:
        return text


def _compute_matra(weights: List[str]) -> int:
    """Mātrā sum: L=1, G=2."""
    return sum(2 if w == "G" else 1 for w in weights)


@router.post("/scan")
async def scan_chandas(payload: ChandasScanRequest):
    """
    Full Piṅgala scansion:
      - L/G weight per syllable
      - mātrā sum (L=1, G=2)
      - meter classification (Anuṣṭubh, Triṣṭubh, etc.)
      - pāda structure
    """
    if not _SCANNER_OK and not _CHHANDAS_OK:
        raise HTTPException(status_code=503, detail="No chandas module available")

    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty input")

    iast = _to_iast(text)

    weights: List[str] = []
    meter_info: Optional[dict] = None
    errors: List[str] = []

    if _SCANNER_OK and hasattr(_chhandas_scanner, "scan_iast"):
        try:
            result = _chhandas_scanner.scan_iast(iast)
            if isinstance(result, list):
                weights = [str(w) for w in result]
        except Exception as e:
            errors.append(f"scanner: {e}")

    if _CHHANDAS_OK and hasattr(_chhandas, "analyze_verse"):
        try:
            info = _chhandas.analyze_verse(iast)
            if isinstance(info, dict):
                meter_info = info
        except Exception as e:
            errors.append(f"analyze: {e}")

    return {
        "surface": text,
        "iast": iast,
        "weights": weights,
        "syllable_count": len(weights),
        "matra_sum": _compute_matra(weights) if weights else 0,
        "meter": meter_info,
        "errors": errors if errors else None,
    }


@router.post("/analyze")
async def analyze_chandas(payload: ChandasScanRequest):
    """Meter classification only — lighter than /scan."""
    if not _CHHANDAS_OK:
        raise HTTPException(status_code=503, detail="Chandas analyzer unavailable")

    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty input")

    iast = _to_iast(text)
    try:
        result = _chhandas.analyze_verse(iast)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analyze failed: {e}")

    if not result:
        return {"surface": text, "iast": iast, "found": False, "meter": None}

    return {
        "surface": text,
        "iast": iast,
        "found": True,
        "meter": result,
    }


@router.get("/probe")
async def chandas_probe():
    return {
        "chhandas_ok": _CHHANDAS_OK,
        "scanner_ok": _SCANNER_OK,
        "script_ok": _SCRIPT_OK,
        "has_analyze_verse": _CHHANDAS_OK and hasattr(_chhandas, "analyze_verse"),
        "has_scan_iast": _SCANNER_OK and hasattr(_chhandas_scanner, "scan_iast"),
    }