from typing import Any, Dict, List

from engines.ambiguity import AmbiguityCandidate, make_ambiguous, make_unambiguous


class ExecutableAmbiguityDAG:
    def execute_fork(self, engine_node: str, variants: list[dict]) -> dict:
        if not variants:
            return {
                "is_ambiguous": False,
                "candidates": [],
                "strategy": "none",
                "selected_candidate_id": None,
            }

        candidates = [
            self._candidate_from_variant(index, engine_node, variant)
            for index, variant in enumerate(variants)
        ]

        if len(candidates) == 1:
            payload = make_unambiguous()
            return payload.model_copy(update={"candidates": candidates}).model_dump()

        return make_ambiguous(candidates, strategy="enumeration_only").model_dump()

    def _candidate_from_variant(
        self,
        index: int,
        engine_node: str,
        variant: Dict[str, Any],
    ) -> AmbiguityCandidate:
        if "final_output" not in variant:
            raise ValueError("Ambiguity DAG variant is missing required final_output.")

        derivation_path = variant.get("derivation_path", [])
        if not isinstance(derivation_path, list):
            derivation_path = []

        return AmbiguityCandidate(
            candidate_id=str(index),
            final_output=str(variant["final_output"]),
            source_engine=engine_node,
            confidence=None,
            reason=variant.get("reason") or "Alternative derivation candidate",
            derivation_path=derivation_path,
        )
