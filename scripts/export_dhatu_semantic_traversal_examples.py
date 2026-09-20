#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_traversal_response


EXAMPLES_DIR = ROOT / "data" / "sanskrit" / "dhatus" / "semantic" / "examples" / "graph"
EXAMPLES = {
    "traversal_motion_depth2.response.v1.json": {"nodeId": "motion", "maxDepth": 2},
    "traversal_01_0005_depth2.response.v1.json": {"nodeId": "01.0005", "maxDepth": 2},
    "traversal_guidance_guides.response.v1.json": {
        "nodeId": "guidance",
        "maxDepth": 2,
        "relationType": "guides",
    },
    "traversal_empty_query.response.v1.json": {},
    "traversal_unknown_node.response.v1.json": {"nodeId": "unknown-semantic-node", "maxDepth": 2},
}


def build_examples() -> Dict[str, Dict[str, Any]]:
    return {
        filename: build_dhatu_semantic_traversal_response(**query)
        for filename, query in EXAMPLES.items()
    }


def write_examples(output_dir: Path = EXAMPLES_DIR) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, str] = {}
    for filename, payload in build_examples().items():
        serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        json.loads(serialized)
        path = output_dir / filename
        path.write_text(serialized, encoding="utf-8")
        written[filename] = serialized
    return written


def main() -> int:
    written = write_examples()
    print(json.dumps({
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/export_dhatu_semantic_traversal_examples.py",
        "exampleCount": len(written),
        "examples": sorted(written),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
