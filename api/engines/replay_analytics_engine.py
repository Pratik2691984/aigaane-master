from typing import Any, Dict, List, Set
from collections import Counter, defaultdict, deque
import copy


class ReplayAnalyticsEngine:
    def compute_analytics(self, export_payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(export_payload, dict):
            raise ValueError("Analytics input must be a dictionary.")

        nodes = self._nodes(export_payload)
        edges = self._edges(export_payload)
        frames = self._timeline(export_payload)
        analysis_items = nodes or frames

        return {
            "analyticsVersion": "1.0",
            "nodeCount": len(nodes) if nodes else len(frames),
            "edgeCount": len(edges),
            "ambiguityCount": self._ambiguity_count(export_payload, analysis_items),
            "maxDepth": self._max_depth(nodes, edges) if nodes else len(frames),
            "selectedPathLength": self._selected_path_length(export_payload, analysis_items),
            "rejectedBranchCount": self._rejected_branch_count(export_payload),
            "semanticTagDistribution": dict(sorted(self._semantic_tags(export_payload, analysis_items).items())),
            "sutraFrequency": dict(sorted(self._sutra_frequency(analysis_items).items())),
        }

    def _nodes(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        nodes = payload.get("nodes", [])
        return [copy.deepcopy(node) for node in nodes if isinstance(node, dict)] if isinstance(nodes, list) else []

    def _edges(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        edges = payload.get("edges", [])
        return [copy.deepcopy(edge) for edge in edges if isinstance(edge, dict)] if isinstance(edges, list) else []

    def _timeline(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        timeline = payload.get("timeline", [])
        return [copy.deepcopy(frame) for frame in timeline if isinstance(frame, dict)] if isinstance(timeline, list) else []

    def _ambiguity_count(self, payload: Dict[str, Any], items: List[Dict[str, Any]]) -> int:
        branch_ids: Set[str] = set()
        for item in items:
            for key in ("ambiguity_branch_ids", "ambiguityBranchIds"):
                value = item.get(key)
                if isinstance(value, list):
                    branch_ids.update(str(branch_id) for branch_id in value)
        for key in ("ambiguity_branches", "ambiguityBranches", "branches"):
            value = payload.get(key)
            if isinstance(value, list):
                for index, branch in enumerate(value):
                    if isinstance(branch, dict):
                        branch_ids.add(str(branch.get("branch_id") or branch.get("candidate_id") or index))
        return len(branch_ids)

    def _max_depth(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> int:
        if not nodes:
            return 0
        node_ids = {str(node.get("node_id") or node.get("id") or node.get("step_id")) for node in nodes}
        children = defaultdict(list)
        incoming = set()
        for edge in edges:
            source = edge.get("source") or edge.get("from")
            target = edge.get("target") or edge.get("to")
            if source and target:
                source_id = str(source)
                target_id = str(target)
                children[source_id].append(target_id)
                incoming.add(target_id)
        roots = sorted(node_ids - incoming) or sorted(node_ids)
        max_depth = 0
        queue = deque((root, 1) for root in roots)
        seen = set()
        while queue:
            node_id, depth = queue.popleft()
            if (node_id, depth) in seen:
                continue
            seen.add((node_id, depth))
            max_depth = max(max_depth, depth)
            for child in children.get(node_id, []):
                queue.append((child, depth + 1))
        return max_depth

    def _selected_path_length(self, payload: Dict[str, Any], items: List[Dict[str, Any]]) -> int:
        selected = payload.get("selected_path") or payload.get("selectedPath")
        if isinstance(selected, list):
            return len(selected)
        selected_items = [item for item in items if item.get("selected") is True or item.get("is_selected") is True]
        return len(selected_items) if selected_items else len(items)

    def _rejected_branch_count(self, payload: Dict[str, Any]) -> int:
        rejected = 0
        for key in ("ambiguity_branches", "ambiguityBranches", "branches"):
            value = payload.get(key)
            if isinstance(value, list):
                for branch in value:
                    if isinstance(branch, dict) and str(branch.get("status") or branch.get("decision")).lower() in {"rejected", "discarded"}:
                        rejected += 1
        return rejected

    def _semantic_tags(self, payload: Dict[str, Any], items: List[Dict[str, Any]]) -> Counter:
        tags = Counter()
        for item in items:
            self._collect_semantic_tags(item, tags)
        for key in ("semanticAttributions", "semantic_attributions", "semantic_annotations", "semanticAnnotations"):
            value = payload.get(key)
            if isinstance(value, list):
                for annotation in value:
                    self._collect_semantic_tags(annotation, tags)
        return tags

    def _sutra_frequency(self, items: List[Dict[str, Any]]) -> Counter:
        sutras = Counter()
        for item in items:
            self._collect_sutras(item, sutras)
        return sutras

    def _collect_semantic_tags(self, value: Any, tags: Counter) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"semanticTag", "semantic_tag", "tag"} and child:
                    tags[str(child)] += 1
                else:
                    self._collect_semantic_tags(child, tags)
        elif isinstance(value, list):
            for child in value:
                self._collect_semantic_tags(child, tags)

    def _collect_sutras(self, value: Any, sutras: Counter) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"sutra", "sutra_id", "sutraId"} and child:
                    sutras[str(child)] += 1
                else:
                    self._collect_sutras(child, sutras)
        elif isinstance(value, list):
            for child in value:
                self._collect_sutras(child, sutras)
