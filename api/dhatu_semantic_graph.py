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
    traversal_summary = validate_traversal_behaviors(edge_path, canonical_registry_path, semantic_root)
    checks = {
        "edgeIdsUnique": duplicate_edge_ids == [],
        "sourceAndTargetTypesAllowed": invalid_node_types == [],
        "sourceAndTargetReferencesExist": invalid_references == [],
        "dhatuReferencesAreCanonical": noncanonical_dhatu_refs == [],
        "relationTypesAllowed": invalid_relations == [],
        "confidenceValuesAreFoundationPlaceholder": invalid_confidence_edges == [],
        "noExactGrammaticalDerivationClaims": derivation_claim_edges == [],
        "semanticTraversalValidationPasses": traversal_summary["traversalValidationStatus"] == "PASS",
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
        "traversalValidationSummary": traversal_summary,
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


def node_type_for_id(graph: Dict[str, Any], node_id: str) -> Optional[str]:
    ids_by_type = known_ids(graph)
    for node_type in ("dhatu", "semantic_cluster", "gloss_taxonomy", "action_facet"):
        if node_id in ids_by_type[node_type]:
            return node_type
    return None


def traversable_edges_for_node(
    edges: List[Dict[str, Any]],
    node_id: str,
    relation_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    return sorted(
        [
            edge
            for edge in edges
            if (not relation_type or edge.get("relationType") == relation_type)
            and edge_allows_traversal(edge, node_id)
        ],
        key=lambda edge: str(edge.get("edgeId", "")),
    )


def traverse_graph(
    node_id: Optional[str],
    max_depth: int = 2,
    relation_type: Optional[str] = None,
    edge_path: Any = DEFAULT_EDGE_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> Dict[str, Any]:
    normalized_depth = max(0, int(max_depth))
    if not node_id:
        return {
            "schemaVersion": "1.0.0",
            "generatedBy": "api/dhatu_semantic_graph.py",
            "nodeId": node_id,
            "maxDepth": normalized_depth,
            "relationType": relation_type,
            "traversalStatus": "EMPTY_QUERY",
            "visitedNodeCount": 0,
            "pathCount": 0,
            "paths": [],
            "traversedEdgeIds": [],
            "errorCode": "empty_semantic_traversal_query",
        }

    graph = load_graph(edge_path, canonical_registry_path, semantic_root)
    start_type = node_type_for_id(graph, node_id)
    if start_type is None:
        return {
            "schemaVersion": "1.0.0",
            "generatedBy": "api/dhatu_semantic_graph.py",
            "nodeId": node_id,
            "maxDepth": normalized_depth,
            "relationType": relation_type,
            "traversalStatus": "NODE_NOT_FOUND",
            "visitedNodeCount": 0,
            "pathCount": 0,
            "paths": [],
            "traversedEdgeIds": [],
            "errorCode": "semantic_graph_node_not_found",
        }

    edges = graph["edges"].get("edges", [])
    traversed_edges: Set[str] = set()
    visited_nodes: Set[str] = {node_id}
    raw_paths: List[Dict[str, Any]] = []
    queue = deque([
        {
            "currentNodeId": node_id,
            "depth": 0,
            "nodes": [{"nodeType": start_type, "nodeId": node_id}],
            "edges": [],
            "relationTypes": [],
            "nodeIdsInPath": {node_id},
        }
    ])

    while queue:
        state = queue.popleft()
        if state["depth"] >= normalized_depth:
            continue
        for edge in traversable_edges_for_node(edges, state["currentNodeId"], relation_type):
            neighbor_type, neighbor_id = next_node_for_edge(edge, state["currentNodeId"])
            traversed_edges.add(edge["edgeId"])
            if neighbor_id in state["nodeIdsInPath"]:
                continue

            next_nodes = state["nodes"] + [{"nodeType": neighbor_type, "nodeId": neighbor_id}]
            next_edges = state["edges"] + [edge["edgeId"]]
            next_relation_types = state["relationTypes"] + [edge["relationType"]]
            next_depth = state["depth"] + 1
            raw_paths.append({
                "depth": next_depth,
                "nodes": next_nodes,
                "edges": next_edges,
                "terminalNodeId": neighbor_id,
                "relationTypes": next_relation_types,
            })
            visited_nodes.add(neighbor_id)
            queue.append({
                "currentNodeId": neighbor_id,
                "depth": next_depth,
                "nodes": next_nodes,
                "edges": next_edges,
                "relationTypes": next_relation_types,
                "nodeIdsInPath": set(state["nodeIdsInPath"]) | {neighbor_id},
            })

    ordered_paths = sorted(raw_paths, key=lambda path: (path["depth"], path["terminalNodeId"], path["edges"]))
    paths = [
        {
            "pathId": f"path.semantic.{index:04d}",
            **path,
        }
        for index, path in enumerate(ordered_paths, start=1)
    ]
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "api/dhatu_semantic_graph.py",
        "nodeId": node_id,
        "maxDepth": normalized_depth,
        "relationType": relation_type,
        "traversalStatus": "OK",
        "visitedNodeCount": len(visited_nodes),
        "pathCount": len(paths),
        "paths": paths,
        "traversedEdgeIds": sorted(traversed_edges),
        "errorCode": None,
    }


def validate_traversal_behaviors(
    edge_path: Any = DEFAULT_EDGE_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> Dict[str, Any]:
    registry = load_json(canonical_registry_path)
    canonical_ids = set(registry.get("records", {}).keys())
    motion = traverse_graph("motion", max_depth=2, edge_path=edge_path, canonical_registry_path=canonical_registry_path, semantic_root=semantic_root)
    gam = traverse_graph("01.0005", max_depth=2, edge_path=edge_path, canonical_registry_path=canonical_registry_path, semantic_root=semantic_root)
    guides = traverse_graph("guidance", max_depth=2, relation_type="guides", edge_path=edge_path, canonical_registry_path=canonical_registry_path, semantic_root=semantic_root)
    unknown = traverse_graph("unknown-semantic-node", max_depth=2, edge_path=edge_path, canonical_registry_path=canonical_registry_path, semantic_root=semantic_root)
    empty = traverse_graph(None, max_depth=2, edge_path=edge_path, canonical_registry_path=canonical_registry_path, semantic_root=semantic_root)
    traversals = [motion, gam, guides]
    duplicate_path_nodes = [
        path["pathId"]
        for traversal in traversals
        for path in traversal["paths"]
        if len([node["nodeId"] for node in path["nodes"]]) != len({node["nodeId"] for node in path["nodes"]})
    ]
    noncanonical_path_dhatu_ids = sorted({
        node["nodeId"]
        for traversal in traversals
        for path in traversal["paths"]
        for node in path["nodes"]
        if node["nodeType"] == "dhatu" and node["nodeId"] not in canonical_ids
    })
    gam_terminal_ids = {path["terminalNodeId"] for path in gam["paths"]}
    guides_terminal_ids = {path["terminalNodeId"] for path in guides["paths"]}
    checks = {
        "motionDepthTwoCycleSafe": duplicate_path_nodes == [] and motion["traversalStatus"] == "OK",
        "gamDepthTwoReachesMotion": "motion" in gam_terminal_ids,
        "guidanceGuidesTraversalWorks": guides["traversalStatus"] == "OK" and "motion" in guides_terminal_ids,
        "unknownNodeSafe": unknown["traversalStatus"] == "NODE_NOT_FOUND" and unknown["errorCode"] == "semantic_graph_node_not_found",
        "emptyNodeSafe": empty["traversalStatus"] == "EMPTY_QUERY" and empty["errorCode"] == "empty_semantic_traversal_query",
        "pathDhatuIdsCanonical": noncanonical_path_dhatu_ids == [],
    }
    return {
        "traversalValidationStatus": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "motionPathCount": motion["pathCount"],
        "gamTerminalNodeIds": sorted(gam_terminal_ids),
        "guidesTerminalNodeIds": sorted(guides_terminal_ids),
        "duplicatePathNodes": duplicate_path_nodes,
        "noncanonicalPathDhatuIds": noncanonical_path_dhatu_ids,
        "unknownNodeStatus": unknown["traversalStatus"],
        "emptyNodeStatus": empty["traversalStatus"],
    }


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
