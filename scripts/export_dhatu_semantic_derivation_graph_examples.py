#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_derivation_graph_response


EXAMPLES_DIR = ROOT / "data" / "sanskrit" / "dhatus" / "semantic" / "derivations" / "examples" / "graph"
GENERATED_BY = "scripts/export_dhatu_semantic_derivation_graph_examples.py"
EXAMPLES = {
    "derivation_graph_domain_motion.response.v1.json": {"domain": "motion", "maxDepth": 2},
    "derivation_graph_dhatu_01_0005.response.v1.json": {"dhatuId": "01.0005", "maxDepth": 2},
    "derivation_graph_family_guidance.response.v1.json": {"family": "guidance-transfer", "maxDepth": 2},
    "derivation_graph_relation_semantic_family_bridge.response.v1.json": {"relationType": "semantic_family_bridge", "maxDepth": 1},
    "derivation_graph_empty_query.response.v1.json": {},
    "derivation_graph_unknown_node.response.v1.json": {"dhatuId": "99.9999"},
}


def ui_panel(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": GENERATED_BY,
        "panelType": "semanticDerivationGraphPlaceholder",
        "title": "Semantic Derivation Graph Bridge",
        "cards": [
            {
                "cardId": f"semantic.derivation.graph.{index:02d}",
                "cardType": "semanticDerivationGraphPath",
                "label": path.get("terminalNodeId"),
                "value": " -> ".join(node.get("nodeId", "") for node in path.get("nodes", [])),
                "metadata": {
                    "depth": path.get("depth"),
                    "edgeIds": path.get("edges", []),
                    "relationLabels": path.get("relationLabels", []),
                },
            }
            for index, path in enumerate(payload.get("paths", []), start=1)
        ],
        "nodes": payload.get("nodes", []),
        "edges": payload.get("edges", []),
        "safetyNote": payload.get("safety", {}).get("warning", ""),
    }


def build_examples() -> Dict[str, Dict[str, Any]]:
    examples = {
        filename: build_dhatu_semantic_derivation_graph_response(**query)
        for filename, query in EXAMPLES.items()
    }
    examples["ui_semantic_derivation_graph_panel.v1.json"] = ui_panel(
        build_dhatu_semantic_derivation_graph_response(domain="motion", maxDepth=2)
    )
    return examples


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
        "generatedBy": GENERATED_BY,
        "exampleCount": len(written),
        "examples": sorted(written),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
