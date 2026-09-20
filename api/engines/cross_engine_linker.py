from typing import Any, Dict, List, Optional
import copy

try:
    from api.engines.lexical_registry import LexicalRegistryValidator
    from api.engines.sutra_registry import SutraRegistryValidator
except ModuleNotFoundError:
    from engines.lexical_registry import LexicalRegistryValidator
    from engines.sutra_registry import SutraRegistryValidator


class CrossEngineLinker:
    def __init__(
        self,
        lexical_validator: Optional[LexicalRegistryValidator] = None,
        sutra_validator: Optional[SutraRegistryValidator] = None,
        semantic_registry: Optional[Dict[str, Any]] = None,
    ):
        self.lexical_validator = lexical_validator or LexicalRegistryValidator()
        self.sutra_validator = sutra_validator or SutraRegistryValidator()
        self.semantic_registry = semantic_registry or {}

    def link(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Cross-engine link input must be a dictionary.")

        sutra_index = self._sutra_index()
        lexical_index = self._lexical_index()
        sutra_refs = sorted(self._collect_values(payload, {"sutra", "sutra_id", "sutraId"}))
        semantic_refs = sorted(self._collect_values(payload, {"semanticTag", "semantic_tag", "tag"}))
        lexical_refs = sorted(self._collect_values(payload, {"lexical_id", "lexicalId", "dhatu_id", "dhatuId", "lemma_iast"}))

        return {
            "crossEngineLinkVersion": "1.0",
            "links": {
                "sutraRegistry": [self._reference("sutra", ref, sutra_index.get(ref)) for ref in sutra_refs],
                "dhatuRegistry": [self._reference("dhatu", ref, lexical_index.get(ref)) for ref in lexical_refs],
                "semanticRegistry": [self._reference("semantic", ref, self.semantic_registry.get(ref)) for ref in semantic_refs],
                "bijaRegistry": [{"type": "bija", "id": None, "status": "reserved_future_reference"}],
                "vector49DLayer": [{"type": "49d_vector", "id": None, "status": "reserved_future_reference"}],
            },
        }

    def _sutra_index(self) -> Dict[str, Dict[str, Any]]:
        try:
            entries = self.sutra_validator.validate_registry(self.sutra_validator.load_sample_sutras())
        except Exception:
            return {}
        return {entry["sutra_id"]: copy.deepcopy(entry) for entry in entries}

    def _lexical_index(self) -> Dict[str, Dict[str, Any]]:
        try:
            entries = self.lexical_validator.validate_registry(self.lexical_validator.load_sample_entries())
        except Exception:
            return {}
        index = {}
        for entry in entries:
            for key in ("lexical_id", "lemma_iast", "lemma_devanagari"):
                if entry.get(key):
                    index[str(entry[key])] = copy.deepcopy(entry)
        return index

    def _reference(self, ref_type: str, ref_id: str, entry: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        reference = {"type": ref_type, "id": ref_id, "resolved": entry is not None}
        if entry is not None:
            reference["registryEntry"] = copy.deepcopy(entry)
        return reference

    def _collect_values(self, value: Any, keys: set) -> set:
        values = set()
        if isinstance(value, dict):
            for key, child in value.items():
                if key in keys and child:
                    values.add(str(child))
                else:
                    values.update(self._collect_values(child, keys))
        elif isinstance(value, list):
            for child in value:
                values.update(self._collect_values(child, keys))
        return values
