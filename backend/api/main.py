from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import quanta_routes, aigaane_routes, corpus_routes, samasa_routes, sandhi_routes, morphology_routes, chandas_routes

APP_VERSION = "1.4.2-audit-updated"

app = FastAPI(
    title="Quanta-Aigaane Neuro-Symbolic API",
    version=APP_VERSION,
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

# Dual-mount: /api/v1 (deprecated) and /api/v3 (canonical)
app.include_router(quanta_routes.router, prefix="/api/v1/quanta", tags=["quanta"])
app.include_router(quanta_routes.router, prefix="/api/v3/quanta", tags=["quanta"])

app.include_router(aigaane_routes.router, prefix="/api/v1/aigaane", tags=["aigaane"])
app.include_router(aigaane_routes.router, prefix="/api/v3/aigaane", tags=["aigaane"])

app.include_router(corpus_routes.router, prefix="/api/v1/corpus", tags=["corpus"])
app.include_router(corpus_routes.router, prefix="/api/v3/corpus", tags=["corpus"])
app.include_router(samasa_routes.router, prefix="/api/v1/samasa", tags=["samasa"])
app.include_router(samasa_routes.router, prefix="/api/v3/samasa", tags=["samasa"])
app.include_router(sandhi_routes.router, prefix="/api/v1/sandhi", tags=["sandhi"])
app.include_router(sandhi_routes.router, prefix="/api/v3/sandhi", tags=["sandhi"])
app.include_router(morphology_routes.router, prefix="/api/v1/morphology", tags=["morphology"])
app.include_router(morphology_routes.router, prefix="/api/v3/morphology", tags=["morphology"])
app.include_router(chandas_routes.router, prefix="/api/v1/chandas", tags=["chandas"])
app.include_router(chandas_routes.router, prefix="/api/v3/chandas", tags=["chandas"])


@app.get("/health")
def health():
    return {
        "status": "ok",
        "architecture": "Neuro-Symbolic",
        "version": APP_VERSION,
    }


@app.get("/")
def root():
    return {
        "status": "online",
        "engine": "Aigaane-Quanta Neuro-Symbolic",
        "version": APP_VERSION,
        "docs": "/docs",
    }