"""
routers/changelog.py
Release history endpoint.

GET /api/v3/changelog       — all releases
GET /api/v3/changelog/latest — latest release
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, status


router = APIRouter(prefix="/api/v3/changelog", tags=["Changelog"])


_CHANGELOG_PATH = Path(__file__).parent.parent / "data" / "changelog.json"


def _load_changelog() -> dict:
    if not _CHANGELOG_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Changelog data not found",
        )
    with open(_CHANGELOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("", status_code=status.HTTP_200_OK, summary="All releases")
def get_changelog() -> dict:
    """Return the full release history."""
    return _load_changelog()


@router.get("/latest", status_code=status.HTTP_200_OK, summary="Latest release")
def get_latest_release() -> dict:
    """Return only the most recent release."""
    data = _load_changelog()
    releases = data.get("releases", [])
    if not releases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No releases found",
        )
    return releases[0]