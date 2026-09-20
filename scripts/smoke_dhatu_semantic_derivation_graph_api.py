#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_derivation_graph_response


def main() -> int:
    motion = build_dhatu_semantic_derivation_graph_response(domain="motion", maxDepth=2)
    empty = build_dhatu_semantic_derivation_graph_response()
    ok = (
        motion["traversalStatus"] == "OK"
        and empty["traversalStatus"] == "EMPTY_QUERY"
        and motion["safety"]["requiredConfidence"] == "unreviewed"
    )
    print(json.dumps({
        "smokeStatus": "PASS" if ok else "FAIL",
        "motionPathCount": motion["pathCount"],
        "emptyStatus": empty["traversalStatus"],
        "endpoint": "/api/dhatu/semantic/derivation-graph",
    }, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
