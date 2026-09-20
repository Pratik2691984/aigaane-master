#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_derivations_response


EXAMPLES_DIR = ROOT / "data" / "sanskrit" / "dhatus" / "semantic" / "derivations" / "examples"
GENERATED_BY = "scripts/export_dhatu_semantic_derivation_examples.py"
EXAMPLES = {
    "derivation_01_0005.response.v1.json": {"dhatuId": "01.0005"},
    "derivation_family_motion_transition.response.v1.json": {"family": "motion-transition"},
    "derivation_domain_motion.response.v1.json": {"domain": "motion"},
    "derivation_relation_motion_guidance.response.v1.json": {"relation": "motion-guidance-adjacent"},
}


def ui_panel(payload: Dict[str, Any], title: str) -> Dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": GENERATED_BY,
        "panelType": "semanticDerivationPlaceholder",
        "title": title,
        "cards": [
            {
                "cardId": f"semantic.derivation.{index:02d}",
                "cardType": "semanticDerivationPlaceholder",
                "label": result.get("derivationFamilyId"),
                "value": result.get("dhatuId"),
                "metadata": {
                    "derivationId": result.get("derivationId"),
                    "usageDomains": result.get("usageDomains", []),
                    "reviewStatus": result.get("reviewStatus"),
                    "relationTypes": [
                        relation.get("relationType")
                        for relation in result.get("protoDerivationRelations", [])
                    ],
                },
            }
            for index, result in enumerate(payload.get("results", []), start=1)
        ],
        "links": [
            {
                "label": "Semantic derivations API",
                "href": "/api/dhatu/semantic/derivations",
                "linkType": "api",
            }
        ],
        "safetyNote": "Derivation metadata is placeholder-only and requires local review before any grammatical use.",
    }


def build_examples() -> Dict[str, Dict[str, Any]]:
    examples = {
        filename: build_dhatu_semantic_derivations_response(**query)
        for filename, query in EXAMPLES.items()
    }
    examples["ui_semantic_derivation_panel.v1.json"] = ui_panel(
        build_dhatu_semantic_derivations_response(domain="motion"),
        "Semantic Derivation Placeholder Panel",
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
