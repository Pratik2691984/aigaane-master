from typing import Any, Dict, List


class SemanticQueryEngine:
    def query(self, corpus: List[Dict[str, Any]], query: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not isinstance(corpus, list):
            raise ValueError("Semantic query corpus must be a list.")
        if not isinstance(query, dict):
            raise ValueError("Semantic query must be a dictionary.")
        query_type = query.get("type")
        handlers = {
            "sutra": self._matches_sutra,
            "has_ambiguity": self._matches_ambiguity,
            "semantic_tag": self._matches_semantic_tag,
            "pada_rule": self._matches_pada_rule,
            "provenance_min": self._matches_provenance_min,
        }
        if query_type not in handlers:
            raise ValueError(f"Unsupported semantic query type: {query_type}")
        matcher = handlers[query_type]
        results = []
        for index, item in enumerate(corpus):
            if not isinstance(item, dict):
                continue
            if matcher(item, query):
                results.append(self._result(item, index, query_type))
        return results

    def find_derivations_using_sutra(self, corpus: List[Dict[str, Any]], sutra_id: str) -> List[Dict[str, Any]]:
        return self.query(corpus, {"type": "sutra", "sutraId": sutra_id})

    def find_traces_with_ambiguity(self, corpus: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self.query(corpus, {"type": "has_ambiguity"})

    def find_outputs_linked_to_semantic_tag(self, corpus: List[Dict[str, Any]], tag: str) -> List[Dict[str, Any]]:
        return self.query(corpus, {"type": "semantic_tag", "semanticTag": tag})

    def find_dhatus_with_pada_rule(self, corpus: List[Dict[str, Any]], sutra_id: str) -> List[Dict[str, Any]]:
        return self.query(corpus, {"type": "pada_rule", "sutraId": sutra_id})

    def find_replay_sessions_above_provenance(self, corpus: List[Dict[str, Any]], minimum_score: float) -> List[Dict[str, Any]]:
        return self.query(corpus, {"type": "provenance_min", "minimumScore": minimum_score})

    def _matches_sutra(self, item: Dict[str, Any], query: Dict[str, Any]) -> bool:
        return str(query.get("sutraId")) in self._collect_values(item, {"sutra", "sutra_id", "sutraId"})

    def _matches_ambiguity(self, item: Dict[str, Any], query: Dict[str, Any]) -> bool:
        if self._collect_values(item, {"ambiguity_branch_ids", "ambiguityBranchIds"}):
            return True
        for key in ("ambiguity_branches", "ambiguityBranches", "branches"):
            value = item.get(key)
            if isinstance(value, list) and len(value) > 0:
                return True
        return False

    def _matches_semantic_tag(self, item: Dict[str, Any], query: Dict[str, Any]) -> bool:
        return str(query.get("semanticTag")) in self._collect_values(item, {"semanticTag", "semantic_tag", "tag"})

    def _matches_pada_rule(self, item: Dict[str, Any], query: Dict[str, Any]) -> bool:
        sutra_id = str(query.get("sutraId"))
        if sutra_id not in self._collect_values(item, {"sutra", "sutra_id", "sutraId", "padaRule", "pada_rule"}):
            return False
        category_values = self._collect_values(item, {"category", "kind", "type"})
        return not category_values or bool(category_values & {"verb", "dhatu", "verbal"})

    def _matches_provenance_min(self, item: Dict[str, Any], query: Dict[str, Any]) -> bool:
        minimum = float(query.get("minimumScore", 0.0))
        score = item.get("provenanceScore") or item.get("provenance_score")
        if isinstance(score, dict):
            score = score.get("score")
        return isinstance(score, (int, float)) and float(score) >= minimum

    def _collect_values(self, value: Any, keys: set) -> set:
        values = set()
        if isinstance(value, dict):
            for key, child in value.items():
                if key in keys and child:
                    if isinstance(child, list):
                        values.update(str(item) for item in child)
                    else:
                        values.add(str(child))
                else:
                    values.update(self._collect_values(child, keys))
        elif isinstance(value, list):
            for child in value:
                values.update(self._collect_values(child, keys))
        return values

    def _result(self, item: Dict[str, Any], index: int, query_type: str) -> Dict[str, Any]:
        item_id = (
            item.get("replay_id")
            or item.get("session_id")
            or item.get("id")
            or item.get("lexical_id")
            or f"item_{index}"
        )
        return {
            "id": str(item_id),
            "type": query_type,
            "item": item,
            "reason": f"matched {query_type}",
        }
