from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_SEMANTIC_ROOT = ROOT / "data" / "sanskrit" / "dhatus" / "semantic"
IAST_DISPLAY_OVERRIDES = {
    "01.0008": "nī",
    "01.0013": "sthā",
}


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Semantic query source must be a JSON object: {path}")
    return payload


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    return "".join(char for char in text if not unicodedata.combining(char))


def load_semantic_context(
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> Dict[str, Any]:
    root = resolve_path(semantic_root)
    return {
        "canonicalRegistry": load_json(canonical_registry_path),
        "semanticManifest": load_json(root / "semantic_manifest.v1.json"),
        "semanticClusters": load_json(root / "semantic_clusters.v1.json"),
        "actionVectors": load_json(root / "action_vectors.v1.json"),
        "glossTaxonomy": load_json(root / "gloss_taxonomy.v1.json"),
        "derivationGraph": load_json(root / "derivation_graph.v1.json"),
        "paniniReferences": load_json(root / "panini_references.v1.json"),
    }


def _cluster_lookup(context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {cluster["id"]: cluster for cluster in context["semanticClusters"].get("clusters", [])}


def _taxonomy_lookup(context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {entry["id"]: entry for entry in context["glossTaxonomy"].get("taxonomy", [])}


def _panini_lookup(context: Dict[str, Any], dhatu_id: str) -> List[Dict[str, Any]]:
    return [
        reference
        for reference in context["paniniReferences"].get("references", [])
        if reference.get("dhatuId") == dhatu_id
    ]


def _derivation_links(context: Dict[str, Any], dhatu_id: str) -> List[Dict[str, Any]]:
    node_id = f"dhatu:{dhatu_id}"
    return [
        edge
        for edge in context["derivationGraph"].get("edges", [])
        if edge.get("source") == node_id or edge.get("target") == node_id
    ]


def build_result(context: Dict[str, Any], record: Dict[str, Any], rank_score: int, match_reasons: List[str]) -> Dict[str, Any]:
    dhatu_id = record["dhatuId"]
    clusters = _cluster_lookup(context)
    taxonomy = _taxonomy_lookup(context)
    return {
        "dhatuId": dhatu_id,
        "root": record.get("root", ""),
        "iast": IAST_DISPLAY_OVERRIDES.get(dhatu_id, record.get("iast", "")),
        "gloss": record.get("gloss", ""),
        "semanticClusters": [
            clusters.get(cluster_id, {"id": cluster_id})
            for cluster_id in record.get("semanticClusterIds", [])
        ],
        "actionVector": record.get("actionVector", {}),
        "glossTaxonomy": [
            taxonomy.get(taxonomy_id, {"id": taxonomy_id})
            for taxonomy_id in record.get("glossTaxonomyIds", [])
        ],
        "paniniReferences": _panini_lookup(context, dhatu_id),
        "derivationLinks": _derivation_links(context, dhatu_id),
        "rankScore": rank_score,
        "matchReasons": match_reasons,
    }


def query_semantics(
    dhatu_id: Optional[str] = None,
    root: Optional[str] = None,
    iast: Optional[str] = None,
    cluster: Optional[str] = None,
    gloss: Optional[str] = None,
    action: Optional[str] = None,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
    semantic_root: Any = DEFAULT_SEMANTIC_ROOT,
) -> List[Dict[str, Any]]:
    context = load_semantic_context(canonical_registry_path, semantic_root)
    canonical_ids = set(context["canonicalRegistry"].get("records", {}).keys())
    query_iast = normalize_text(iast)
    query_cluster = normalize_text(cluster)
    query_gloss = normalize_text(gloss)
    query_action = normalize_text(action)
    results: List[Dict[str, Any]] = []
    for record in context["actionVectors"].get("records", []):
        record_id = record.get("dhatuId")
        if record_id not in canonical_ids:
            continue
        score = 0
        reasons: List[str] = []
        if dhatu_id and record_id == dhatu_id:
            score += 100
            reasons.append("dhatu-id")
        if root and record.get("root") == root:
            score += 90
            reasons.append("root")
        if iast and normalize_text(record.get("iast")) == query_iast:
            score += 85
            reasons.append("iast")
        if cluster and any(normalize_text(cluster_id) == query_cluster for cluster_id in record.get("semanticClusterIds", [])):
            score += 75
            reasons.append("cluster")
        if gloss and query_gloss in normalize_text(record.get("gloss")):
            score += 65
            reasons.append("gloss")
        if action:
            action_vector = record.get("actionVector", {})
            tokens = [action_vector.get("primary", ""), *action_vector.get("facets", [])]
            if any(query_action in normalize_text(token) for token in tokens):
                score += 70
                reasons.append("action")
        if score:
            results.append(build_result(context, record, score, reasons))
    results.sort(key=lambda item: (-item["rankScore"], item["dhatuId"]))
    return results


def query_payload(**kwargs: Any) -> Dict[str, Any]:
    results = query_semantics(**kwargs)
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "api/dhatu_semantic_query.py",
        "resultCount": len(results),
        "results": results,
    }
