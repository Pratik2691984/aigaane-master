#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from validate_large_scale_ingestion import ROOT

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.dhatu_semantic_query import query_semantics


DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_SEMANTIC_ROOT = ROOT / "data" / "sanskrit" / "dhatus" / "semantic"
PROMOTED_DHATU_IDS = ["01.0005", "01.0013", "01.0008"]


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    resolved = resolve_path(path)
    with resolved.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Semantic layer source must be a JSON object: {resolved}")
    return payload


def file_sha256(path: Any) -> str:
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def load_semantic_files(semantic_root: Any = DEFAULT_SEMANTIC_ROOT) -> Dict[str, Dict[str, Any]]:
    root = resolve_path(semantic_root)
    filenames = [
        "semantic_schema.v2.json",
        "semantic_clusters.v1.json",
        "panini_references.v1.json",
        "action_vectors.v1.json",
        "derivation_graph.v1.json",
        "gloss_taxonomy.v1.json",
        "semantic_manifest.v1.json",
    ]
    return {filename: load_json(root / filename) for filename in filenames}


def duplicate_values(values: List[str]) -> List[str]:
    seen: Set[str] = set()
    duplicates: Set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def validate_semantic_layer(
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> Dict[str, Any]:
    registry_before = file_sha256(canonical_registry_path)
    registry = load_json(canonical_registry_path)
    semantic_files = load_semantic_files(semantic_root)
    registry_after = file_sha256(canonical_registry_path)

    canonical_ids = set(registry.get("records", {}).keys())
    action_records = semantic_files["action_vectors.v1.json"].get("records", [])
    semantic_ids = [record.get("dhatuId") for record in action_records]
    cluster_ids = {cluster.get("id") for cluster in semantic_files["semantic_clusters.v1.json"].get("clusters", [])}
    referenced_clusters = sorted({
        cluster_id
        for record in action_records
        for cluster_id in record.get("semanticClusterIds", [])
    })
    invalid_clusters = [cluster_id for cluster_id in referenced_clusters if cluster_id not in cluster_ids]
    manifest = semantic_files["semantic_manifest.v1.json"]
    covered_ids = list(manifest.get("coveredDhatuIds", []))
    semantic_id_set = set(semantic_ids)
    missing_promoted = [dhatu_id for dhatu_id in PROMOTED_DHATU_IDS if dhatu_id not in semantic_id_set]
    noncanonical_semantic_ids = sorted(dhatu_id for dhatu_id in semantic_id_set if dhatu_id not in canonical_ids)
    duplicate_semantic_ids = duplicate_values([str(dhatu_id) for dhatu_id in semantic_ids])
    manifest_count_matches = int(manifest.get("semanticRecordCount", -1)) == len(action_records)
    manifest_coverage_matches = sorted(covered_ids) == sorted(semantic_id_set)
    query_results = {
        "guidanceAction": query_semantics(
            action="guidance",
            canonical_registry_path=canonical_registry_path,
            semantic_root=semantic_root,
        ),
        "motionCluster": query_semantics(
            cluster="motion",
            canonical_registry_path=canonical_registry_path,
            semantic_root=semantic_root,
        ),
        "standGloss": query_semantics(
            gloss="stand",
            canonical_registry_path=canonical_registry_path,
            semantic_root=semantic_root,
        ),
    }
    queryable_ids = sorted({
        result["dhatuId"]
        for results in query_results.values()
        for result in results
    })
    all_query_results_canonical = all(
        result["dhatuId"] in canonical_ids
        for results in query_results.values()
        for result in results
    )
    canonical_registry_unchanged = registry_before == registry_after
    checks = {
        "semanticDirectoryPresent": resolve_path(semantic_root).exists(),
        "semanticIdsExistInCanonicalRegistry": noncanonical_semantic_ids == [],
        "noDuplicateSemanticDhatuIds": duplicate_semantic_ids == [],
        "promotedRootsCovered": missing_promoted == [],
        "actionVectorsReferenceValidClusters": invalid_clusters == [],
        "manifestCountMatchesSemanticEntries": manifest_count_matches,
        "manifestCoverageMatchesSemanticEntries": manifest_coverage_matches,
        "canonicalRegistryUnchanged": canonical_registry_unchanged,
        "canonicalRegistryRecordCountIs13": len(canonical_ids) == 13,
        "queryableSemanticRecordsMatchManifestCoverage": sorted(semantic_id_set) == sorted(covered_ids),
        "semanticQueryResultsPointToCanonicalRegistry": all_query_results_canonical,
        "guidanceActionQueryReturnsNi": any(result["dhatuId"] == "01.0008" for result in query_results["guidanceAction"]),
        "motionClusterQueryReturnsGam": any(result["dhatuId"] == "01.0005" for result in query_results["motionCluster"]),
        "standGlossQueryReturnsStha": any(result["dhatuId"] == "01.0013" for result in query_results["standGloss"]),
    }
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "scripts/validate_dhatu_semantic_layer.py",
        "semanticValidationStatus": "PASS" if all(checks.values()) else "FAIL",
        "canonicalRegistryRecordCount": len(canonical_ids),
        "semanticRecordCount": len(action_records),
        "coveredDhatuIds": sorted(semantic_id_set),
        "missingPromotedDhatuIds": missing_promoted,
        "noncanonicalSemanticDhatuIds": noncanonical_semantic_ids,
        "duplicateSemanticDhatuIds": duplicate_semantic_ids,
        "invalidSemanticClusterIds": invalid_clusters,
        "queryableDhatuIds": queryable_ids,
        "checks": checks,
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate canonical dhatu semantic sidecar layer.")
    parser.add_argument("--canonical-registry", default=str(DEFAULT_CANONICAL_REGISTRY_PATH))
    parser.add_argument("--semantic-root", default=str(DEFAULT_SEMANTIC_ROOT))
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        summary = validate_semantic_layer(args.canonical_registry, args.semantic_root)
        print(json.dumps({
            "semanticValidationStatus": summary["semanticValidationStatus"],
            "canonicalRegistryRecordCount": summary["canonicalRegistryRecordCount"],
            "semanticRecordCount": summary["semanticRecordCount"],
            "coveredDhatuIds": summary["coveredDhatuIds"],
        }, sort_keys=True))
        return 0 if summary["semanticValidationStatus"] == "PASS" else 1
    except Exception as exc:
        print(f"Dhatu semantic layer validation failed: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
