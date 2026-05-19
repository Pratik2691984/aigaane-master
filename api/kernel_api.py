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
from engines.ambiguity import AmbiguityPayload
try:
    from api.engines.ambiguity_resolver import ExecutableAmbiguityDAG
except ModuleNotFoundError:
    from engines.ambiguity_resolver import ExecutableAmbiguityDAG
try:
    from api.engines.derivation_session import DerivationSession
except ModuleNotFoundError:
    from engines.derivation_session import DerivationSession
from engines.consonant_sandhi import ConsonantSandhiException, analyze_consonant_sandhi
from engines.lexical_governance import (
    ANALYZE_GOVERNANCE,
    MORPHOLOGY_GOVERNANCE,
    SANDHI_GOVERNANCE,
    LexicalGovernanceException,
    attach_governance,
    sanitize_mixed_chandas_input,
    validate_devanagari_only,
)
from engines.morphology import (
    MorphologyException,
    conjugate_verb,
    inflect_noun,
    morphology_meta,
)
from engines.sandhi import SandhiException, analyze_vowel_sandhi, final_vowel_boundary, initial_vowel_boundary
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
    left_consonant: Optional[str] = None
    right_consonant: Optional[str] = None
    sutra: Optional[str] = None
    merged: Optional[str] = None

class DerivationPathStep(BaseModel):
    sutra: str
    sutra_name: str
    operation: str
    input_state: str
    output_state: str
    engine_node: str

class GovernanceResponse(BaseModel):
    normalization: str
    script_policy: str
    source: str

class SandhiAnalyzeResponse(BaseModel):
    merged: str
    sutra: str
    sutra_name: str
    type: str
    trace: List[SandhiTraceStep]
    derivation_path: Optional[List[DerivationPathStep]] = None
    governance: Optional[GovernanceResponse] = None
    ambiguity: Optional[AmbiguityPayload] = None

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
    governance: Optional[GovernanceResponse] = None
    ambiguity: Optional[AmbiguityPayload] = None

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
        input_text = sanitize_mixed_chandas_input(payload.input_text, "input_text")
        result = analyze_sanskrit(input_text)
        result["governance"] = ANALYZE_GOVERNANCE.to_dict()
        return JSONResponse(
            content=result,
            media_type="application/json; charset=utf-8",
        )
    except LexicalGovernanceException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": exc.message,
                "invalid_characters": exc.invalid_characters,
            },
        ) from exc
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
        governed_word1 = validate_devanagari_only(payload.word1, "word1")
        governed_word2 = validate_devanagari_only(payload.word2, "word2")
        word1 = unicodedata.normalize("NFC", governed_word1.strip()) if isinstance(governed_word1, str) else governed_word1
        if isinstance(word1, str) and word1.endswith("\u0903"):
            return JSONResponse(
                content=attach_governance(analyze_visarga_sandhi(governed_word1, governed_word2), SANDHI_GOVERNANCE),
                media_type="application/json; charset=utf-8",
            )
        if isinstance(word1, str) and word1.endswith("\u094d"):
            return JSONResponse(
                content=attach_governance(analyze_consonant_sandhi(governed_word1, governed_word2), SANDHI_GOVERNANCE),
                media_type="application/json; charset=utf-8",
            )
        return JSONResponse(
            content=attach_governance(analyze_vowel_sandhi(governed_word1, governed_word2), SANDHI_GOVERNANCE),
            media_type="application/json; charset=utf-8",
        )
    except LexicalGovernanceException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": exc.message,
                "invalid_characters": exc.invalid_characters,
            },
        ) from exc
    except ConsonantSandhiException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc
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
        stem = validate_devanagari_only(payload.stem, "stem")
        return JSONResponse(
            content=attach_governance(inflect_noun(stem, payload.case, payload.number), MORPHOLOGY_GOVERNANCE),
            media_type="application/json; charset=utf-8",
        )
    except LexicalGovernanceException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": exc.message,
                "invalid_characters": exc.invalid_characters,
            },
        ) from exc
    except MorphologyException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc

@app.post("/api/v3/morphology/verb/conjugate", response_model=MorphologyResponse)
async def conjugate_verb_v3(payload: MorphologyVerbRequest):
    try:
        dhatu = validate_devanagari_only(payload.dhatu, "dhatu")
        return JSONResponse(
            content=attach_governance(conjugate_verb(dhatu, payload.lakara, payload.person, payload.number), MORPHOLOGY_GOVERNANCE),
            media_type="application/json; charset=utf-8",
        )
    except LexicalGovernanceException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": exc.message,
                "invalid_characters": exc.invalid_characters,
            },
        ) from exc
    except MorphologyException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        ) from exc

@app.get("/api/v3/debug/ambiguity-demo")
async def debug_ambiguity_demo_v3():
    dag = ExecutableAmbiguityDAG()
    return JSONResponse(
        content=dag.execute_fork(
            "Node 6C Debug Ambiguity Demo",
            [
                {
                    "final_output": "तच्च",
                    "reason": "Optional Ścutva assimilation via Sutra 8.4.40",
                    "derivation_path": [
                        {
                            "sutra": "8.4.40",
                            "sutra_name": "स्तोः श्चुना श्चुः",
                            "operation": "dental_to_palatal_assimilation",
                            "input_state": "तत् + च",
                            "output_state": "तच्च",
                        }
                    ],
                },
                {
                    "final_output": "तद् च",
                    "reason": "Padānta preservation fallback candidate",
                    "derivation_path": [
                        {
                            "sutra": "debug.default",
                            "sutra_name": "Debug fallback candidate",
                            "operation": "padanta_preservation_fallback",
                            "input_state": "तत् + च",
                            "output_state": "तद् च",
                        }
                    ],
                },
            ],
        ),
        media_type="application/json; charset=utf-8",
    )

def session_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "code": "session_error",
            "message": message,
        },
    )

def session_orchestration_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "code": "session_orchestration_error",
            "message": message,
        },
    )

def session_pipeline_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "code": "session_pipeline_error",
            "message": message,
        },
    )

@app.post("/api/v3/debug/session/create")
async def debug_session_create_v3(payload: Dict[str, Any]):
    input_text = payload.get("input_text")
    if input_text is None:
        raise session_error("input_text is required.")
    if not isinstance(input_text, str) or not input_text.strip():
        raise session_error("input_text must not be blank.")

    metadata = payload.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise session_error("metadata must be a dict.")

    session = DerivationSession.create(input_text=input_text, metadata=metadata)
    return JSONResponse(
        content=session.to_dict(),
        media_type="application/json; charset=utf-8",
    )

@app.post("/api/v3/debug/session/append")
async def debug_session_append_v3(payload: Dict[str, Any]):
    if "session" not in payload:
        raise session_error("session is required.")
    if "step" not in payload:
        raise session_error("step is required.")

    step_payload = payload["step"]
    if not isinstance(step_payload, dict):
        raise session_error("step must be a dict.")

    try:
        session = DerivationSession.from_dict(payload["session"])
        session.add_step(
            engine=step_payload["engine"],
            operation=step_payload["operation"],
            input_state=step_payload["input_state"],
            output_state=step_payload["output_state"],
            parent_step_id=step_payload.get("parent_step_id"),
            derivation_path=step_payload.get("derivation_path"),
            metadata=step_payload.get("metadata"),
        )
    except KeyError as exc:
        raise session_error(f"step is missing required field: {exc.args[0]}.") from exc
    except (TypeError, ValueError) as exc:
        raise session_error(str(exc)) from exc

    return JSONResponse(
        content=session.to_dict(),
        media_type="application/json; charset=utf-8",
    )

@app.post("/api/v3/debug/session/run-morphology")
async def debug_session_run_morphology_v3(payload: Dict[str, Any]):
    if "session" not in payload:
        raise session_orchestration_error("session is required.")
    if "request" not in payload:
        raise session_orchestration_error("request is required.")

    request_payload = payload["request"]
    if not isinstance(request_payload, dict):
        raise session_orchestration_error("request must be a dict.")

    try:
        session = DerivationSession.from_dict(payload["session"])
    except (KeyError, TypeError, ValueError) as exc:
        raise session_orchestration_error(str(exc)) from exc

    mode = request_payload.get("mode")
    if mode != "noun":
        raise session_orchestration_error("Unsupported morphology mode.")

    try:
        stem = validate_devanagari_only(request_payload.get("stem"), "stem")
        morphology_result = attach_governance(
            inflect_noun(stem, request_payload.get("case"), request_payload.get("number")),
            MORPHOLOGY_GOVERNANCE,
        )
    except LexicalGovernanceException as exc:
        raise session_orchestration_error(exc.message) from exc
    except MorphologyException as exc:
        raise session_orchestration_error(exc.message) from exc
    except (TypeError, ValueError) as exc:
        raise session_orchestration_error(str(exc)) from exc

    parent_step_id = session.steps[-1].step_id if session.steps else None
    metadata = {"source": "debug_session_run_morphology"}
    if morphology_result.get("governance") is not None:
        metadata["governance"] = morphology_result["governance"]
    if morphology_result.get("rule") is not None:
        metadata["rule"] = morphology_result["rule"]

    try:
        session.add_step(
            engine="Node 3 Morphology",
            operation="noun_inflection",
            input_state={"request": request_payload},
            output_state={
                "form": morphology_result["form"],
                "type": morphology_result["type"],
            },
            parent_step_id=parent_step_id,
            derivation_path=morphology_result.get("derivation_path") or [],
            metadata=metadata,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise session_orchestration_error(str(exc)) from exc

    return JSONResponse(
        content=session.to_dict(),
        media_type="application/json; charset=utf-8",
    )

@app.post("/api/v3/debug/session/run-sandhi")
async def debug_session_run_sandhi_v3(payload: Dict[str, Any]):
    if "session" not in payload:
        raise session_orchestration_error("session is required.")
    if "request" not in payload:
        raise session_orchestration_error("request is required.")

    request_payload = payload["request"]
    if not isinstance(request_payload, dict):
        raise session_orchestration_error("request must be a dict.")
    if request_payload.get("word1") is None:
        raise session_orchestration_error("word1 is required.")
    if request_payload.get("word2") is None:
        raise session_orchestration_error("word2 is required.")

    try:
        session = DerivationSession.from_dict(payload["session"])
    except (KeyError, TypeError, ValueError) as exc:
        raise session_orchestration_error(str(exc)) from exc

    try:
        word1 = validate_devanagari_only(request_payload.get("word1"), "word1")
        word2 = validate_devanagari_only(request_payload.get("word2"), "word2")
        normalized_word1 = unicodedata.normalize("NFC", word1.strip())
        if normalized_word1.endswith("\u0903"):
            sandhi_result = attach_governance(analyze_visarga_sandhi(word1, word2), SANDHI_GOVERNANCE)
        elif final_vowel_boundary(word1) is not None and initial_vowel_boundary(word2) is not None:
            sandhi_result = attach_governance(analyze_vowel_sandhi(word1, word2), SANDHI_GOVERNANCE)
        elif normalized_word1.endswith("\u094d"):
            sandhi_result = attach_governance(analyze_consonant_sandhi(word1, word2), SANDHI_GOVERNANCE)
        else:
            raise session_orchestration_error("Unsupported sandhi boundary.")
    except LexicalGovernanceException as exc:
        raise session_orchestration_error(exc.message) from exc
    except (SandhiException, VisargaSandhiException, ConsonantSandhiException) as exc:
        raise session_orchestration_error(exc.message) from exc
    except (TypeError, ValueError) as exc:
        raise session_orchestration_error(str(exc)) from exc

    parent_step_id = session.steps[-1].step_id if session.steps else None

    try:
        session.add_step(
            engine="Node 2 Sandhi",
            operation="sandhi_execution",
            input_state={
                "word1": word1,
                "word2": word2,
            },
            output_state={
                "merged": sandhi_result["merged"],
                "sutra": sandhi_result.get("sutra"),
                "sutra_name": sandhi_result.get("sutra_name"),
                "type": sandhi_result.get("type"),
            },
            parent_step_id=parent_step_id,
            derivation_path=sandhi_result.get("derivation_path") or [],
            metadata={
                "source": "debug_session_run_sandhi",
                "governance": sandhi_result.get("governance"),
                "trace": sandhi_result.get("trace"),
            },
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise session_orchestration_error(str(exc)) from exc

    return JSONResponse(
        content=session.to_dict(),
        media_type="application/json; charset=utf-8",
    )

@app.post("/api/v3/debug/session/run-pipeline")
async def debug_session_run_pipeline_v3(payload: Dict[str, Any]):
    if "session" not in payload:
        raise session_pipeline_error("session is required.")
    if "pipeline" not in payload:
        raise session_pipeline_error("pipeline is required.")

    pipeline = payload["pipeline"]
    if not isinstance(pipeline, list):
        raise session_pipeline_error("pipeline must be a list.")
    if len(pipeline) != 2:
        raise session_pipeline_error("pipeline must contain exactly 2 steps.")
    if not all(isinstance(step, dict) for step in pipeline):
        raise session_pipeline_error("pipeline steps must be dicts.")

    morphology_step = pipeline[0]
    sandhi_step = pipeline[1]
    if morphology_step.get("engine") != "morphology":
        raise session_pipeline_error("first pipeline step must use morphology.")
    if sandhi_step.get("engine") != "sandhi":
        raise session_pipeline_error("second pipeline step must use sandhi.")

    morphology_request = morphology_step.get("request")
    sandhi_request = sandhi_step.get("request")
    if not isinstance(morphology_request, dict):
        raise session_pipeline_error("morphology request must be a dict.")
    if not isinstance(sandhi_request, dict):
        raise session_pipeline_error("sandhi request must be a dict.")
    if morphology_request.get("mode") != "noun":
        raise session_pipeline_error("morphology mode must be noun.")
    if morphology_request.get("stem") is None:
        raise session_pipeline_error("morphology stem is required.")
    if morphology_request.get("case") is None:
        raise session_pipeline_error("morphology case is required.")
    if morphology_request.get("number") is None:
        raise session_pipeline_error("morphology number is required.")
    if sandhi_request.get("word2") is None:
        raise session_pipeline_error("sandhi word2 is required.")

    try:
        session = DerivationSession.from_dict(payload["session"])
    except (KeyError, TypeError, ValueError) as exc:
        raise session_pipeline_error(str(exc)) from exc

    pipeline_steps = []

    try:
        stem = validate_devanagari_only(morphology_request.get("stem"), "stem")
        morphology_result = attach_governance(
            inflect_noun(stem, morphology_request.get("case"), morphology_request.get("number")),
            MORPHOLOGY_GOVERNANCE,
        )
    except LexicalGovernanceException as exc:
        raise session_pipeline_error(exc.message) from exc
    except MorphologyException as exc:
        raise session_pipeline_error(exc.message) from exc
    except (TypeError, ValueError) as exc:
        raise session_pipeline_error(str(exc)) from exc

    try:
        morphology_parent_step_id = session.steps[-1].step_id if session.steps else None
        morphology_session_step = session.add_step(
            engine="Node 3 Morphology",
            operation="noun_inflection",
            input_state={"request": morphology_request},
            output_state={
                "form": morphology_result["form"],
                "type": morphology_result.get("type"),
            },
            parent_step_id=morphology_parent_step_id,
            derivation_path=morphology_result.get("derivation_path") or [],
            metadata={
                "source": "debug_session_pipeline",
                "pipeline_index": 0,
                "rule": morphology_result.get("rule"),
                "governance": morphology_result.get("governance"),
            },
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise session_pipeline_error(str(exc)) from exc

    previous_output = morphology_result["form"]
    pipeline_steps.append(morphology_session_step.to_dict())

    try:
        word1 = validate_devanagari_only(previous_output, "word1")
        word2 = validate_devanagari_only(sandhi_request.get("word2"), "word2")
        normalized_word1 = unicodedata.normalize("NFC", word1.strip())
        if normalized_word1.endswith("\u0903"):
            sandhi_result = attach_governance(analyze_visarga_sandhi(word1, word2), SANDHI_GOVERNANCE)
        elif final_vowel_boundary(word1) is not None and initial_vowel_boundary(word2) is not None:
            sandhi_result = attach_governance(analyze_vowel_sandhi(word1, word2), SANDHI_GOVERNANCE)
        elif normalized_word1.endswith("\u094d"):
            sandhi_result = attach_governance(analyze_consonant_sandhi(word1, word2), SANDHI_GOVERNANCE)
        else:
            raise session_pipeline_error("Unsupported sandhi boundary.")
    except LexicalGovernanceException as exc:
        raise session_pipeline_error(exc.message) from exc
    except (SandhiException, VisargaSandhiException, ConsonantSandhiException) as exc:
        raise session_pipeline_error(exc.message) from exc
    except (TypeError, ValueError) as exc:
        raise session_pipeline_error(str(exc)) from exc

    try:
        sandhi_session_step = session.add_step(
            engine="Node 2 Sandhi",
            operation="sandhi_execution",
            input_state={
                "word1": previous_output,
                "word2": word2,
            },
            output_state={
                "merged": sandhi_result["merged"],
                "sutra": sandhi_result.get("sutra"),
                "sutra_name": sandhi_result.get("sutra_name"),
                "type": sandhi_result.get("type"),
            },
            parent_step_id=morphology_session_step.step_id,
            derivation_path=sandhi_result.get("derivation_path") or [],
            metadata={
                "source": "debug_session_pipeline",
                "pipeline_index": 1,
                "trace": sandhi_result.get("trace"),
                "governance": sandhi_result.get("governance"),
            },
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise session_pipeline_error(str(exc)) from exc

    previous_output = sandhi_result["merged"]
    pipeline_steps.append(sandhi_session_step.to_dict())

    return JSONResponse(
        content={
            "session": session.to_dict(),
            "final_output": previous_output,
            "pipeline_steps": pipeline_steps,
        },
        media_type="application/json; charset=utf-8",
    )

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
