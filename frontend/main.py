from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import uvicorn

from aigaane.chandas import scan_iast
from aigaane.tala import align_to_tala
from aigaane.raga import assign_svaras
from aigaane.midi import assign_timings
from aigaane.synth import render_to_wav

app = FastAPI(title="Aigaane Gandharva API")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MantraRequest(BaseModel):
    text: str
    reference_hz: float = 146.83
    akshara_duration_s: float = 0.5

@app.post("/api/v1/gandharva/render")
def render_mantra(req: MantraRequest):
    try:
        weights = scan_iast(req.text)
        if not weights:
            raise HTTPException(status_code=400, detail="Could not scan text. Ensure IAST format.")
            
        aligned = align_to_tala(weights, "adi")
        svaras = assign_svaras(aligned, "mayamalavagowla")
        timed = assign_timings(svaras, req.akshara_duration_s)
        
        filename = f"{uuid.uuid4().hex}.wav"
        render_to_wav(timed, "mayamalavagowla", req.reference_hz, filename)
        
        return {"status": "success", "scansion": "".join(weights), "file": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/gandharva/audio/{filename}")
def get_audio(filename: str):
    if os.path.exists(filename):
        return FileResponse(filename, media_type="audio/wav")
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
