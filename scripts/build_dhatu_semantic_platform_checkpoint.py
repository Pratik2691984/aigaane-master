#!/usr/bin/env python
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.dhatu_semantic_derivation import validate_derivations
from api.dhatu_semantic_derivation_graph import validate_derivation_graph
from api.dhatu_semantic_graph import validate_graph

SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_dhatu_semantic_layer import validate_semantic_layer


RELEASE_TAG = "sanskrit-v70-semantic-derivation-graph-ui-stable"
OUTPUT_DIR = ROOT / "data" / "sanskrit" / "dhatus" / "semantic" / "releases" / "v70"
JSON_OUTPUT = OUTPUT_DIR / "semantic_platform_checkpoint.v70.json"
MARKDOWN_OUTPUT = OUTPUT_DIR / "semantic_platform_checkpoint.v70.md"
CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
SEMANTIC_ROOT = ROOT / "data" / "sanskrit" / "dhatus" / "semantic"
SEMANTIC_MANIFEST_PATH = SEMANTIC_ROOT / "semantic_manifest.v1.json"
SEMANTIC_CLUSTERS_PATH = SEMANTIC_ROOT / "semantic_clusters.v1.json"
ACTION_VECTORS_PATH = SEMANTIC_ROOT / "action_vectors.v1.json"
SEMANTIC_EDGES_PATH = SEMANTIC_ROOT / "edges" / "semantic_edges.v1.json"
DERIVATIONS_PATH = SEMANTIC_ROOT / "derivations" / "semantic_derivations.v1.json"
DERIVATION_EDGES_PATH = SEMANTIC_ROOT / "derivations" / "semantic_derivation_edges.v1.json"
SEMANTIC_UI_EXAMPLES_ROOT = SEMANTIC_ROOT / "examples" / "ui"
DERIVATION_GRAPH_EXAMPLES_ROOT = SEMANTIC_ROOT / "derivations" / "examples" / "graph"
REQUIRED_COVERAGE = ["01.0005", "01.0008", "01.0013"]
PLACEHOLDER_REVIEW_STATUS = "placeholder-local-review-required"
UNREVIEWED_CONFIDENCE = "unreviewed"
EXACT_SUTRA_PATTERN = re.compile(r"\b\d+\.\d+\.\d+(?:\.\d+)?\b")
FORBIDDEN_SUTRA_KEYS = {
    "exactSutraId",
    "exactSutraIds",
    "paniniSutra",
    "paniniSutraId",
    "sutra",
    "sutraId",
    "sutraIds",
    "sutraNumber",
}

MILESTONE_TAGS = [
    {"node": "v53", "tag": "semantic-layer-foundation", "summary": "Semantic sidecar foundation"},
    {"node": "v54", "tag": "semantic-query-engine", "summary": "Semantic query engine"},
    {"node": "v55", "tag": "semantic-search-api", "summary": "Semantic search API"},
    {"node": "v56", "tag": "semantic-api-examples-docs", "summary": "Examples and documentation"},
    {"node": "v57", "tag": "semantic-graph-neighbors", "summary": "Semantic graph neighbors"},
    {"node": "v58", "tag": "semantic-platform-continuity", "summary": "Semantic platform continuity checkpoint"},
    {"node": "v59", "tag": "semantic-platform-continuity", "summary": "Semantic platform continuity checkpoint"},
    {"node": "v60", "tag": "semantic-graph-api-helper", "summary": "Graph API helper"},
    {"node": "v61", "tag": "semantic-traversal-api", "summary": "Traversal API"},
    {"node": "v62", "tag": "ui-ready-semantic-fixtures", "summary": "UI-ready semantic fixtures"},
    {"node": "v63", "tag": "sanskrit-semantic-panels", "summary": "Sanskrit semantic panels"},
    {"node": "v64", "tag": "interactive-semantic-controls", "summary": "Interactive semantic controls"},
    {"node": "v65", "tag": "semantic-graph-visualization", "summary": "Graph visualization"},
    {"node": "v66", "tag": "semantic-graph-a11y", "summary": "Graph accessibility"},
    {"node": "v67", "tag": "semantic-derivation-layer", "summary": "Semantic derivation placeholder layer"},
    {"node": "v68", "tag": "semantic-derivation-ui", "summary": "Derivation Intelligence UI"},
    {"node": "v69", "tag": "semantic-derivation-graph-bridge", "summary": "Derivation graph bridge"},
    {"node": "v70", "tag": "semantic-derivation-graph-ui", "summary": "Derivation Graph Intelligence UI"},
]


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def release_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def contains_exact_sutra_claim(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "schemaVersion":
                continue
            if key in FORBIDDEN_SUTRA_KEYS:
                return True
            if contains_exact_sutra_claim(child):
                return True
        return False
    if isinstance(value, list):
        return any(contains_exact_sutra_claim(child) for child in value)
    if isinstance(value, str):
        return bool(EXACT_SUTRA_PATTERN.search(value))
    return False


def collect_field_values(value: Any, field_name: str) -> List[Any]:
    values: List[Any] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == field_name:
                values.append(child)
            values.extend(collect_field_values(child, field_name))
    elif isinstance(value, list):
        for child in value:
            values.extend(collect_field_values(child, field_name))
    return values


def count_json_files(path: Path) -> int:
    return len(sorted(path.glob("*.json"))) if path.exists() else 0


def generated_artifacts() -> List[str]:
    artifacts = [
        JSON_OUTPUT,
        MARKDOWN_OUTPUT,
        SEMANTIC_MANIFEST_PATH,
        SEMANTIC_CLUSTERS_PATH,
        ACTION_VECTORS_PATH,
        SEMANTIC_EDGES_PATH,
        DERIVATIONS_PATH,
        DERIVATION_EDGES_PATH,
        SEMANTIC_ROOT / "UI_INTEGRATION.md",
        SEMANTIC_ROOT / "DERIVATION_API.md",
    ]
    artifacts.extend(sorted(SEMANTIC_UI_EXAMPLES_ROOT.glob("*.json")))
    artifacts.extend(sorted(DERIVATION_GRAPH_EXAMPLES_ROOT.glob("*.json")))
    return [str(path.relative_to(ROOT)).replace("\\", "/") for path in artifacts]


def build_checkpoint() -> Dict[str, Any]:
    registry = load_json(CANONICAL_REGISTRY_PATH)
    manifest = load_json(SEMANTIC_MANIFEST_PATH)
    clusters = load_json(SEMANTIC_CLUSTERS_PATH)
    action_vectors = load_json(ACTION_VECTORS_PATH)
    semantic_edges = load_json(SEMANTIC_EDGES_PATH)
    derivations = load_json(DERIVATIONS_PATH)
    derivation_edges = load_json(DERIVATION_EDGES_PATH)

    semantic_summary = validate_semantic_layer()
    semantic_graph_summary = validate_graph()
    derivation_summary = validate_derivations()
    derivation_graph_summary = validate_derivation_graph()

    canonical_count = len(registry.get("records", {}))
    semantic_records = action_vectors.get("records", [])
    derivation_records = derivations.get("records", [])
    covered_ids = sorted({record.get("dhatuId") for record in semantic_records if record.get("dhatuId")})
    derivation_payloads = [derivations, derivation_edges]
    confidence_values = collect_field_values(derivation_payloads, "confidence")
    review_status_values = collect_field_values(derivation_payloads, "reviewStatus")
    no_exact_sutra_claims = not any(contains_exact_sutra_claim(payload) for payload in derivation_payloads + [semantic_edges])
    confidence_unreviewed = all(value == UNREVIEWED_CONFIDENCE for value in confidence_values)
    review_status_placeholder = all(value == PLACEHOLDER_REVIEW_STATUS for value in review_status_values)
    required_coverage = all(dhatu_id in covered_ids for dhatu_id in REQUIRED_COVERAGE)

    validation_summary = {
        "semanticLayer": semantic_summary.get("semanticValidationStatus"),
        "semanticGraph": semantic_graph_summary.get("graphValidationStatus"),
        "semanticDerivation": derivation_summary.get("derivationValidationStatus"),
        "semanticDerivationGraph": derivation_graph_summary.get("derivationGraphValidationStatus"),
    }
    safety_policy = {
        "readOnlySemanticArchitecture": True,
        "canonicalRegistryMutation": False,
        "canonicalWriteEnvironmentFlagsRequired": False,
        "exactPaninianDerivationClaimsAllowed": False,
        "exactSutraAssertionsAllowed": False,
        "grammaticalCorrectnessGuarantee": False,
        "derivationConfidenceRequired": UNREVIEWED_CONFIDENCE,
        "derivationReviewStatusRequired": PLACEHOLDER_REVIEW_STATUS,
        "allDerivationConfidenceValuesUnreviewed": confidence_unreviewed,
        "allDerivationReviewStatusesPlaceholder": review_status_placeholder,
        "noExactPaninianDerivationClaimsPresent": no_exact_sutra_claims,
    }
    checks = {
        "canonicalRegistryCountIs13": canonical_count == 13,
        "semanticLayerValidationPasses": validation_summary["semanticLayer"] == "PASS",
        "semanticGraphValidationPasses": validation_summary["semanticGraph"] == "PASS",
        "derivationValidationPasses": validation_summary["semanticDerivation"] == "PASS",
        "derivationGraphValidationPasses": validation_summary["semanticDerivationGraph"] == "PASS",
        "requiredDhatuCoveragePresent": required_coverage,
        "noCanonicalWriteEnvironmentFlagsRequired": not safety_policy["canonicalWriteEnvironmentFlagsRequired"],
        "noExactPaninianDerivationClaimsPresent": no_exact_sutra_claims,
        "allDerivationConfidenceValuesUnreviewed": confidence_unreviewed,
        "allDerivationReviewStatusesPlaceholder": review_status_placeholder,
    }
    blocking_reasons = [name for name, ok in checks.items() if not ok]
    platform_status = "READY" if not blocking_reasons else "BLOCKED"

    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/build_dhatu_semantic_platform_checkpoint.py",
        "releaseTag": RELEASE_TAG,
        "releaseCommit": release_commit(),
        "platformStatus": platform_status,
        "canonicalRegistryRecordCount": canonical_count,
        "semanticRecordCount": len(semantic_records),
        "semanticClusterCount": len(clusters.get("clusters", [])),
        "semanticGraphEdgeCount": len(semantic_edges.get("edges", [])),
        "derivationRecordCount": len(derivation_records),
        "derivationGraphEdgeCount": len(derivation_edges.get("edges", [])),
        "uiPanelCount": count_json_files(SEMANTIC_UI_EXAMPLES_ROOT) + count_json_files(DERIVATION_GRAPH_EXAMPLES_ROOT),
        "coveredDhatuIds": covered_ids,
        "safetyPolicy": safety_policy,
        "validationSummary": validation_summary,
        "validationDetails": {
            "semanticLayer": semantic_summary,
            "semanticGraph": semantic_graph_summary,
            "semanticDerivation": derivation_summary,
            "semanticDerivationGraph": derivation_graph_summary,
        },
        "milestoneTags": MILESTONE_TAGS,
        "generatedArtifacts": generated_artifacts(),
        "blockingReasons": blocking_reasons,
    }


def markdown_table(rows: List[Dict[str, str]]) -> str:
    lines = ["| Node | Tag | Summary |", "| --- | --- | --- |"]
    for row in rows:
        lines.append(f"| {row['node']} | `{row['tag']}` | {row['summary']} |")
    return "\n".join(lines)


def build_markdown(checkpoint: Dict[str, Any]) -> str:
    validation = checkpoint["validationSummary"]
    safety = checkpoint["safetyPolicy"]
    return "\n".join([
        "# Sanskrit Semantic Platform Checkpoint v70",
        "",
        "## Release Summary",
        "",
        f"- Release tag: `{checkpoint['releaseTag']}`",
        f"- Release commit: `{checkpoint['releaseCommit']}`",
        f"- Platform status: **{checkpoint['platformStatus']}**",
        f"- Generated by: `{checkpoint['generatedBy']}`",
        "",
        "## v53-v70 Milestone Table",
        "",
        markdown_table(checkpoint["milestoneTags"]),
        "",
        "## Canonical Registry Status",
        "",
        f"- Canonical registry records: {checkpoint['canonicalRegistryRecordCount']}",
        "- Canonical registry mutation: disabled",
        "",
        "## Semantic Layer Status",
        "",
        f"- Semantic records: {checkpoint['semanticRecordCount']}",
        f"- Semantic clusters: {checkpoint['semanticClusterCount']}",
        f"- Covered dhatu ids: {', '.join(checkpoint['coveredDhatuIds'])}",
        "",
        "## Graph and Traversal Status",
        "",
        f"- Semantic graph edges: {checkpoint['semanticGraphEdgeCount']}",
        f"- Semantic graph validator: {validation['semanticGraph']}",
        "",
        "## Derivation Status",
        "",
        f"- Derivation records: {checkpoint['derivationRecordCount']}",
        f"- Derivation graph edges: {checkpoint['derivationGraphEdgeCount']}",
        f"- Derivation validator: {validation['semanticDerivation']}",
        f"- Derivation graph validator: {validation['semanticDerivationGraph']}",
        "",
        "## UI Status",
        "",
        f"- UI/example panel count: {checkpoint['uiPanelCount']}",
        "- Sanskrit semantic, derivation, and derivation graph panels are read-only fixture-compatible surfaces.",
        "",
        "## Safety Guarantees",
        "",
        f"- Exact Paninian derivation claims allowed: {safety['exactPaninianDerivationClaimsAllowed']}",
        f"- Exact sutra assertions allowed: {safety['exactSutraAssertionsAllowed']}",
        f"- Grammatical correctness guarantee: {safety['grammaticalCorrectnessGuarantee']}",
        f"- Derivation confidence requirement: `{safety['derivationConfidenceRequired']}`",
        f"- Derivation review status requirement: `{safety['derivationReviewStatusRequired']}`",
        "",
        "## Validator Results",
        "",
        f"- Semantic layer validation: {validation['semanticLayer']}",
        f"- Semantic graph validation: {validation['semanticGraph']}",
        f"- Semantic derivation validation: {validation['semanticDerivation']}",
        f"- Semantic derivation graph validation: {validation['semanticDerivationGraph']}",
        f"- Blocking reasons: {', '.join(checkpoint['blockingReasons']) if checkpoint['blockingReasons'] else 'none'}",
        "",
        "## Next Recommended Phase",
        "",
        "Proceed to reviewed, source-backed semantic enrichment only after maintaining the placeholder safety contract. Future Paninian derivational intelligence should remain gated by explicit review, evidence, and no canonical mutation by default.",
        "",
    ])


def write_checkpoint() -> Dict[str, Any]:
    checkpoint = build_checkpoint()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MARKDOWN_OUTPUT.write_text(build_markdown(checkpoint), encoding="utf-8")
    return checkpoint


def main() -> int:
    checkpoint = write_checkpoint()
    print(json.dumps({
        "schemaVersion": checkpoint["schemaVersion"],
        "generatedBy": checkpoint["generatedBy"],
        "releaseTag": checkpoint["releaseTag"],
        "platformStatus": checkpoint["platformStatus"],
        "canonicalRegistryRecordCount": checkpoint["canonicalRegistryRecordCount"],
        "blockingReasons": checkpoint["blockingReasons"],
    }, sort_keys=True))
    return 0 if checkpoint["platformStatus"] == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
