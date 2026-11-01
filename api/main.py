"""
Aigaane Core API Gateway
Provides HTTP endpoints for Paninian morphological analysis and multi-studio routing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import health, parse, route

app = FastAPI(
    title="Aigaane Sanskrit Engine API",
    description="Deterministic Pāṇinian morphological parsing and multi-studio routing gateway.",
    version="0.8.2",
)

# Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(parse.router)
app.include_router(route.router)
