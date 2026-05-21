#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_graph_neighbors_response


def main() -> int:
    queries = {
        "neighbor_01_0005": build_dhatu_semantic_graph_neighbors_response(nodeId="01.0005"),
        "neighbor_motion_depth2": build_dhatu_semantic_graph_neighbors_response(nodeId="motion", depth=2),
        "neighbor_guidance_guides": build_dhatu_semantic_graph_neighbors_response(
            nodeId="guidance",
            relationType="guides",
        ),
        "neighbor_empty_query": build_dhatu_semantic_graph_neighbors_response(),
    }
    summary = {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/smoke_dhatu_semantic_graph_api.py",
        "queries": {
            name: {
                "neighborCount": payload["neighborCount"],
                "errorCode": payload.get("error", {}).get("code"),
            }
            for name, payload in queries.items()
        },
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
