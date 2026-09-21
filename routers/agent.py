"""
routers/agent.py
POST /api/v3/agent/lyric — SSE streaming endpoint.

Requires X-API-Key header (see api/auth.py).
"""

from __future__ import annotations

import json
from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent.orchestrator import Orchestrator
from api.auth import require_api_key


router = APIRouter(prefix="/api/v3/agent", tags=["Agent"])


class LyricRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    meter: str = Field("anuṣṭubh", max_length=64)
    max_attempts: int = Field(3, ge=1, le=5)
    quanta_ceiling: int = Field(300, ge=50, le=1000)


@router.post("/lyric", dependencies=[Depends(require_api_key)])
async def generate_lyric(payload: LyricRequest) -> StreamingResponse:
    """
    Generate a metrically-validated Sanskrit verse.

    Returns Server-Sent Events with progress stages:
      retrieving → drafting → scanning → validating → complete
    """
    orchestrator = Orchestrator()

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for event in orchestrator.generate_verse(
                prompt=payload.prompt,
                meter=payload.meter,
                max_attempts=payload.max_attempts,
                ledger_ceiling=payload.quanta_ceiling,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        finally:
            await orchestrator.close()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )