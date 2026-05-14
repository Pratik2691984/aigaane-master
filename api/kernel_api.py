# C:\aigaane-master\api\kernel_api.py
# FastAPI Endpoint for External Queries + Static Frontend Hosting

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # <-- ADDED for static files
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
import asyncio

app = FastAPI(title="Aigaane 49D Kernel API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Data Models ============

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

# ============ Storage ============

current_state: Optional[KernelState] = None
history_states: List[KernelState] = []
golden_builds: List[Dict[str, Any]] = []
current_golden_build: Optional[Dict[str, Any]] = None

# ============ WebSocket Manager ============

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.channel_subscriptions: Dict[str, List[WebSocket]] = {
            "golden_build": [], "kernel_state": [], "anomaly_alerts": []
        }
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        for channel in self.channel_subscriptions:
            if websocket in self.channel_subscriptions[channel]:
                self.channel_subscriptions[channel].remove(websocket)
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        if channel in self.channel_subscriptions:
            for connection in self.channel_subscriptions[channel]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# ============ Helper Functions ============

def vector_to_list(v: Vector49D) -> List[float]:
    return v.spatial + v.temporal + v.planetary + v.guna + v.energy + v.biological + v.stellar

def list_to_vector(vector: List[float]) -> Vector49D:
    return Vector49D(
        spatial=vector[0:7], temporal=vector[7:14], planetary=vector[14:21],
        guna=vector[21:28], energy=vector[28:35], biological=vector[35:42], stellar=vector[42:49]
    )

# ============ WebSocket Endpoint ============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    await manager.broadcast_to_channel(message.get("channel"), {"type": "subscribed"})
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ============ Core Endpoints ============

@app.get("/kernel/v3/current")
async def get_current_kernel():
    if current_state is None:
        raise HTTPException(status_code=404, detail="No kernel state available")
    return current_state

@app.post("/kernel/v3/update")
async def update_kernel(state: KernelState):
    global current_state
    current_state = state
    history_states.append(state)
    while len(history_states) > 108:
        history_states.pop(0)
    return {"status": "updated", "timestamp": state.timestamp}

@app.get("/kernel/v3/history")
async def get_history(limit: int = 50):
    return history_states[-limit:]

@app.get("/kernel/v3/compare")
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

# ============ Golden Build Endpoints ============

@app.post("/kernel/v3/golden/build")
async def create_golden_build(data: GoldenBuildData):
    global current_golden_build, golden_builds
    build_data = data.dict()
    build_id = f"gb_{len(golden_builds) + 1:04d}"
    build_data["id"] = build_id
    build_data["created_at"] = datetime.now().isoformat()
    golden_builds.append(build_data)
    current_golden_build = build_data
    return {"status": "created", "id": build_id}

@app.get("/kernel/v3/golden/current")
async def get_current_golden_build():
    if current_golden_build is None:
        raise HTTPException(status_code=404, detail="No Golden Build set")
    return current_golden_build

@app.get("/kernel/v3/golden/list")
async def list_golden_builds():
    return golden_builds

@app.delete("/kernel/v3/golden/{build_id}")
async def delete_golden_build(build_id: str):
    global golden_builds, current_golden_build
    for i, build in enumerate(golden_builds):
        if build.get("id") == build_id:
            del golden_builds[i]
            if current_golden_build and current_golden_build.get("id") == build_id:
                current_golden_build = None
            return {"status": "deleted", "id": build_id}
    raise HTTPException(status_code=404, detail="Golden Build not found")

# ============ Health Endpoints ============

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.0_PRO",
        "golden_builds": len(golden_builds),
        "history_states": len(history_states),
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/info")
async def server_info():
    return {
        "version": "3.0_PRO",
        "name": "Aigaane V3 PRO",
        "golden_build_active": current_golden_build is not None,
        "total_golden_builds": len(golden_builds),
        "total_history_states": len(history_states),
        "current_golden_build": current_golden_build.get("metadata", {}).get("build_name") if current_golden_build else None
    }

# ============ Serve Static Frontend (HTML, JS, CSS) ============
# Mount the repository root (one level above /api) so that index.html, app.js, etc. are accessible.
frontend_root = os.path.join(os.path.dirname(__file__), "..")
if os.path.exists(frontend_root):
    app.mount("/", StaticFiles(directory=frontend_root, html=True), name="frontend")
else:
    print(f"[Startup] Warning: Frontend directory not found at {frontend_root}")

# ============ Startup ============

@app.on_event("startup")
async def startup_event():
    golden_build_path = "golden_build_chitra_53.json"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)