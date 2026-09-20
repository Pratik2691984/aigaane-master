#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_platform_index_response


EXPECTED_ENDPOINTS = {
    "/api/dhatu/semantic/search",
    "/api/dhatu/semantic/neighbors",
    "/api/dhatu/semantic/traverse",
    "/api/dhatu/semantic/derivations",
    "/api/dhatu/semantic/derivation-graph",
}


def main() -> int:
    payload = build_dhatu_semantic_platform_index_response()
    endpoint_paths = {entry["path"] for entry in payload.get("endpoints", [])}
    safety = payload.get("safetyPolicy", {})
    ok = (
        payload.get("platformStatus") == "READY"
        and EXPECTED_ENDPOINTS.issubset(endpoint_paths)
        and safety.get("exactSutraAssertionsAllowed") is False
        and safety.get("exactPaninianDerivationClaimsAllowed") is False
    )
    print(json.dumps({
        "smokeStatus": "PASS" if ok else "FAIL",
        "endpoint": "/api/dhatu/semantic",
        "platformStatus": payload.get("platformStatus"),
        "canonicalRegistryRecordCount": payload.get("canonicalRegistryRecordCount"),
        "endpointCount": len(endpoint_paths),
        "checkpoint": payload.get("checkpoint", {}).get("jsonPath"),
    }, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
