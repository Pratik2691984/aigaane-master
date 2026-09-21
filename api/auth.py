"""
api/auth.py
API key authentication for internal endpoints.

- Public endpoints (chandas/*, sandhi) accept anonymous requests.
- Internal endpoints (agent/*, notebook/*) require X-API-Key.

Uses constant-time comparison to prevent timing attacks.
"""

from __future__ import annotations

import hmac
import os
from typing import Annotated

from fastapi import Header, HTTPException, status


_EXPECTED_KEY = os.environ.get("AIGAANE_API_KEY", "").strip()


def require_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    """
    FastAPI dependency: require a valid API key.

    Raises:
        500 if the server is not configured with an API key.
        401 if the header is missing or invalid.
    """
    if not _EXPECTED_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server auth not configured",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not hmac.compare_digest(x_api_key.strip(), _EXPECTED_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )