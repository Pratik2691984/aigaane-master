from typing import Any, Dict, List, Optional
import copy

try:
    from api.engines.sutra_registry import SutraRegistryValidator
except ModuleNotFoundError:
    from engines.sutra_registry import SutraRegistryValidator


class SutraTraceLinker:
    def __init__(self, validator: Optional[SutraRegistryValidator] = None):
        self.validator = validator or SutraRegistryValidator()
        self._registry_index: Optional[Dict[str, Dict[str, Any]]] = None

    def load_registry(self) -> Dict[str, Dict[str, Any]]:
        entries = self.validator.load_sample_sutras()
        validated_entries = self.validator.validate_registry(entries)
        self._registry_index = {
            entry["sutra_id"]: copy.deepcopy(entry)
            for entry in validated_entries
        }
        return copy.deepcopy(self._registry_index)

    def resolve_sutra(self, sutra_id: str) -> Optional[Dict[str, Any]]:
        if self._registry_index is None:
            self.load_registry()
        if not isinstance(sutra_id, str):
            return None
        sutra = self._registry_index.get(sutra_id) if self._registry_index is not None else None
        return copy.deepcopy(sutra) if sutra is not None else None

    def link_trace_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(step, dict):
            linked_step = {"sutra_ref": None}
            return linked_step

        linked_step = copy.deepcopy(step)
        linked_step["sutra_ref"] = self.resolve_sutra(linked_step.get("sutra"))
        return linked_step

    def link_trace(self, trace_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(trace_steps, list):
            return []
        return [self.link_trace_step(step) for step in trace_steps]
