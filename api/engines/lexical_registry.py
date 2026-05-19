from pathlib import Path
from typing import Any, Dict, List
import copy
import json
import unicodedata


ROOT = Path(__file__).resolve().parents[2]
LEXICON_ROOT = ROOT / "data" / "lexicon"
SAMPLE_ENTRIES_PATH = LEXICON_ROOT / "sample_entries.json"

REQUIRED_FIELDS = {
    "lexical_id",
    "lemma_devanagari",
    "lemma_iast",
    "category",
    "gender",
    "stem_class",
    "dhatu_class",
    "meaning",
    "source",
    "normalization",
    "status",
}
SOURCE_REQUIRED_FIELDS = {"name", "type", "citation", "license", "verified"}
NORMALIZATION_REQUIRED_FIELDS = {"unicode", "script_policy"}

VALID_CATEGORIES = {"noun", "verb", "indeclinable", "unknown"}
VALID_GENDERS = {"masculine", "feminine", "neuter", None}
VALID_SOURCE_TYPES = {"manual", "dictionary", "corpus", "app", "scholarly"}
VALID_STATUSES = {"validated", "draft", "rejected"}


class LexicalRegistryValidator:
    def normalize_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(entry, dict):
            raise ValueError("Lexical entry must be a dict.")

        normalized = copy.deepcopy(entry)
        for field_name in ("lemma_devanagari", "lemma_iast"):
            value = normalized.get(field_name)
            if not isinstance(value, str):
                raise ValueError(f"{field_name} is required.")
            normalized[field_name] = unicodedata.normalize("NFC", value)
        return normalized

    def validate_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        normalized = self.normalize_entry(entry)

        missing_fields = sorted(REQUIRED_FIELDS - set(normalized.keys()))
        if missing_fields:
            raise ValueError(f"Lexical entry missing required fields: {', '.join(missing_fields)}.")

        for field_name in ("lexical_id", "lemma_devanagari", "lemma_iast"):
            if not isinstance(normalized.get(field_name), str) or not normalized[field_name].strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        if normalized["category"] not in VALID_CATEGORIES:
            raise ValueError(f"Invalid lexical category: {normalized['category']}.")
        if normalized["gender"] not in VALID_GENDERS:
            raise ValueError(f"Invalid gender: {normalized['gender']}.")
        if normalized["status"] not in VALID_STATUSES:
            raise ValueError(f"Invalid lexical status: {normalized['status']}.")

        source = normalized.get("source")
        if not isinstance(source, dict):
            raise ValueError("Lexical entry source provenance is required.")
        missing_source_fields = sorted(SOURCE_REQUIRED_FIELDS - set(source.keys()))
        if missing_source_fields:
            raise ValueError(f"Lexical entry source missing required fields: {', '.join(missing_source_fields)}.")
        for field_name in ("name", "type", "citation", "license"):
            if not isinstance(source.get(field_name), str) or not source[field_name].strip():
                raise ValueError(f"source.{field_name} must be a non-empty string.")
        if source["type"] not in VALID_SOURCE_TYPES:
            raise ValueError(f"Invalid source type: {source['type']}.")
        if not isinstance(source.get("verified"), bool):
            raise ValueError("source.verified must be a boolean.")

        normalization = normalized.get("normalization")
        if not isinstance(normalization, dict):
            raise ValueError("Lexical entry normalization metadata is required.")
        missing_normalization_fields = sorted(NORMALIZATION_REQUIRED_FIELDS - set(normalization.keys()))
        if missing_normalization_fields:
            raise ValueError(
                f"Lexical entry normalization missing required fields: {', '.join(missing_normalization_fields)}."
            )
        if normalization.get("unicode") != "NFC":
            raise ValueError("normalization.unicode must be NFC.")
        if normalization.get("script_policy") != "devanagari_primary":
            raise ValueError("normalization.script_policy must be devanagari_primary.")

        return normalized

    def load_sample_entries(self) -> List[Dict[str, Any]]:
        with SAMPLE_ENTRIES_PATH.open("r", encoding="utf-8") as handle:
            entries = json.load(handle)
        if not isinstance(entries, list):
            raise ValueError("Sample lexical registry must be a list.")
        return entries

    def validate_registry(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(entries, list):
            raise ValueError("Lexical registry must be a list.")

        seen_ids = set()
        normalized_entries = []
        for entry in entries:
            normalized = self.validate_entry(entry)
            lexical_id = normalized["lexical_id"]
            if lexical_id in seen_ids:
                raise ValueError(f"Duplicate lexical_id: {lexical_id}.")
            seen_ids.add(lexical_id)
            normalized_entries.append(normalized)
        return normalized_entries
