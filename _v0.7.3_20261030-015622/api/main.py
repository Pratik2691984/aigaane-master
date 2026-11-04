"""
Aigaane Core API Gateway
Provides HTTP endpoints for Paninian morphological analysis and multi-studio routing.
"""

from fastapi import FastAPI
from api.routes import health, parse, route

app = FastAPI(
    title="Aigaane Sanskrit Engine API",
    description="Deterministic Pāṇinian morphological parsing and multi-studio routing gateway.",
    version="0.4.0",
)

app.include_router(health.router)
app.include_router(parse.router)
app.include_router(route.router)
