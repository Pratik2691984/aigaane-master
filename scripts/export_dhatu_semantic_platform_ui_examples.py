#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import build_dhatu_semantic_platform_index_response


EXAMPLES_DIR = ROOT / "data" / "sanskrit" / "dhatus" / "semantic" / "examples" / "ui"
EXAMPLE_FILE = EXAMPLES_DIR / "ui_semantic_platform_status_panel.v1.json"
GENERATED_BY = "scripts/export_dhatu_semantic_platform_ui_examples.py"
SAFETY_NOTE = "Semantic graph links are foundation-placeholder UI context only; no exact Pāṇinian derivation claim is made. Placeholder-safe: no exact sutra guarantees, no authoritative grammatical claims, and no canonical write hooks."


def ensure_v72_milestones(payload: Dict[str, Any]) -> list[Dict[str, str]]:
    milestones = list(payload.get("milestoneTags", []))
    nodes = {entry.get("node") for entry in milestones}
    if "v71" not in nodes:
        milestones.append({
            "node": "v71",
            "tag": "semantic-api-index",
            "summary": "Public read-only semantic API index",
        })
    if "v72" not in nodes:
        milestones.append({
            "node": "v72",
            "tag": "semantic-platform-status-ui",
            "summary": "Read-only Sanskrit tab semantic platform status panel",
        })
    return milestones


def build_platform_status_panel(index_payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = index_payload or build_dhatu_semantic_platform_index_response()
    milestones = ensure_v72_milestones(payload)
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": GENERATED_BY,
        "panelType": "semanticPlatformStatus",
        "title": "Semantic Platform Status",
        "description": "UI-ready read-only status summary for the Sanskrit dhatu semantic platform.",
        "platformStatus": payload["platformStatus"],
        "milestoneSpan": "v53-v72",
        "milestoneTags": milestones,
        "canonicalRegistryRecordCount": payload["canonicalRegistryRecordCount"],
        "semanticRecordCount": payload["semanticRecordCount"],
        "cards": [
            {
                "cardId": "platform.status.01",
                "cardType": "platformStatus",
                "label": "Platform status",
                "value": payload["platformStatus"],
                "metadata": {
                    "section": "Platform Overview",
                    "milestoneSpan": "v53-v72",
                    "uiReadiness": "READY",
                },
            },
            {
                "cardId": "platform.registry.01",
                "cardType": "registryCount",
                "label": "Canonical registry count",
                "value": payload["canonicalRegistryRecordCount"],
                "metadata": {
                    "section": "Platform Overview",
                    "readOnly": True,
                    "canonicalMutation": False,
                },
            },
            {
                "cardId": "platform.endpoints.01",
                "cardType": "endpointSummary",
                "label": "Available APIs",
                "value": len(payload["endpoints"]),
                "metadata": {
                    "section": "Available APIs",
                    "paths": [entry["path"] for entry in payload["endpoints"]],
                },
            },
            {
                "cardId": "platform.validators.01",
                "cardType": "validatorSummary",
                "label": "Validator summary",
                "value": "PASS",
                "metadata": {
                    "section": "Validator Summary",
                    "validators": [entry["name"] for entry in payload["validators"]],
                },
            },
        ],
        "validators": payload["validators"],
        "endpoints": payload["endpoints"],
        "docs": payload["docs"],
        "examples": payload["examples"] + [
            "data/sanskrit/dhatus/semantic/examples/ui/ui_semantic_platform_status_panel.v1.json",
        ],
        "checkpoint": payload["checkpoint"],
        "safetyPolicy": payload["safetyPolicy"],
        "safetyNote": SAFETY_NOTE,
        "uiReadiness": {
            "status": "READY",
            "mode": "client-side-read-only",
            "backendFetchRequired": False,
            "networkFetchRequired": False,
            "mutationHooksPresent": False,
        },
    }


def write_example(output_path: Path = EXAMPLE_FILE) -> Dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_platform_status_panel()
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    json.loads(serialized)
    output_path.write_text(serialized, encoding="utf-8")
    return payload


def main() -> int:
    payload = write_example()
    print(json.dumps({
        "schemaVersion": "1.0.0",
        "generatedBy": GENERATED_BY,
        "example": str(EXAMPLE_FILE.relative_to(ROOT)).replace("\\", "/"),
        "platformStatus": payload["platformStatus"],
        "milestoneSpan": payload["milestoneSpan"],
        "endpointCount": len(payload["endpoints"]),
        "validatorCount": len(payload["validators"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
