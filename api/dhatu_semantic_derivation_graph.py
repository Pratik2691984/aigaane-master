from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_SEMANTIC_ROOT = ROOT / "data" / "sanskrit" / "dhatus" / "semantic"
DEFAULT_DERIVATION_ROOT = DEFAULT_SEMANTIC_ROOT / "derivations"
DEFAULT_DERIVATION_PATH = DEFAULT_DERIVATION_ROOT / "semantic_derivations.v1.json"
DEFAULT_EDGE_PATH = DEFAULT_DERIVATION_ROOT / "semantic_derivation_edges.v1.json"
PLACEHOLDER_REVIEW_STATUS = "placeholder-local-review-required"
UNREVIEWED_CONFIDENCE = "unreviewed"
PLACEHOLDER_WARNING = "Placeholder-only derivation graph bridge; no exact Paninian derivation claim is made."
ALLOWED_NODE_TYPES = {"semantic_cluster", "derivation_family", "derivation_record"}
ALLOWED_RELATION_TYPES = {
    "semantic_family_bridge",
    "family_record_placeholder",
    "motion_guidance_placeholder",
    "motion_stability_placeholder",
}
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
EXACT_SUTRA_PATTERN = re.compile(r"\b\d+\.\d+\.\d+(?:\.\d+)?\b")


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Semantic derivation graph source must be a JSON object: {path}")
    return payload


def file_sha256(path: Any) -> str:
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    return "".join(char for char in text if not unicodedata.combining(char))


def duplicate_values(values: List[str]) -> List[str]:
    seen: Set[str] = set()
    duplicates: Set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def load_context(
    edge_path: Any = DEFAULT_EDGE_PATH,
    derivation_path: Any = DEFAULT_DERIVATION_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> Dict[str, Any]:
    root = resolve_path(semantic_root)
    return {
        "edges": load_json(edge_path),
        "derivations": load_json(derivation_path),
        "canonicalRegistry": load_json(canonical_registry_path),
        "semanticClusters": load_json(root / "semantic_clusters.v1.json"),
    }


def derivation_records(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [record for record in context["derivations"].get("records", []) if isinstance(record, dict)]


def family_nodes(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [node for node in context["edges"].get("familyNodes", []) if isinstance(node, dict)]


def edge_records(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [edge for edge in context["edges"].get("edges", []) if isinstance(edge, dict)]


def derivation_by_id(context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {record["derivationId"]: record for record in derivation_records(context) if record.get("derivationId")}


def derivation_by_dhatu_id(context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {record["dhatuId"]: record for record in derivation_records(context) if record.get("dhatuId")}


def family_by_node_id(context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {node["graphNodeId"]: node for node in family_nodes(context) if node.get("graphNodeId")}


def family_node_for_family(context: Dict[str, Any], family: str) -> Optional[Dict[str, Any]]:
    needle = normalize_text(family)
    for node in family_nodes(context):
        if needle in normalize_text(node.get("derivationFamilyId")) or needle in normalize_text(node.get("graphNodeId")):
            return node
    return None


def known_ids(context: Dict[str, Any]) -> Dict[str, Set[str]]:
    return {
        "semantic_cluster": {cluster.get("id") for cluster in context["semanticClusters"].get("clusters", [])},
        "derivation_family": {node.get("graphNodeId") for node in family_nodes(context)},
        "derivation_record": {record.get("derivationId") for record in derivation_records(context)},
    }


def node_metadata(context: Dict[str, Any], node_type: str, node_id: str) -> Dict[str, Any]:
    if node_type == "semantic_cluster":
        return {
            "graphNodeId": node_id,
            "nodeType": node_type,
            "label": node_id,
            "reviewStatus": PLACEHOLDER_REVIEW_STATUS,
        }
    if node_type == "derivation_family":
        family = family_by_node_id(context).get(node_id, {})
        return {
            "graphNodeId": node_id,
            "nodeType": node_type,
            "label": family.get("label", node_id),
            "derivationFamilyId": family.get("derivationFamilyId"),
            "semanticLineage": family.get("semanticLineage", []),
            "transformationHints": family.get("transformationHints", []),
            "reviewStatus": family.get("reviewStatus", PLACEHOLDER_REVIEW_STATUS),
        }
    record = derivation_by_id(context).get(node_id, {})
    return {
        "graphNodeId": node_id,
        "nodeType": node_type,
        "label": record.get("rootIast", node_id),
        "dhatuId": record.get("dhatuId"),
        "derivationFamilyId": record.get("derivationFamilyId"),
        "semanticLineage": record.get("semanticLineage", []),
        "transformationHints": record.get("semanticTransformationNotes", []),
        "reviewStatus": record.get("reviewStatus", PLACEHOLDER_REVIEW_STATUS),
    }


def edge_allows_traversal(edge: Dict[str, Any], node_id: str) -> bool:
    if edge.get("sourceId") == node_id:
        return True
    return edge.get("direction") == "bidirectional" and edge.get("targetId") == node_id


def next_node_for_edge(edge: Dict[str, Any], node_id: str) -> Tuple[str, str]:
    if edge.get("sourceId") == node_id:
        return str(edge.get("targetType")), str(edge.get("targetId"))
    return str(edge.get("sourceType")), str(edge.get("sourceId"))


def edge_matches(edge: Dict[str, Any], relation_type: Optional[str]) -> bool:
    return not relation_type or edge.get("relationType") == relation_type


def traversable_edges(edges: List[Dict[str, Any]], node_id: str, relation_type: Optional[str]) -> List[Dict[str, Any]]:
    return sorted(
        [edge for edge in edges if edge_matches(edge, relation_type) and edge_allows_traversal(edge, node_id)],
        key=lambda edge: str(edge.get("edgeId", "")),
    )


def start_nodes_for_query(
    context: Dict[str, Any],
    dhatu_id: Optional[str],
    family: Optional[str],
    domain: Optional[str],
) -> List[Dict[str, str]]:
    starts: List[Dict[str, str]] = []
    if dhatu_id:
        record = derivation_by_dhatu_id(context).get(dhatu_id)
        if record:
            starts.append({"nodeType": "derivation_record", "nodeId": record["derivationId"]})
        return starts
    if family:
        node = family_node_for_family(context, family)
        if node:
            starts.append({"nodeType": "derivation_family", "nodeId": node["graphNodeId"]})
        return starts
    if domain:
        ids = known_ids(context)
        if domain in ids["semantic_cluster"]:
            starts.append({"nodeType": "semantic_cluster", "nodeId": domain})
        for record in derivation_records(context):
            if domain in record.get("usageDomains", []):
                node = family_node_for_family(context, record.get("derivationFamilyId", ""))
                if node:
                    starts.append({"nodeType": "derivation_family", "nodeId": node["graphNodeId"]})
        deduped = {(item["nodeType"], item["nodeId"]): item for item in starts}
        return sorted(deduped.values(), key=lambda item: (item["nodeType"], item["nodeId"]))
    return starts


def traverse_derivation_graph(
    dhatu_id: Optional[str] = None,
    family: Optional[str] = None,
    domain: Optional[str] = None,
    relation: Optional[str] = None,
    max_depth: int = 2,
    relation_type: Optional[str] = None,
    edge_path: Any = DEFAULT_EDGE_PATH,
    derivation_path: Any = DEFAULT_DERIVATION_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> Dict[str, Any]:
    normalized_depth = max(0, int(max_depth))
    query = {
        "dhatuId": dhatu_id,
        "family": family,
        "domain": domain,
        "relation": relation,
        "maxDepth": normalized_depth,
        "relationType": relation_type,
    }
    effective_relation_type = relation_type or relation
    if not any([dhatu_id, family, domain, relation, relation_type]):
        return {
            "schemaVersion": "1.0.0",
            "generatedBy": "api/dhatu_semantic_derivation_graph.py",
            "query": query,
            "traversalStatus": "EMPTY_QUERY",
            "nodeCount": 0,
            "edgeCount": 0,
            "pathCount": 0,
            "nodes": [],
            "edges": [],
            "paths": [],
            "traversedEdgeIds": [],
            "safety": safety_metadata(),
            "errorCode": "empty_semantic_derivation_graph_query",
        }

    context = load_context(edge_path, derivation_path, canonical_registry_path, semantic_root)
    starts = start_nodes_for_query(context, dhatu_id, family, domain)
    if not starts and (relation or relation_type):
        starts = [
            {"nodeType": str(edge["sourceType"]), "nodeId": str(edge["sourceId"])}
            for edge in edge_records(context)
            if edge.get("relationType") == effective_relation_type
        ]
    if not starts:
        return {
            "schemaVersion": "1.0.0",
            "generatedBy": "api/dhatu_semantic_derivation_graph.py",
            "query": query,
            "traversalStatus": "NODE_NOT_FOUND",
            "nodeCount": 0,
            "edgeCount": 0,
            "pathCount": 0,
            "nodes": [],
            "edges": [],
            "paths": [],
            "traversedEdgeIds": [],
            "safety": safety_metadata(),
            "errorCode": "semantic_derivation_graph_node_not_found",
        }

    all_edges = edge_records(context)
    visited_nodes: Set[Tuple[str, str]] = {(start["nodeType"], start["nodeId"]) for start in starts}
    traversed_edge_ids: Set[str] = set()
    raw_paths: List[Dict[str, Any]] = []
    queue = deque([
        {
            "currentNodeType": start["nodeType"],
            "currentNodeId": start["nodeId"],
            "depth": 0,
            "nodes": [start],
            "edges": [],
            "relationLabels": [],
            "nodeIdsInPath": {start["nodeId"]},
        }
        for start in sorted(starts, key=lambda item: (item["nodeType"], item["nodeId"]))
    ])

    while queue:
        state = queue.popleft()
        if state["depth"] >= normalized_depth:
            continue
        for edge in traversable_edges(all_edges, state["currentNodeId"], effective_relation_type):
            neighbor_type, neighbor_id = next_node_for_edge(edge, state["currentNodeId"])
            traversed_edge_ids.add(str(edge["edgeId"]))
            if neighbor_id in state["nodeIdsInPath"]:
                continue
            next_nodes = state["nodes"] + [{"nodeType": neighbor_type, "nodeId": neighbor_id}]
            next_edges = state["edges"] + [edge["edgeId"]]
            next_depth = state["depth"] + 1
            relation_labels = state["relationLabels"] + [edge.get("relationLabel", edge.get("relationType"))]
            raw_paths.append({
                "depth": next_depth,
                "nodes": next_nodes,
                "edges": next_edges,
                "relationLabels": relation_labels,
                "terminalNodeId": neighbor_id,
            })
            visited_nodes.add((neighbor_type, neighbor_id))
            queue.append({
                "currentNodeType": neighbor_type,
                "currentNodeId": neighbor_id,
                "depth": next_depth,
                "nodes": next_nodes,
                "edges": next_edges,
                "relationLabels": relation_labels,
                "nodeIdsInPath": set(state["nodeIdsInPath"]) | {neighbor_id},
            })

    nodes = [
        node_metadata(context, node_type, node_id)
        for node_type, node_id in sorted(visited_nodes, key=lambda item: (item[0], item[1]))
    ]
    edges = [
        enrich_edge(edge)
        for edge in sorted(all_edges, key=lambda item: str(item.get("edgeId", "")))
        if edge.get("edgeId") in traversed_edge_ids
    ]
    paths = [
        {"pathId": f"path.derivation.semantic.{index:04d}", **path}
        for index, path in enumerate(
            sorted(raw_paths, key=lambda item: (item["depth"], item["terminalNodeId"], item["edges"])),
            start=1,
        )
    ]
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "api/dhatu_semantic_derivation_graph.py",
        "query": query,
        "traversalStatus": "OK",
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "pathCount": len(paths),
        "nodes": nodes,
        "edges": edges,
        "paths": paths,
        "traversedEdgeIds": sorted(traversed_edge_ids),
        "safety": safety_metadata(),
        "errorCode": None,
    }


def enrich_edge(edge: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "edgeId": edge.get("edgeId"),
        "sourceType": edge.get("sourceType"),
        "sourceId": edge.get("sourceId"),
        "targetType": edge.get("targetType"),
        "targetId": edge.get("targetId"),
        "relationType": edge.get("relationType"),
        "relationLabel": edge.get("relationLabel"),
        "depthPolicy": "bounded-read-only-traversal",
        "confidence": edge.get("confidence"),
        "reviewStatus": edge.get("reviewStatus"),
        "notes": edge.get("notes"),
    }


def safety_metadata() -> Dict[str, Any]:
    return {
        "warning": PLACEHOLDER_WARNING,
        "authoritativePaninianClaims": False,
        "exactSutraAssertions": False,
        "grammaticalCorrectnessGuarantee": False,
        "canonicalRegistryMutation": False,
        "automatedDerivationGeneration": False,
        "requiredReviewStatus": PLACEHOLDER_REVIEW_STATUS,
        "requiredConfidence": UNREVIEWED_CONFIDENCE,
    }


def _contains_forbidden_sutra_claim(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "schemaVersion":
                continue
            if key in FORBIDDEN_SUTRA_KEYS:
                return True
            if _contains_forbidden_sutra_claim(child):
                return True
        return False
    if isinstance(value, list):
        return any(_contains_forbidden_sutra_claim(child) for child in value)
    if isinstance(value, str):
        return bool(EXACT_SUTRA_PATTERN.search(value))
    return False


def validate_derivation_graph(
    edge_path: Any = DEFAULT_EDGE_PATH,
    derivation_path: Any = DEFAULT_DERIVATION_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> Dict[str, Any]:
    registry_before = file_sha256(canonical_registry_path)
    context = load_context(edge_path, derivation_path, canonical_registry_path, semantic_root)
    registry_after = file_sha256(canonical_registry_path)
    edges_payload = context["edges"]
    edges = edge_records(context)
    families = family_nodes(context)
    ids_by_type = known_ids(context)
    edge_ids = [str(edge.get("edgeId", "")) for edge in edges]
    duplicate_edge_ids = duplicate_values(edge_ids)
    invalid_node_types = sorted({
        edge.get(field)
        for edge in edges
        for field in ("sourceType", "targetType")
        if edge.get(field) not in ALLOWED_NODE_TYPES
    })
    invalid_relation_types = sorted({
        edge.get("relationType")
        for edge in edges
        if edge.get("relationType") not in ALLOWED_RELATION_TYPES
    })
    invalid_references = []
    for edge in edges:
        for side in ("source", "target"):
            node_type = edge.get(f"{side}Type")
            node_id = edge.get(f"{side}Id")
            if node_type in ids_by_type and node_id not in ids_by_type[node_type]:
                invalid_references.append({"edgeId": edge.get("edgeId"), "nodeType": node_type, "nodeId": node_id})
    invalid_confidence_edges = [edge.get("edgeId") for edge in edges if edge.get("confidence") != UNREVIEWED_CONFIDENCE]
    invalid_review_edges = [edge.get("edgeId") for edge in edges if edge.get("reviewStatus") != PLACEHOLDER_REVIEW_STATUS]
    invalid_family_reviews = [
        node.get("graphNodeId")
        for node in families
        if node.get("reviewStatus") != PLACEHOLDER_REVIEW_STATUS
    ]
    canonical_ids = set(context["canonicalRegistry"].get("records", {}).keys())
    noncanonical_dhatu_ids = sorted(
        record.get("dhatuId")
        for record in derivation_records(context)
        if record.get("dhatuId") not in canonical_ids
    )
    exact_sutra_assertions_present = _contains_forbidden_sutra_claim(edges_payload)
    motion = traverse_derivation_graph(domain="motion", max_depth=2, edge_path=edge_path, derivation_path=derivation_path, canonical_registry_path=canonical_registry_path, semantic_root=semantic_root)
    empty = traverse_derivation_graph(edge_path=edge_path, derivation_path=derivation_path, canonical_registry_path=canonical_registry_path, semantic_root=semantic_root)
    unknown = traverse_derivation_graph(dhatu_id="99.9999", edge_path=edge_path, derivation_path=derivation_path, canonical_registry_path=canonical_registry_path, semantic_root=semantic_root)
    checks = {
        "edgeIdsUnique": duplicate_edge_ids == [],
        "nodeTypesAllowed": invalid_node_types == [],
        "relationTypesAllowed": invalid_relation_types == [],
        "referencesResolve": invalid_references == [],
        "confidenceValuesRemainUnreviewed": invalid_confidence_edges == [],
        "reviewStatusPlaceholderOnly": invalid_review_edges == [] and invalid_family_reviews == [],
        "noExactSutraAssertions": not exact_sutra_assertions_present,
        "canonicalDhatuIdsExist": noncanonical_dhatu_ids == [],
        "canonicalRegistryUnchanged": registry_before == registry_after,
        "canonicalRegistryRecordCountIs13": len(canonical_ids) == 13,
        "domainMotionTraversalWorks": motion["traversalStatus"] == "OK" and "edge.derivation.semantic.0001" in motion["traversedEdgeIds"],
        "emptyQuerySafe": empty["traversalStatus"] == "EMPTY_QUERY",
        "unknownNodeSafe": unknown["traversalStatus"] == "NODE_NOT_FOUND",
    }
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "api/dhatu_semantic_derivation_graph.py",
        "derivationGraphValidationStatus": "PASS" if all(checks.values()) else "FAIL",
        "edgeCount": len(edges),
        "familyNodeCount": len(families),
        "canonicalRegistryRecordCount": len(canonical_ids),
        "duplicateEdgeIds": duplicate_edge_ids,
        "invalidNodeTypes": invalid_node_types,
        "invalidRelationTypes": invalid_relation_types,
        "invalidReferences": invalid_references,
        "invalidConfidenceEdges": invalid_confidence_edges,
        "invalidReviewEdges": invalid_review_edges,
        "invalidFamilyReviewNodes": invalid_family_reviews,
        "noncanonicalDhatuIds": noncanonical_dhatu_ids,
        "exactSutraAssertionsPresent": exact_sutra_assertions_present,
        "checks": checks,
    }
