from pathlib import Path
from typing import Any, Dict, List, Optional
import copy
import json
import re


FORBIDDEN_SEMANTIC_KEYS = {
    "bija",
    "chakra",
    "mantra",
    "deity",
    "sonicProfile",
    "vector49d",
    "mandala",
}
REQUIRED_SEMANTIC_FIELDS = {
    "root",
    "semanticDomains",
    "transitivitySemantics",
    "actionType",
    "coreGlosses",
    "semanticNotes",
}
DOMAIN_RE = re.compile(r"^[a-z]+(?:-[a-z]+)*$")


def load_semantic_overlay(path: Any) -> Dict[str, Any]:
    overlay_path = Path(path)
    with overlay_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Semantic overlay must be a JSON object.")
    return copy.deepcopy(payload)


def validate_semantic_overlay(
    payload: Dict[str, Any],
    goldset_ids: List[str],
    allow_extra: bool = False,
) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Semantic overlay must be a dict.")
    if not payload.get("goldsetVersion"):
        raise ValueError("goldsetVersion is required.")
    if not payload.get("semanticVersion"):
        raise ValueError("semanticVersion is required.")

    records = payload.get("records")
    if not isinstance(records, dict):
        raise ValueError("records must be a dict.")

    expected_ids = set(goldset_ids)
    record_ids = set(records.keys())
    missing = sorted(expected_ids - record_ids)
    if missing:
        raise ValueError(f"Semantic overlay missing goldset ids: {', '.join(missing)}.")
    extra = sorted(record_ids - expected_ids)
    if extra and not allow_extra:
        raise ValueError(f"Semantic overlay contains ids outside goldset: {', '.join(extra)}.")

    for dhatu_id, record in records.items():
        _validate_semantic_record(dhatu_id, record)

    return copy.deepcopy(payload)


def get_semantics_for_dhatu(payload: Dict[str, Any], dhatu_id: str) -> Optional[Dict[str, Any]]:
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, dict) or dhatu_id not in records:
        return None
    return copy.deepcopy(records[dhatu_id])


def find_dhatus_by_semantic_domain(payload: Dict[str, Any], domain: str) -> List[str]:
    index = build_semantic_domain_index(payload)
    return copy.deepcopy(index.get(domain, []))


def list_semantic_domains(payload: Dict[str, Any]) -> List[str]:
    return sorted(build_semantic_domain_index(payload).keys())


def build_semantic_domain_index(payload: Dict[str, Any]) -> Dict[str, List[str]]:
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, dict):
        return {}

    index: Dict[str, List[str]] = {}
    for dhatu_id, record in records.items():
        domains = record.get("semanticDomains", []) if isinstance(record, dict) else []
        if not isinstance(domains, list):
            continue
        for domain in domains:
            if isinstance(domain, str):
                index.setdefault(domain, []).append(dhatu_id)
    return {domain: sorted(ids) for domain, ids in sorted(index.items())}


def _validate_semantic_record(dhatu_id: str, record: Any) -> None:
    if not isinstance(record, dict):
        raise ValueError(f"Semantic overlay record must be a dict: {dhatu_id}.")
    forbidden = sorted(_find_forbidden_keys(record))
    if forbidden:
        raise ValueError(f"Forbidden semantic overlay keys in {dhatu_id}: {', '.join(forbidden)}.")

    missing = sorted(REQUIRED_SEMANTIC_FIELDS - set(record.keys()))
    if missing:
        raise ValueError(f"Semantic overlay record {dhatu_id} missing fields: {', '.join(missing)}.")

    if not isinstance(record["root"], str) or not record["root"]:
        raise ValueError(f"Semantic overlay record {dhatu_id} root must be a non-empty string.")
    for field_name in ("transitivitySemantics", "actionType"):
        if not isinstance(record[field_name], str) or not record[field_name]:
            raise ValueError(f"Semantic overlay record {dhatu_id} {field_name} must be a non-empty string.")

    semantic_domains = record["semanticDomains"]
    if not isinstance(semantic_domains, list) or not semantic_domains:
        raise ValueError(f"Semantic overlay record {dhatu_id} semanticDomains must be a non-empty list.")
    for domain in semantic_domains:
        if not isinstance(domain, str) or not DOMAIN_RE.match(domain):
            raise ValueError(f"Invalid semantic domain for {dhatu_id}: {domain}.")

    for field_name in ("coreGlosses", "semanticNotes"):
        if not isinstance(record[field_name], list):
            raise ValueError(f"Semantic overlay record {dhatu_id} {field_name} must be a list.")
        for item in record[field_name]:
            if not isinstance(item, str):
                raise ValueError(f"Semantic overlay record {dhatu_id} {field_name} values must be strings.")


def _find_forbidden_keys(value: Any) -> List[str]:
    found: List[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_SEMANTIC_KEYS:
                found.append(key)
            found.extend(_find_forbidden_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_find_forbidden_keys(child))
    return found
