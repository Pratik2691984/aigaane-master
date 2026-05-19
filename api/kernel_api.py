# C:\aigaane-master\api\kernel_api.py
# Vercel‑compatible ASGI handler (using Mangum) – WebSockets disabled, routes prefixed with /api

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
import sys
import unicodedata

try:
    from mangum import Mangum
except ImportError:
    Mangum = None

sys.path.insert(0, os.path.dirname(__file__))
from engines.anumana import calculate_friction
from engines.morphology import (
    MorphologyException,
    conjugate_verb,
    inflect_noun,
    morphology_meta,
)
from engines.sandhi import SandhiException, analyze_vowel_sandhi
from engines.visarga_sandhi import VisargaSandhiException, analyze_visarga_sandhi
from engines.vyakarana import SanskritTabException, analyze_sanskrit

app = FastAPI(
    title="Aigaane Sanskrit Engine",
    version="3.0",
    default_response_class=JSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Data Models (unchanged) ============
class Vector49D(BaseModel):
    spatial: List[float]
    temporal: List[float]
    planetary: List[float]
    guna: List[float]
    energy: List[float]
    biological: List[float]
    stellar: List[float]

class KernelState(BaseModel):
    timestamp: str
    nakshatra: str
    pada: int
    cosmic_angle: float
    sruti_ratio: float
    vector_data: Vector49D
    primary_guna: str
    status: str

class GoldenBuildMetadata(BaseModel):
    build_name: str
    pada: int
    cosmic_angle: float
    emission_model: str
    timestamp: str
    version: str = "3.0_PRO"

class GoldenBuildConstraints(BaseModel):
    planetary_mean: float
    target_sruti: float
    target_nakshatra: str
    target_pada: int

class GoldenBuildData(BaseModel):
    metadata: GoldenBuildMetadata
    vector: List[float]
    constraints: GoldenBuildConstraints
    status: str = "OPTIMAL"
    direction: str = "→ Forward"
    phase_lock: str = "LOCKED"

class AtmaFrictionRequest(BaseModel):
    solar_time: float
    lunar_velocity: float = 1.0
    user_action: str
    current_dosha: str
    agni_factor: float
    cosmic_angle: float = 0.0

class SanskritAnalyzeRequest(BaseModel):
    input_text: str

class SandhiAnalyzeRequest(BaseModel):
    word1: str
    word2: str

class SandhiTraceStep(BaseModel):
    layer: str
    word1: Optional[str] = None
    word2: Optional[str] = None
    left_vowel: Optional[str] = None
    right_vowel: Optional[str] = None
    left_visarga: Optional[str] = None
    preceding_vowel: Optional[str] = None
    right_initial: Optional[str] = None
    right_class: Optional[str] = None
    sutra: Optional[str] = None
    merged: Optional[str] = None

class DerivationPathStep(BaseModel):
    sutra: str
    sutra_name: str
    operation: str
    input_state: str
    output_state: str
    engine_node: str

class SandhiAnalyzeResponse(BaseModel):
    merged: str
    sutra: str
    sutra_name: str
    type: str
    trace: List[SandhiTraceStep]
    derivation_path: Optional[List[DerivationPathStep]] = None

class MorphologyNounRequest(BaseModel):
    stem: str
    case: str
    number: str

class MorphologyVerbRequest(BaseModel):
    dhatu: str
    lakara: str
    person: str
    number: str

class MorphologyResponse(BaseModel):
    type: str
    input: Dict[str, str]
    form: str
    metadata: Dict[str, Any]
    rule: Dict[str, Any]
    derivation_path: Optional[List[DerivationPathStep]] = None

class MorphologyMetaResponse(BaseModel):
    engine: str
    phase: str
    scope: Dict[str, List[str]]
    nouns: List[Dict[str, Any]]
    dhatus: List[Dict[str, Any]]

# ============ Storage ============
current_state: Optional[KernelState] = None
history_states: List[KernelState] = []
golden_builds: List[Dict[str, Any]] = []
current_golden_build: Optional[Dict[str, Any]] = None

# ============ WebSocket disabled for Vercel ============
manager = None

# ============ Helper Functions ============
def vector_to_list(v: Vector49D) -> List[float]:
    return v.spatial + v.temporal + v.planetary + v.guna + v.energy + v.biological + v.stellar

def list_to_vector(vector: List[float]) -> Vector49D:
    return Vector49D(
        spatial=vector[0:7], temporal=vector[7:14], planetary=vector[14:21],
        guna=vector[21:28], energy=vector[28:35], biological=vector[35:42], stellar=vector[42:49]
    )

# ============ Core Endpoints (now under /api) ============
@app.get("/api/kernel/v3/current")
async def get_current_kernel():
    if current_state is None:
        raise HTTPException(status_code=404, detail="No kernel state available")
    return current_state

@app.post("/api/kernel/v3/update")
async def update_kernel(state: KernelState):
    global current_state
    current_state = state
    history_states.append(state)
    while len(history_states) > 108:
        history_states.pop(0)
    return {"status": "updated", "timestamp": state.timestamp}

@app.get("/api/kernel/v3/history")
async def get_history(limit: int = 50):
    return history_states[-limit:]

@app.get("/api/kernel/v3/compare")
async def compare_states(index_a: int = -2, index_b: int = -1):
    if len(history_states) < 2:
        raise HTTPException(status_code=404, detail="Not enough history")
    state_a, state_b = history_states[index_a], history_states[index_b]
    vec_a, vec_b = vector_to_list(state_a.vector_data), vector_to_list(state_b.vector_data)
    deltas = [vec_b[i] - vec_a[i] for i in range(49)]
    avg_delta = sum(abs(d) for d in deltas) / 49
    return {
        "state_a": {"angle": state_a.cosmic_angle, "pada": state_a.pada, "nakshatra": state_a.nakshatra},
        "state_b": {"angle": state_b.cosmic_angle, "pada": state_b.pada, "nakshatra": state_b.nakshatra},
        "avg_vector_delta": avg_delta,
        "angle_delta": state_b.cosmic_angle - state_a.cosmic_angle,
        "deltas": deltas[:10]
    }

# ============ Golden Build Endpoints (under /api) ============
@app.post("/api/kernel/v3/golden/build")
async def create_golden_build(data: GoldenBuildData):
    global current_golden_build, golden_builds
    build_data = data.dict()
    build_id = f"gb_{len(golden_builds) + 1:04d}"
    build_data["id"] = build_id
    build_data["created_at"] = datetime.now().isoformat()
    golden_builds.append(build_data)
    current_golden_build = build_data
    return {"status": "created", "id": build_id}

@app.get("/api/kernel/v3/golden/current")
async def get_current_golden_build():
    if current_golden_build is None:
        raise HTTPException(status_code=404, detail="No Golden Build set")
    return current_golden_build

@app.get("/api/kernel/v3/golden/list")
async def list_golden_builds():
    return golden_builds

@app.delete("/api/kernel/v3/golden/{build_id}")
async def delete_golden_build(build_id: str):
    global golden_builds, current_golden_build
    for i, build in enumerate(golden_builds):
        if build.get("id") == build_id:
            del golden_builds[i]
            if current_golden_build and current_golden_build.get("id") == build_id:
                current_golden_build = None
            return {"status": "deleted", "id": build_id}
    raise HTTPException(status_code=404, detail="Golden Build not found")

# ============ Health & Info (under /api) ============
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.0_PRO",
        "golden_builds": len(golden_builds),
        "history_states": len(history_states),
        "active_connections": 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/info")
async def server_info():
    return {
        "version": "3.0_PRO",
        "name": "Aigaane V3 PRO",
        "golden_build_active": current_golden_build is not None,
        "total_golden_builds": len(golden_builds),
        "total_history_states": len(history_states),
        "current_golden_build": current_golden_build.get("metadata", {}).get("build_name") if current_golden_build else None
    }

@app.post("/api/calculate-friction")
async def calculate_atma_friction(payload: AtmaFrictionRequest):
    return calculate_friction(
        user_action=payload.user_action,
        current_dosha=payload.current_dosha,
        agni_factor=payload.agni_factor,
        solar_time=payload.solar_time,
        lunar_velocity=payload.lunar_velocity,
        cosmic_angle=payload.cosmic_angle,
    )

@app.post("/api/atma/calculate-friction")
async def calculate_atma_friction_alias(payload: AtmaFrictionRequest):
    return await calculate_atma_friction(payload)

@app.post("/api/v3/analyze")
async def analyze_sanskrit_v3(payload: SanskritAnalyzeRequest):
    try:
        return JSONResponse(
            content=analyze_sanskrit(payload.input_text),
            media_type="application/json; charset=utf-8",
        )
    except SanskritTabException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": exc.message,
                "parser_diagnostics": exc.diagnostics,
            },
        ) from exc

@app.options("/api/v3/analyze")
async def analyze_sanskrit_v3_options():
    return {"allow": "POST, OPTIONS", "headers": "Content-Type"}

@app.post("/api/v3/sandhi", response_model=SandhiAnalyzeResponse)
async def analyze_sandhi_v3(payload: SandhiAnalyzeRequest):
    try:
        word1 = unicodedata.normalize("NFC", payload.word1.strip()) if isinstance(payload.word1, str) else payload.word1
        if isinstance(word1, str) and word1.endswith("\u0903"):
            return JSONResponse(
                content=analyze_visarga_sandhi(payload.word1, payload.word2),
                media_type="application/json; charset=utf-8",
            )
        return JSONResponse(
            content=analyze_vowel_sandhi(payload.word1, payload.word2),
            media_type="application/json; charset=utf-8",
        )
    except VisargaSandhiException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc
    except SandhiException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc

@app.options("/api/v3/sandhi")
async def analyze_sandhi_v3_options():
    return {"allow": "POST, OPTIONS", "headers": "Content-Type"}

@app.get("/api/v3/morphology/meta", response_model=MorphologyMetaResponse)
async def morphology_meta_v3():
    return JSONResponse(
        content=morphology_meta(),
        media_type="application/json; charset=utf-8",
    )

@app.post("/api/v3/morphology/noun/inflect", response_model=MorphologyResponse)
async def inflect_noun_v3(payload: MorphologyNounRequest):
    try:
        return JSONResponse(
            content=inflect_noun(payload.stem, payload.case, payload.number),
            media_type="application/json; charset=utf-8",
        )
    except MorphologyException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc

@app.post("/api/v3/morphology/verb/conjugate", response_model=MorphologyResponse)
async def conjugate_verb_v3(payload: MorphologyVerbRequest):
    try:
        return JSONResponse(
            content=conjugate_verb(payload.dhatu, payload.lakara, payload.person, payload.number),
            media_type="application/json; charset=utf-8",
        )
    except MorphologyException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc

# ============ Startup: load Golden Build from file ============
@app.on_event("startup")
async def startup_event():
    golden_build_path = os.path.join(os.path.dirname(__file__), "..", "golden_build_chitra_53.json")
    if os.path.exists(golden_build_path):
        try:
            with open(golden_build_path, 'r', encoding='utf-8') as f:
                golden_data = json.load(f)
            metadata = golden_data.get("metadata", {})
            constraints = golden_data.get("constraints", {})
            build_data = GoldenBuildData(
                metadata=GoldenBuildMetadata(**metadata),
                vector=golden_data.get("vector", []),
                constraints=GoldenBuildConstraints(**constraints),
                status=golden_data.get("status", "OPTIMAL"),
                direction=golden_data.get("direction", "→ Forward"),
                phase_lock=golden_data.get("phase_lock", "LOCKED")
            )
            await create_golden_build(build_data)
            print(f"[Startup] ✅ Loaded Golden Build from {golden_build_path}")
        except Exception as e:
            print(f"[Startup] ⚠️ Failed to load Golden Build: {e}")

# ============ Vercel Handler ============
handler = Mangum(app) if Mangum else None
