# C:\aigaane-master\api\kernel_api.py
# Vercel‑compatible ASGI handler (using Mangum) – WebSockets disabled, routes prefixed with /api

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
import sys

try:
    from mangum import Mangum
except ImportError:
    Mangum = None

sys.path.insert(0, os.path.dirname(__file__))
from engines.anumana import calculate_friction
from engines.vyakarana import SanskritTabException, analyze_sanskrit

app = FastAPI(title="Aigaane 49D Kernel API", version="3.0")

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
        return analyze_sanskrit(payload.input_text)
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
