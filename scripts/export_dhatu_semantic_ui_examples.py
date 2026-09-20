#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.kernel_api import (
    build_dhatu_semantic_graph_neighbors_response,
    build_dhatu_semantic_search_response,
    build_dhatu_semantic_traversal_response,
)


EXAMPLES_DIR = ROOT / "data" / "sanskrit" / "dhatus" / "semantic" / "examples" / "ui"
GENERATED_BY = "scripts/export_dhatu_semantic_ui_examples.py"
SAFETY_NOTE = "Semantic graph links are foundation-placeholder UI context only; no exact Pāṇinian derivation claim is made."


def card(card_id: str, card_type: str, label: str, value: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "cardId": card_id,
        "cardType": card_type,
        "label": label,
        "value": value,
        "metadata": metadata,
    }


def link(label: str, href: str, link_type: str) -> Dict[str, str]:
    return {
        "label": label,
        "href": href,
        "linkType": link_type,
    }


def primary_dhatu_from_search(search_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = search_payload["results"][0] if search_payload.get("results") else {}
    return {
        "dhatuId": result.get("dhatuId"),
        "root": result.get("root"),
        "iast": result.get("iast"),
        "gloss": result.get("gloss"),
    }


def panel(
    panel_type: str,
    title: str,
    description: str,
    primary_dhatu: Dict[str, Any],
    cards: List[Dict[str, Any]],
    links: List[Dict[str, str]],
) -> Dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": GENERATED_BY,
        "panelType": panel_type,
        "title": title,
        "description": description,
        "primaryDhatu": primary_dhatu,
        "cards": cards,
        "links": links,
        "safetyNote": SAFETY_NOTE,
    }


def build_search_panel(search_payload: Dict[str, Any]) -> Dict[str, Any]:
    primary = primary_dhatu_from_search(search_payload)
    cards = [
        card(
            "search.result.01",
            "searchResult",
            "Search result",
            primary["iast"],
            {
                "section": "Search Results",
                "dhatuId": primary["dhatuId"],
                "root": primary["root"],
                "gloss": primary["gloss"],
                "matchReasons": search_payload["results"][0].get("matchReasons", []),
                "rankScore": search_payload["results"][0].get("rankScore"),
            },
        ),
        card(
            "search.query.01",
            "querySummary",
            "Semantic query",
            "cluster=motion",
            {
                "section": "Search Results",
                "resultCount": search_payload.get("resultCount", 0),
                "endpoint": "/api/dhatu/semantic/search",
            },
        ),
    ]
    return panel(
        "semanticSearch",
        "Semantic Search Panel",
        "UI-ready summary of a motion-cluster semantic search for gam.",
        primary,
        cards,
        [
            link("Semantic search API", "/api/dhatu/semantic/search?cluster=motion", "api"),
            link("Search example fixture", "data/sanskrit/dhatus/semantic/examples/search_by_cluster_motion.response.v1.json", "fixture"),
        ],
    )


def build_neighbor_panel(search_payload: Dict[str, Any], neighbor_payload: Dict[str, Any]) -> Dict[str, Any]:
    primary = primary_dhatu_from_search(search_payload)
    cards = [
        card(
            f"neighbor.{index:02d}",
            "semanticNeighbor",
            neighbor["nodeId"],
            neighbor["nodeType"],
            {
                "section": "Semantic Neighbors",
                "depth": neighbor["depth"],
                "relationTypes": neighbor["relationTypes"],
                "viaEdgeIds": neighbor["viaEdgeIds"],
            },
        )
        for index, neighbor in enumerate(neighbor_payload.get("neighbors", []), start=1)
    ]
    cards.append(
        card(
            "neighbor.summary.01",
            "graphSummary",
            "Neighbor count",
            neighbor_payload.get("neighborCount", 0),
            {
                "section": "Semantic Neighbors",
                "nodeId": neighbor_payload.get("nodeId"),
                "traversedEdgeIds": neighbor_payload.get("traversedEdgeIds", []),
            },
        )
    )
    return panel(
        "semanticNeighbor",
        "Semantic Neighbor Panel",
        "UI-ready neighbor cards for canonical dhatu 01.0005.",
        primary,
        cards,
        [
            link("Semantic neighbors API", "/api/dhatu/semantic/neighbors?nodeId=01.0005", "api"),
            link("Neighbor example fixture", "data/sanskrit/dhatus/semantic/examples/graph/neighbor_01_0005.response.v1.json", "fixture"),
        ],
    )


def build_traversal_panel(search_payload: Dict[str, Any], traversal_payload: Dict[str, Any]) -> Dict[str, Any]:
    primary = primary_dhatu_from_search(search_payload)
    cards = [
        card(
            path["pathId"],
            "traversalPath",
            path["terminalNodeId"],
            " -> ".join(node["nodeId"] for node in path["nodes"]),
            {
                "section": "Traversal Paths",
                "depth": path["depth"],
                "edges": path["edges"],
                "relationTypes": path["relationTypes"],
            },
        )
        for path in traversal_payload.get("paths", [])
    ]
    cards.append(
        card(
            "traversal.summary.01",
            "traversalSummary",
            "Traversal path count",
            traversal_payload.get("pathCount", 0),
            {
                "section": "Traversal Paths",
                "nodeId": traversal_payload.get("nodeId"),
                "maxDepth": traversal_payload.get("maxDepth"),
                "visitedNodeCount": traversal_payload.get("visitedNodeCount"),
                "traversedEdgeIds": traversal_payload.get("traversedEdgeIds", []),
            },
        )
    )
    return panel(
        "semanticTraversal",
        "Semantic Traversal Panel",
        "UI-ready traversal path cards for motion at depth 2.",
        primary,
        cards,
        [
            link("Semantic traversal API", "/api/dhatu/semantic/traverse?nodeId=motion&maxDepth=2", "api"),
            link("Traversal example fixture", "data/sanskrit/dhatus/semantic/examples/graph/traversal_motion_depth2.response.v1.json", "fixture"),
        ],
    )


def build_combined_panel(
    search_payload: Dict[str, Any],
    neighbor_payload: Dict[str, Any],
    traversal_payload: Dict[str, Any],
) -> Dict[str, Any]:
    primary = primary_dhatu_from_search(search_payload)
    search_result = search_payload["results"][0]
    cards = [
        card(
            "combined.search.01",
            "searchResult",
            "Search Results",
            f"{search_result['iast']} / {search_result['root']}",
            {
                "section": "Search Results",
                "dhatuId": search_result["dhatuId"],
                "root": search_result["root"],
                "gloss": search_result["gloss"],
                "matchReasons": search_result.get("matchReasons", []),
            },
        ),
        card(
            "combined.neighbor.01",
            "semanticNeighbor",
            "Semantic Neighbors",
            neighbor_payload["neighbors"][0]["nodeId"],
            {
                "section": "Semantic Neighbors",
                "neighborCount": neighbor_payload["neighborCount"],
                "traversedEdgeIds": neighbor_payload["traversedEdgeIds"],
                "relationTypes": neighbor_payload["neighbors"][0]["relationTypes"],
            },
        ),
        card(
            "combined.traversal.01",
            "traversalPath",
            "Traversal Paths",
            " -> ".join(node["nodeId"] for node in traversal_payload["paths"][0]["nodes"]),
            {
                "section": "Traversal Paths",
                "pathCount": traversal_payload["pathCount"],
                "visitedNodeCount": traversal_payload["visitedNodeCount"],
                "traversedEdgeIds": traversal_payload["traversedEdgeIds"],
            },
        ),
    ]
    return panel(
        "semanticCombined",
        "Semantic Combined Panel",
        "Combined UI payload for search, neighbor, and traversal sections.",
        primary,
        cards,
        [
            link("Semantic search API", "/api/dhatu/semantic/search?cluster=motion", "api"),
            link("Semantic neighbors API", "/api/dhatu/semantic/neighbors?nodeId=01.0005", "api"),
            link("Semantic traversal API", "/api/dhatu/semantic/traverse?nodeId=motion&maxDepth=2", "api"),
        ],
    )


def build_examples() -> Dict[str, Dict[str, Any]]:
    search_payload = build_dhatu_semantic_search_response(cluster="motion")
    neighbor_payload = build_dhatu_semantic_graph_neighbors_response(nodeId="01.0005")
    traversal_payload = build_dhatu_semantic_traversal_response(nodeId="motion", maxDepth=2)
    return {
        "ui_semantic_search_panel.v1.json": build_search_panel(search_payload),
        "ui_semantic_neighbor_panel.v1.json": build_neighbor_panel(search_payload, neighbor_payload),
        "ui_semantic_traversal_panel.v1.json": build_traversal_panel(search_payload, traversal_payload),
        "ui_semantic_combined_panel.v1.json": build_combined_panel(search_payload, neighbor_payload, traversal_payload),
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
        "generatedBy": GENERATED_BY,
        "exampleCount": len(written),
        "examples": sorted(written),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
