import re
from fastapi import FastAPI, HTTPException
from api.schemas.prosody import ProsodyScanRequest, ProsodyScanResponse, PadaScanResult, ProsodyDiagnostic, ProsodyTraceStep
from engine.prosody.chandas import (
    scan_anustubh, 
    scan_upajati, 
    scan_varnavrtta_pada, 
    METER_SCHEMAS
)

app = FastAPI(title="Aigaane Sanskrit Kernel API", version="3.0.0")
handler = app  # Required for api/index.py serverless bridge

@app.post("/api/v3/prosody/scan", response_model=ProsodyScanResponse)
def scan_prosody_endpoint(req: ProsodyScanRequest):
    chandas_clean = (req.chandas or "anustubh").strip().lower()
    
    if chandas_clean == "anustubh":
        report = scan_anustubh(req.text, padanta_guru=req.padanta_guru)
        return ProsodyScanResponse(
            valid=report["valid"],
            chandas=report["chandas"],
            variant=report.get("variant"),
            padas=report["padas"],
            diagnostics=report["diagnostics"],
            trace=report["trace"],
            governance=report["governance"]
        )

    elif chandas_clean in ["upajati", "indravajra", "upendravajra"]:
        report = scan_upajati(req.text, padanta_guru=req.padanta_guru)
        trace_steps = [
            ProsodyTraceStep(
                rule="upajati-line-match",
                pada=p["pada_number"],
                syllable=p["total_syllables"],
                found=p["weights"][-1] if p["weights"] else "L",
                ok=p["valid"]
            )
            for p in report["padas"]
        ]
        return ProsodyScanResponse(
            valid=report["valid"],
            chandas=report["chandas"],
            variant=report.get("variant"),
            padas=report["padas"],
            diagnostics=report["diagnostics"],
            trace=trace_steps,
            governance=report["governance"]
        )

    elif chandas_clean in METER_SCHEMAS:
        split_pat = chr(13) + chr(10) + "/|।॥"
        lines = [ln.strip() for ln in re.split(f"[{split_pat}]+", req.text) if ln.strip()]
        padas = []
        all_diags = []
        all_valid = True
        
        for idx, line in enumerate(lines[:4], 1):
            pada_res, pada_diags = scan_varnavrtta_pada(line, idx, chandas_clean, req.padanta_guru)
            padas.append(pada_res)
            if not pada_res["valid"]:
                all_valid = False
            all_diags.extend(pada_diags)
            
        trace_steps = [
            ProsodyTraceStep(
                rule=f"{chandas_clean}-scan",
                pada=p["pada_number"],
                syllable=p["total_syllables"],
                found=p["weights"][-1] if p["weights"] else "L",
                ok=p["valid"]
            )
            for p in padas
        ]
        
        return ProsodyScanResponse(
            valid=all_valid and len(padas) > 0,
            chandas=chandas_clean,
            variant="samavṛtta",
            padas=padas,
            diagnostics=all_diags,
            trace=trace_steps,
            governance={
                "engine": "engine.prosody.chandas",
                "authority": "Piṅgala Chhandaḥśāstra"
            }
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported meter '{req.chandas}'. Supported: anustubh, upajati, indravajra, upendravajra, shardulavikridita"
        )
