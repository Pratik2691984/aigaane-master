from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import quanta_routes, aigaane_routes

app = FastAPI(
    title="Quanta-Aigaane Neuro-Symbolic API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://aigaane.in",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount both prefixes for backward compat (v1) and canonical (v3)
app.include_router(quanta_routes.router, prefix="/api/v1/quanta", tags=["quanta"])
app.include_router(quanta_routes.router, prefix="/api/v3/quanta", tags=["quanta"])
app.include_router(aigaane_routes.router, prefix="/api/v1/aigaane", tags=["aigaane"])
app.include_router(aigaane_routes.router, prefix="/api/v3/aigaane", tags=["aigaane"])


@app.get("/health")
def health():
    return {"status": "ok", "architecture": "Neuro-Symbolic"}