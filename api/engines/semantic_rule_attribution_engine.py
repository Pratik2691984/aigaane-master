from typing import Any, Dict, List, Optional
import copy


class SemanticRuleAttributionEngine:
    def attribute_semantics(self, trace_payload: Dict[str, Any], semantic_rules: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if not isinstance(trace_payload, dict):
            raise ValueError("Semantic attribution input must be a dictionary.")

        rules = [rule for rule in (semantic_rules or []) if isinstance(rule, dict)]
        steps = self._steps(trace_payload)
        attributions = []
        for step in steps:
            step_id = str(step.get("step_id") or step.get("stepId") or step.get("node_id") or step.get("frame_id") or "")
            sutra_id = self._first_value(step, ("sutra", "sutra_id", "sutraId"))
            for semantic_tag, confidence, source in self._tags_for_step(step, sutra_id, rules):
                if not semantic_tag:
                    continue
                attributions.append(
                    {
                        "stepId": step_id,
                        "sutraId": sutra_id,
                        "semanticTag": semantic_tag,
                        "confidence": round(max(0.0, min(1.0, confidence)), 4),
                        "source": source,
                    }
                )

        return {
            "semanticAttributionVersion": "1.0",
            "semanticAttributions": attributions,
        }

    def _steps(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        for key in ("steps", "timeline", "nodes", "trace"):
            value = payload.get(key)
            if isinstance(value, list):
                return [copy.deepcopy(item) for item in value if isinstance(item, dict)]
        return []

    def _tags_for_step(self, step: Dict[str, Any], sutra_id: Optional[str], rules: List[Dict[str, Any]]) -> List[tuple]:
        explicit = []
        for key in ("semanticTag", "semantic_tag", "tag"):
            if step.get(key):
                explicit.append((str(step[key]), float(step.get("confidence", 0.85)), str(step.get("source", "manual"))))
        semantic = step.get("semantic")
        if isinstance(semantic, dict):
            tag = semantic.get("semanticTag") or semantic.get("semantic_tag") or semantic.get("tag")
            if tag:
                explicit.append((str(tag), float(semantic.get("confidence", 0.8)), str(semantic.get("source", "derived"))))
        for rule in rules:
            rule_sutra = rule.get("sutraId") or rule.get("sutra_id") or rule.get("sutra")
            if rule_sutra and sutra_id and str(rule_sutra) == str(sutra_id):
                explicit.append(
                    (
                        str(rule.get("semanticTag") or rule.get("semantic_tag") or rule.get("tag")),
                        float(rule.get("confidence", 0.9)),
                        str(rule.get("source", "rule")),
                    )
                )
        return explicit

    def _first_value(self, value: Any, keys: tuple) -> Optional[str]:
        if isinstance(value, dict):
            for key in keys:
                if value.get(key):
                    return str(value[key])
            for child in value.values():
                found = self._first_value(child, keys)
                if found:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = self._first_value(child, keys)
                if found:
                    return found
        return None
