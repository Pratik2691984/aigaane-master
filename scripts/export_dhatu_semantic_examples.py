#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_search_response


EXAMPLES_DIR = ROOT / "data" / "sanskrit" / "dhatus" / "semantic" / "examples"
EXAMPLES = {
    "search_by_cluster_motion.response.v1.json": {"cluster": "motion"},
    "search_by_action_guidance.response.v1.json": {"action": "guidance"},
    "search_by_gloss_stand.response.v1.json": {"gloss": "stand"},
    "search_empty_query.response.v1.json": {},
}


def build_examples() -> Dict[str, Dict[str, Any]]:
    return {
        filename: build_dhatu_semantic_search_response(**query)
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
        "generatedBy": "scripts/export_dhatu_semantic_examples.py",
        "exampleCount": len(written),
        "examples": sorted(written),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
