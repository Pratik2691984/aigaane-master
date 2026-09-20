from typing import Any, Dict, List, Tuple


class ProvenanceScoringEngine:
    COMPONENT_WEIGHTS = {
        "sutraCoverage": 0.25,
        "traceCompleteness": 0.20,
        "ambiguityResolutionConfidence": 0.20,
        "semanticAttributionConfidence": 0.20,
        "replayReproducibility": 0.15,
    }

    def score_derivation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Provenance scoring input must be a dictionary.")

        steps = self._steps(payload)
        branches = self._branches(payload)
        semantic_attributions = self._semantic_attributions(payload)
        components = {
            "sutraCoverage": self._sutra_coverage(steps),
            "traceCompleteness": self._trace_completeness(steps),
            "ambiguityResolutionConfidence": self._ambiguity_confidence(branches),
            "semanticAttributionConfidence": self._semantic_confidence(semantic_attributions, steps),
            "replayReproducibility": self._replay_reproducibility(payload, steps),
        }
        score = round(sum(components[key] * weight for key, weight in self.COMPONENT_WEIGHTS.items()), 4)

        return {
            "provenanceVersion": "1.0",
            "score": score,
            "grade": self._grade(score),
            "components": components,
            "explanation": self._explanation(components),
        }

    def _steps(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        for key in ("steps", "timeline", "nodes"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return []

    def _branches(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        for key in ("ambiguity_branches", "ambiguityBranches", "branches"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return []

    def _semantic_attributions(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        attributions = []
        for key in ("semanticAttributions", "semantic_attributions", "semantic_annotations", "semanticAnnotations"):
            value = payload.get(key)
            if isinstance(value, list):
                attributions.extend(item for item in value if isinstance(item, dict))
        for step in self._steps(payload):
            for key in ("semanticAttributions", "semantic_attributions", "semantic_annotations", "semanticAnnotations"):
                value = step.get(key)
                if isinstance(value, list):
                    attributions.extend(item for item in value if isinstance(item, dict))
            semantic = step.get("semantic")
            if isinstance(semantic, dict):
                attributions.append(semantic)
        return attributions

    def _sutra_coverage(self, steps: List[Dict[str, Any]]) -> float:
        if not steps:
            return 0.0
        with_sutra = sum(1 for step in steps if self._has_key_recursive(step, {"sutra", "sutra_id", "sutraId"}))
        return round(with_sutra / len(steps), 4)

    def _trace_completeness(self, steps: List[Dict[str, Any]]) -> float:
        if not steps:
            return 0.0
        complete = 0
        for step in steps:
            has_input = any(key in step for key in ("input_state", "inputState", "input"))
            has_output = any(key in step for key in ("output_state", "outputState", "output"))
            has_operation = any(key in step for key in ("operation", "title", "engine"))
            if has_input and has_output and has_operation:
                complete += 1
        return round(complete / len(steps), 4)

    def _ambiguity_confidence(self, branches: List[Dict[str, Any]]) -> float:
        if not branches:
            return 1.0
        selected = 0
        rejected = 0
        explicit_confidences = []
        for branch in branches:
            decision = str(branch.get("status") or branch.get("decision") or "").lower()
            if decision in {"selected", "accepted", "canonical"}:
                selected += 1
            if decision in {"rejected", "discarded"}:
                rejected += 1
            if isinstance(branch.get("confidence"), (int, float)):
                explicit_confidences.append(float(branch["confidence"]))
        if explicit_confidences:
            return round(max(0.0, min(1.0, sum(explicit_confidences) / len(explicit_confidences))), 4)
        if selected:
            return round(min(1.0, (selected + rejected) / len(branches)), 4)
        return 0.5

    def _semantic_confidence(self, attributions: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> float:
        if not attributions:
            return 1.0 if not steps else 0.0
        confidences = [float(item["confidence"]) for item in attributions if isinstance(item.get("confidence"), (int, float))]
        if confidences:
            return round(max(0.0, min(1.0, sum(confidences) / len(confidences))), 4)
        linked = sum(1 for item in attributions if item.get("semanticTag") or item.get("semantic_tag") or item.get("tag"))
        return round(linked / len(attributions), 4)

    def _replay_reproducibility(self, payload: Dict[str, Any], steps: List[Dict[str, Any]]) -> float:
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        has_id = bool(payload.get("replay_id") or metadata.get("session_id") or payload.get("session_id"))
        has_ordered_steps = all(step.get("step_id") or step.get("stepId") or step.get("node_id") for step in steps)
        has_total = "total_frames" in metadata or "total_nodes" in metadata or "total_steps" in payload
        points = sum([has_id, has_ordered_steps, has_total])
        return round(points / 3, 4)

    def _has_key_recursive(self, value: Any, keys: set) -> bool:
        if isinstance(value, dict):
            return any(key in value and value[key] for key in keys) or any(self._has_key_recursive(child, keys) for child in value.values())
        if isinstance(value, list):
            return any(self._has_key_recursive(child, keys) for child in value)
        return False

    def _grade(self, score: float) -> str:
        if score >= 0.9:
            return "canonical"
        if score >= 0.7:
            return "high"
        if score >= 0.4:
            return "medium"
        return "low"

    def _explanation(self, components: Dict[str, float]) -> List[str]:
        labels: List[Tuple[str, str]] = [
            ("sutraCoverage", "Sutra coverage"),
            ("traceCompleteness", "Trace completeness"),
            ("ambiguityResolutionConfidence", "Ambiguity resolution"),
            ("semanticAttributionConfidence", "Semantic attribution"),
            ("replayReproducibility", "Replay reproducibility"),
        ]
        return [f"{label}: {components[key]:.2f}" for key, label in labels]
