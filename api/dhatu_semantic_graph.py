from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_SEMANTIC_ROOT = ROOT / "data" / "sanskrit" / "dhatus" / "semantic"
DEFAULT_EDGE_PATH = DEFAULT_SEMANTIC_ROOT / "edges" / "semantic_edges.v1.json"
ALLOWED_NODE_TYPES = {"dhatu", "semantic_cluster", "gloss_taxonomy", "action_facet"}
ALLOWED_RELATION_TYPES = {
    "associated_with",
    "expresses",
    "grounds",
    "guides",
    "transitions_to",
    "contrasts_with",
}
NO_DERIVATION_CLAIM_TEXT = "No exact grammatical or Paninian derivation claim is made."


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Semantic graph source must be a JSON object: {path}")
    return payload


def load_graph(
    edge_path: Any = DEFAULT_EDGE_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> Dict[str, Any]:
    root = resolve_path(semantic_root)
    return {
        "edges": load_json(edge_path),
        "canonicalRegistry": load_json(canonical_registry_path),
        "semanticClusters": load_json(root / "semantic_clusters.v1.json"),
        "actionVectors": load_json(root / "action_vectors.v1.json"),
        "glossTaxonomy": load_json(root / "gloss_taxonomy.v1.json"),
    }


def duplicate_values(values: List[str]) -> List[str]:
    seen: Set[str] = set()
    duplicates: Set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def known_ids(graph: Dict[str, Any]) -> Dict[str, Set[str]]:
    action_facets = {
        facet
        for record in graph["actionVectors"].get("records", [])
        for facet in record.get("actionVector", {}).get("facets", [])
    }
    action_facets.update(
        record.get("actionVector", {}).get("primary")
        for record in graph["actionVectors"].get("records", [])
        if record.get("actionVector", {}).get("primary")
    )
    return {
        "dhatu": set(graph["canonicalRegistry"].get("records", {}).keys()),
        "semantic_cluster": {cluster.get("id") for cluster in graph["semanticClusters"].get("clusters", [])},
        "gloss_taxonomy": {entry.get("id") for entry in graph["glossTaxonomy"].get("taxonomy", [])},
        "action_facet": action_facets,
    }


def validate_graph(
    edge_path: Any = DEFAULT_EDGE_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> Dict[str, Any]:
    graph = load_graph(edge_path, canonical_registry_path, semantic_root)
    edges = graph["edges"].get("edges", [])
    ids_by_type = known_ids(graph)
    edge_ids = [edge.get("edgeId", "") for edge in edges]
    duplicate_edge_ids = duplicate_values(edge_ids)
    invalid_node_types = sorted({
        edge.get(field)
        for edge in edges
        for field in ("sourceType", "targetType")
        if edge.get(field) not in ALLOWED_NODE_TYPES
    })
    invalid_relations = sorted({
        edge.get("relationType")
        for edge in edges
        if edge.get("relationType") not in ALLOWED_RELATION_TYPES
    })
    invalid_references = []
    noncanonical_dhatu_refs = []
    for edge in edges:
        for prefix in ("source", "target"):
            node_type = edge.get(f"{prefix}Type")
            node_id = edge.get(f"{prefix}Id")
            if node_type in ids_by_type and node_id not in ids_by_type[node_type]:
                invalid_references.append({"edgeId": edge.get("edgeId"), "nodeType": node_type, "nodeId": node_id})
            if node_type == "dhatu" and node_id not in ids_by_type["dhatu"]:
                noncanonical_dhatu_refs.append(node_id)
    invalid_confidence_edges = [
        edge.get("edgeId")
        for edge in edges
        if edge.get("confidence") != "foundation-placeholder"
    ]
    derivation_claim_edges = [
        edge.get("edgeId")
        for edge in edges
        if NO_DERIVATION_CLAIM_TEXT.casefold() not in str(edge.get("notes", "")).casefold()
    ]
    checks = {
        "edgeIdsUnique": duplicate_edge_ids == [],
        "sourceAndTargetTypesAllowed": invalid_node_types == [],
        "sourceAndTargetReferencesExist": invalid_references == [],
        "dhatuReferencesAreCanonical": noncanonical_dhatu_refs == [],
        "relationTypesAllowed": invalid_relations == [],
        "confidenceValuesAreFoundationPlaceholder": invalid_confidence_edges == [],
        "noExactGrammaticalDerivationClaims": derivation_claim_edges == [],
    }
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "api/dhatu_semantic_graph.py",
        "graphValidationStatus": "PASS" if all(checks.values()) else "FAIL",
        "edgeCount": len(edges),
        "duplicateEdgeIds": duplicate_edge_ids,
        "invalidNodeTypes": invalid_node_types,
        "invalidReferences": invalid_references,
        "noncanonicalDhatuReferences": sorted(set(noncanonical_dhatu_refs)),
        "invalidRelationTypes": invalid_relations,
        "invalidConfidenceEdges": invalid_confidence_edges,
        "derivationClaimEdges": derivation_claim_edges,
        "checks": checks,
    }


def edge_allows_traversal(edge: Dict[str, Any], node_id: str) -> bool:
    if edge.get("sourceId") == node_id:
        return True
    return edge.get("direction") == "bidirectional" and edge.get("targetId") == node_id


def next_node_for_edge(edge: Dict[str, Any], node_id: str) -> Tuple[str, str]:
    if edge.get("sourceId") == node_id:
        return str(edge.get("targetType")), str(edge.get("targetId"))
    return str(edge.get("sourceType")), str(edge.get("sourceId"))


def get_neighbors(
    node_id: str,
    depth: int = 1,
    relation_type: Optional[str] = None,
    edge_path: Any = DEFAULT_EDGE_PATH,
) -> Dict[str, Any]:
    graph = load_graph(edge_path)
    edges = graph["edges"].get("edges", [])
    max_depth = max(0, int(depth))
    visited_nodes: Set[str] = {node_id}
    traversed_edges: Set[str] = set()
    neighbors: Dict[str, Dict[str, Any]] = {}
    queue = deque([(node_id, 0)])
    while queue:
        current_id, current_depth = queue.popleft()
        if current_depth >= max_depth:
            continue
        for edge in edges:
            if relation_type and edge.get("relationType") != relation_type:
                continue
            if not edge_allows_traversal(edge, current_id):
                continue
            neighbor_type, neighbor_id = next_node_for_edge(edge, current_id)
            traversed_edges.add(edge["edgeId"])
            if neighbor_id == node_id:
                continue
            if neighbor_id not in neighbors:
                neighbors[neighbor_id] = {
                    "nodeType": neighbor_type,
                    "nodeId": neighbor_id,
                    "depth": current_depth + 1,
                    "viaEdgeIds": [edge["edgeId"]],
                    "relationTypes": [edge["relationType"]],
                }
            else:
                neighbors[neighbor_id]["viaEdgeIds"].append(edge["edgeId"])
                if edge["relationType"] not in neighbors[neighbor_id]["relationTypes"]:
                    neighbors[neighbor_id]["relationTypes"].append(edge["relationType"])
            if neighbor_id not in visited_nodes:
                visited_nodes.add(neighbor_id)
                queue.append((neighbor_id, current_depth + 1))
    ordered_neighbors = sorted(neighbors.values(), key=lambda item: (item["depth"], item["nodeId"]))
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "api/dhatu_semantic_graph.py",
        "nodeId": node_id,
        "depth": max_depth,
        "relationType": relation_type,
        "neighborCount": len(ordered_neighbors),
        "neighbors": ordered_neighbors,
        "traversedEdgeIds": sorted(traversed_edges),
    }
