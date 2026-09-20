#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_traversal_response


def main() -> int:
    queries = {
        "motion_depth2": build_dhatu_semantic_traversal_response(nodeId="motion", maxDepth=2),
        "gam_depth2": build_dhatu_semantic_traversal_response(nodeId="01.0005", maxDepth=2),
        "guidance_guides": build_dhatu_semantic_traversal_response(
            nodeId="guidance",
            maxDepth=2,
            relationType="guides",
        ),
        "empty_query": build_dhatu_semantic_traversal_response(),
        "unknown_node": build_dhatu_semantic_traversal_response(nodeId="unknown-semantic-node", maxDepth=2),
    }
    summary = {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/smoke_dhatu_semantic_traversal_api.py",
        "queries": {
            name: {
                "traversalStatus": payload["traversalStatus"],
                "pathCount": payload["pathCount"],
                "errorCode": payload["errorCode"],
            }
            for name, payload in queries.items()
        },
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
