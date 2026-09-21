"""
api/kernel_api.py
Unified FastAPI Application for Aigaane Engine

Includes:
  - 49D Kernel, Atma Friction & V3 Derivation Routes
  - Classical Sanskrit Prosody Scansion Engine (Piṅgala Chhandaḥśāstra)
  - Track B Phonology (sandhi) and Chandas scanners
  - Vercel ASGI Handler (Mangum)
"""
import re
import os
import sys
import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from mangum import Mangum
except ImportError:
    Mangum = None

# ────────────────────────────────────────────────────────────────
# sys.path setup — api/ first, repo root as fallback
# ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))                     # api/ (priority)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))       # repo root (fallback)

# ────────────────────────────────────────────────────────────────
# Local imports
# ────────────────────────────────────────────────────────────────
# calculate_friction lives in api/engines/anumana.py — import by absolute path
try:
    from api.engines.anumana import calculate_friction
except ImportError:
    try:
        from engines.anumana import calculate_friction
    except ImportError:
        def calculate_friction(*args, **kwargs):
            return {"error": "calculate_friction not available"}
from v3_derivation import router as v3_router

# Track B routers (corrected Pāṇinian phonology & chandas)
from routers.sandhi import router as sandhi_router
from routers.chandas import router as chandas_router

# Prosody Engine imports
from api.schemas.prosody import (
    ProsodyScanRequest,
    ProsodyScanResponse,
    PadaScanResult,
    ProsodyDiagnostic,
    ProsodyTraceStep,
)
from engine.prosody.chandas import (
    scan_anustubh,
    scan_upajati,
    scan_varnavrtta_pada,
    METER_SCHEMAS,
)


# ────────────────────────────────────────────────────────────────
# Lifespan context — replaces deprecated @app.on_event("startup")
# ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Runs startup logic (load golden build from disk) before yielding,
    then yields to serve requests, then runs shutdown cleanup.
    """
    # ── Startup ──
    golden_build_path = os.path.join(
        os.path.dirname(__file__), "..", "golden_build_chitra_53.json"
    )
    if os.path.exists(golden_build_path):
        try:
            with open(golden_build_path, "r", encoding="utf-8") as f:
                golden_data = json.load(f)
            metadata = golden_data.get("metadata", {})
            constraints = golden_data.get("constraints", {})
            build_data = GoldenBuildData(
                metadata=GoldenBuildMetadata(**metadata),
                vector=golden_data.get("vector", []),
                constraints=GoldenBuildConstraints(**constraints),
                status=golden_data.get("status", "OPTIMAL"),
                direction=golden_data.get("direction", "→ Forward"),
                phase_lock=golden_data.get("phase_lock", "LOCKED"),
            )
            # Persist to the module-level registry
            global current_golden_build, golden_builds
            build_dict = build_data.model_dump()
            build_id = f"gb_{len(golden_builds) + 1:04d}"
            build_dict["id"] = build_id
            build_dict["created_at"] = datetime.now().isoformat()
            golden_builds.append(build_dict)
            current_golden_build = build_dict
            print(f"[Startup] Loaded Golden Build from {golden_build_path}")
        except Exception as e:
            print(f"[Startup] Failed to load Golden Build: {e}")
    else:
        print(f"[Startup] No golden build found at {golden_build_path}")

    yield  # App runs here

    # ── Shutdown ──
    print("[Shutdown] Aigaane kernel shutting down")


# ────────────────────────────────────────────────────────────────
# FastAPI app
# ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Aigaane Unified Kernel API",
    version="3.1.0",
    lifespan=lifespan,
)

# ────────────────────────────────────────────────────────────────
# CORS — restricted to production origins
# ────────────────────────────────────────────────────────────────
_allowed_origins = [
    "https://aigaane.in",
    "https://www.aigaane.in",
    "https://aigaane-sanctuary.web.app",
    "https://aigaane-engine-977695793163.asia-south1.run.app",
]

# Allow localhost during development
if os.environ.get("AIGAANE_ENV") == "development":
    _allowed_origins += [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
    max_age=3600,
)

# ────────────────────────────────────────────────────────────────
# Router mounts
# ────────────────────────────────────────────────────────────────
app.include_router(v3_router)

# Track B mounts
app.include_router(sandhi_router)
app.include_router(chandas_router)


# ════════════════════════════════════════════════════════════════
# 49D KERNEL MODELS & ENDPOINTS
# ════════════════════════════════════════════════════════════════
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


# ────────────────────────────────────────────────────────────────
# Module-level state
# ────────────────────────────────────────────────────────────────
current_state: Optional[KernelState] = None
history_states: List[KernelState] = []
golden_builds: List[Dict[str, Any]] = []
current_golden_build: Optional[Dict[str, Any]] = None


# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────
def vector_to_list(v: Vector49D) -> List[float]:
    return (v.spatial + v.temporal + v.planetary + v.guna
            + v.energy + v.biological + v.stellar)


def list_to_vector(vector: List[float]) -> Vector49D:
    return Vector49D(
        spatial=vector[0:7],
        temporal=vector[7:14],
        planetary=vector[14:21],
        guna=vector[21:28],
        energy=vector[28:35],
        biological=vector[35:42],
        stellar=vector[42:49],
    )


# ────────────────────────────────────────────────────────────────
# Kernel state endpoints
# ────────────────────────────────────────────────────────────────
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
    vec_a = vector_to_list(state_a.vector_data)
    vec_b = vector_to_list(state_b.vector_data)
    deltas = [vec_b[i] - vec_a[i] for i in range(49)]
    avg_delta = sum(abs(d) for d in deltas) / 49
    return {
        "state_a": {
            "angle": state_a.cosmic_angle,
            "pada": state_a.pada,
            "nakshatra": state_a.nakshatra,
        },
        "state_b": {
            "angle": state_b.cosmic_angle,
            "pada": state_b.pada,
            "nakshatra": state_b.nakshatra,
        },
        "avg_vector_delta": avg_delta,
        "angle_delta": state_b.cosmic_angle - state_a.cosmic_angle,
        "deltas": deltas[:10],
    }


# ────────────────────────────────────────────────────────────────
# Golden Build endpoints
# ────────────────────────────────────────────────────────────────
@app.post("/api/kernel/v3/golden/build")
async def create_golden_build(data: GoldenBuildData):
    global current_golden_build, golden_builds
    build_data = data.model_dump()
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


# ────────────────────────────────────────────────────────────────
# Health & info
# ────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.1_PRO",
        "golden_builds": len(golden_builds),
        "history_states": len(history_states),
        "active_connections": 0,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/info")
async def server_info():
    return {
        "version": "3.1_PRO",
        "name": "Aigaane Unified Kernel",
        "golden_build_active": current_golden_build is not None,
        "total_golden_builds": len(golden_builds),
        "total_history_states": len(history_states),
        "current_golden_build": (
            current_golden_build.get("metadata", {}).get("build_name")
            if current_golden_build else None
        ),
    }


# ────────────────────────────────────────────────────────────────
# Atma friction
# ────────────────────────────────────────────────────────────────
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


# ════════════════════════════════════════════════════════════════
# CLASSICAL PROSODY SCANSION ENDPOINTS
# ════════════════════════════════════════════════════════════════
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
            governance=report["governance"],
        )

    elif chandas_clean in ["upajati", "indravajra", "upendravajra"]:
        report = scan_upajati(req.text, padanta_guru=req.padanta_guru)
        trace_steps = [
            ProsodyTraceStep(
                rule="upajati-line-match",
                pada=p["pada_number"],
                syllable=p["total_syllables"],
                found=p["weights"][-1] if p["weights"] else "L",
                ok=p["valid"],
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
            governance=report["governance"],
        )

    elif chandas_clean in METER_SCHEMAS:
        # Split on newlines and danda (।) / double-danda (॥)
        split_pat = chr(13) + chr(10) + "/|।॥"
        lines = [
            ln.strip() for ln in re.split(f"[{split_pat}]+", req.text) if ln.strip()
        ]
        padas = []
        all_diags = []
        all_valid = True

        for idx, line in enumerate(lines[:4], 1):
            pada_res, pada_diags = scan_varnavrtta_pada(
                line, idx, chandas_clean, req.padanta_guru
            )
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
                ok=p["valid"],
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
                "authority": "Piṅgala Chhandaḥśāstra",
            },
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported meter '{req.chandas}'. "
                "Supported: anustubh, upajati, indravajra, upendravajra, "
                "shardulavikridita"
            ),
        )


# ────────────────────────────────────────────────────────────────
# Vercel / Lambda handler
# ────────────────────────────────────────────────────────────────
if Mangum is not None:
    handler = Mangum(app)
else:
    handler = None