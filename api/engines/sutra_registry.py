from pathlib import Path
from typing import Any, Dict, List
import copy
import json
import unicodedata


ROOT = Path(__file__).resolve().parents[2]
SUTRA_ROOT = ROOT / "data" / "sutras"
SAMPLE_SUTRAS_PATH = SUTRA_ROOT / "sample_sutras.json"

REQUIRED_FIELDS = {
    "sutra_id",
    "sutra_text_devanagari",
    "sutra_text_iast",
    "chapter",
    "pada",
    "sutra_number",
    "domain",
    "source",
    "source_type",
    "status",
    "provenance",
    "notes",
}

VALID_DOMAINS = {
    "vowel_sandhi",
    "visarga_sandhi",
    "consonant_sandhi",
    "morphology",
    "governance",
    "orchestration",
}
VALID_SOURCE_TYPES = {"ashtadhyayi", "commentary", "internal_registry"}
VALID_STATUSES = {"canonical", "provisional", "deprecated"}


class SutraRegistryValidator:
    def normalize_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(entry, dict):
            raise ValueError("Sutra entry must be a dict.")

        normalized = copy.deepcopy(entry)
        for field_name in ("sutra_id", "sutra_text_devanagari", "sutra_text_iast", "sutra_number", "source", "notes"):
            value = normalized.get(field_name)
            if not isinstance(value, str):
                raise ValueError(f"{field_name} is required.")
            normalized[field_name] = unicodedata.normalize("NFC", value)
        return normalized

    def validate_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self.normalize_entry(entry)

        missing_fields = sorted(REQUIRED_FIELDS - set(normalized.keys()))
        if missing_fields:
            raise ValueError(f"Sutra entry missing required fields: {', '.join(missing_fields)}.")

        for field_name in ("sutra_id", "sutra_text_devanagari", "sutra_text_iast", "sutra_number", "source"):
            if not normalized[field_name].strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        if not isinstance(normalized["chapter"], int) or not 1 <= normalized["chapter"] <= 8:
            raise ValueError("chapter must be an integer from 1 to 8.")
        if not isinstance(normalized["pada"], int) or not 1 <= normalized["pada"] <= 4:
            raise ValueError("pada must be an integer from 1 to 4.")
        if not normalized["sutra_number"].isdigit():
            raise ValueError("sutra_number must be a numeric string.")

        expected_prefix = f"{normalized['chapter']}.{normalized['pada']}."
        if not normalized["sutra_id"].startswith(expected_prefix):
            raise ValueError("sutra_id must match chapter and pada.")
        if normalized["sutra_id"].split(".")[-1] != normalized["sutra_number"]:
            raise ValueError("sutra_id must match sutra_number.")

        if normalized["domain"] not in VALID_DOMAINS:
            raise ValueError(f"Invalid sutra domain: {normalized['domain']}.")
        if normalized["source_type"] not in VALID_SOURCE_TYPES:
            raise ValueError(f"Invalid source_type: {normalized['source_type']}.")
        if normalized["status"] not in VALID_STATUSES:
            raise ValueError(f"Invalid sutra status: {normalized['status']}.")
        if not isinstance(normalized["provenance"], dict):
            raise ValueError("provenance must be a dict.")

        return normalized

    def load_sample_sutras(self) -> List[Dict[str, Any]]:
        with SAMPLE_SUTRAS_PATH.open("r", encoding="utf-8") as handle:
            sutras = json.load(handle)
        if not isinstance(sutras, list):
            raise ValueError("Sample sutra registry must be a list.")
        return sutras

    def validate_registry(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(entries, list):
            raise ValueError("Sutra registry must be a list.")

        seen_ids = set()
        normalized_entries = []
        for entry in entries:
            normalized = self.validate_entry(entry)
            sutra_id = normalized["sutra_id"]
            if sutra_id in seen_ids:
                raise ValueError(f"Duplicate sutra_id: {sutra_id}.")
            seen_ids.add(sutra_id)
            normalized_entries.append(normalized)
        return normalized_entries
