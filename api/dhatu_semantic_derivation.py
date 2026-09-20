from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL_REGISTRY_PATH = ROOT / "data" / "sanskrit" / "dhatus" / "index.json"
DEFAULT_DERIVATION_ROOT = ROOT / "data" / "sanskrit" / "dhatus" / "semantic" / "derivations"
DEFAULT_DERIVATION_PATH = DEFAULT_DERIVATION_ROOT / "semantic_derivations.v1.json"
PLACEHOLDER_REVIEW_STATUS = "placeholder-local-review-required"
UNREVIEWED_CONFIDENCE = "unreviewed"
PLACEHOLDER_SOURCES = {"placeholder-local-model", "placeholder-local-review-required"}
FORBIDDEN_SUTRA_KEYS = {
    "exactSutraId",
    "exactSutraIds",
    "paniniSutra",
    "paniniSutraId",
    "sutra",
    "sutraId",
    "sutraIds",
    "sutraNumber",
}
EXACT_SUTRA_PATTERN = re.compile(r"\b\d+\.\d+\.\d+(?:\.\d+)?\b")


def resolve_path(path: Any) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def load_json(path: Any) -> Dict[str, Any]:
    with resolve_path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Semantic derivation source must be a JSON object: {path}")
    return payload


def file_sha256(path: Any) -> str:
    return hashlib.sha256(resolve_path(path).read_bytes()).hexdigest()


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    return "".join(char for char in text if not unicodedata.combining(char))


def duplicate_values(values: List[str]) -> List[str]:
    seen: Set[str] = set()
    duplicates: Set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def load_derivation_context(
    derivation_path: Any = DEFAULT_DERIVATION_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
) -> Dict[str, Any]:
    return {
        "derivations": load_json(derivation_path),
        "canonicalRegistry": load_json(canonical_registry_path),
    }


def _records(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise ValueError("Semantic derivation records must be a list.")
    return [record for record in records if isinstance(record, dict)]


def _relations(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        relation
        for record in records
        for relation in record.get("protoDerivationRelations", [])
        if isinstance(relation, dict)
    ]


def _contains_forbidden_sutra_claim(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "schemaVersion":
                continue
            if key in FORBIDDEN_SUTRA_KEYS:
                return True
            if _contains_forbidden_sutra_claim(child):
                return True
        return False
    if isinstance(value, list):
        return any(_contains_forbidden_sutra_claim(child) for child in value)
    if isinstance(value, str):
        return bool(EXACT_SUTRA_PATTERN.search(value))
    return False


def _collect_non_placeholder_sources(value: Any) -> List[str]:
    sources: List[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"source", "evidenceSource", "sourceType"} and child not in PLACEHOLDER_SOURCES:
                sources.append(str(child))
            sources.extend(_collect_non_placeholder_sources(child))
    elif isinstance(value, list):
        for child in value:
            sources.extend(_collect_non_placeholder_sources(child))
    return sources


def _collect_invalid_confidence_values(value: Any) -> List[str]:
    values: List[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "confidence" and child != UNREVIEWED_CONFIDENCE:
                values.append(str(child))
            values.extend(_collect_invalid_confidence_values(child))
    elif isinstance(value, list):
        for child in value:
            values.extend(_collect_invalid_confidence_values(child))
    return values


def query_derivations(
    dhatu_id: Optional[str] = None,
    family: Optional[str] = None,
    domain: Optional[str] = None,
    relation: Optional[str] = None,
    derivation_path: Any = DEFAULT_DERIVATION_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
) -> List[Dict[str, Any]]:
    context = load_derivation_context(derivation_path, canonical_registry_path)
    canonical_ids = set(context["canonicalRegistry"].get("records", {}).keys())
    query_family = normalize_text(family)
    query_domain = normalize_text(domain)
    query_relation = normalize_text(relation)
    results: List[Dict[str, Any]] = []

    for record in _records(context["derivations"]):
        record_id = record.get("dhatuId")
        if record_id not in canonical_ids:
            continue
        if dhatu_id and record_id != dhatu_id:
            continue
        if family and query_family not in normalize_text(record.get("derivationFamilyId")):
            continue
        if domain and not any(query_domain == normalize_text(item) for item in record.get("usageDomains", [])):
            continue
        if relation and not any(
            query_relation == normalize_text(item.get("relationType"))
            for item in record.get("protoDerivationRelations", [])
            if isinstance(item, dict)
        ):
            continue
        results.append(json.loads(json.dumps(record)))

    return sorted(results, key=lambda item: (item.get("derivationFamilyId", ""), item.get("dhatuId", "")))


def query_payload(**kwargs: Any) -> Dict[str, Any]:
    results = query_derivations(**kwargs)
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "api/dhatu_semantic_derivation.py",
        "query": {
            "dhatuId": kwargs.get("dhatu_id"),
            "family": kwargs.get("family"),
            "domain": kwargs.get("domain"),
            "relation": kwargs.get("relation"),
        },
        "resultCount": len(results),
        "results": results,
        "safetyPolicy": {
            "authoritativePaninianClaims": False,
            "exactSutraAssertions": False,
            "grammaticalCorrectnessGuarantee": False,
            "requiredReviewStatus": PLACEHOLDER_REVIEW_STATUS,
            "requiredConfidence": UNREVIEWED_CONFIDENCE,
        },
    }


def validate_derivations(
    derivation_path: Any = DEFAULT_DERIVATION_PATH,
    canonical_registry_path: Any = DEFAULT_CANONICAL_REGISTRY_PATH,
) -> Dict[str, Any]:
    registry_before = file_sha256(canonical_registry_path)
    context = load_derivation_context(derivation_path, canonical_registry_path)
    registry_after = file_sha256(canonical_registry_path)
    registry = context["canonicalRegistry"]
    payload = context["derivations"]
    records = _records(payload)
    relations = _relations(records)
    canonical_ids = set(registry.get("records", {}).keys())
    derivation_ids = [str(record.get("derivationId", "")) for record in records]
    duplicate_derivation_ids = duplicate_values(derivation_ids)
    derivation_id_set = set(derivation_ids)
    noncanonical_dhatu_ids = sorted(
        str(record.get("dhatuId"))
        for record in records
        if record.get("dhatuId") not in canonical_ids
    )
    unresolved_relation_references = [
        {
            "relationId": relation.get("relationId"),
            "sourceDerivationId": relation.get("sourceDerivationId"),
            "targetDerivationId": relation.get("targetDerivationId"),
        }
        for relation in relations
        if relation.get("sourceDerivationId") not in derivation_id_set
        or relation.get("targetDerivationId") not in derivation_id_set
    ]
    invalid_confidence_values = sorted(set(_collect_invalid_confidence_values(payload)))
    non_placeholder_sources = sorted(set(_collect_non_placeholder_sources(payload)))
    non_placeholder_review_records = sorted(
        str(record.get("derivationId"))
        for record in records
        if record.get("reviewStatus") != PLACEHOLDER_REVIEW_STATUS
        or record.get("placeholderPaniniRelation", {}).get("reviewStatus") != PLACEHOLDER_REVIEW_STATUS
    )
    exact_sutra_assertions_present = _contains_forbidden_sutra_claim(payload)
    policy = payload.get("policy", {})
    checks = {
        "derivationDirectoryPresent": resolve_path(derivation_path).parent.exists(),
        "derivationIdsUnique": duplicate_derivation_ids == [],
        "canonicalDhatuIdsExist": noncanonical_dhatu_ids == [],
        "relationReferencesResolve": unresolved_relation_references == [],
        "confidenceValuesRemainUnreviewed": invalid_confidence_values == [],
        "placeholderSourcesOnly": non_placeholder_sources == [],
        "reviewStatusPlaceholderOnly": non_placeholder_review_records == [],
        "noExactSutraAssertions": not exact_sutra_assertions_present,
        "noAuthoritativePaninianClaims": policy.get("authoritativePaninianClaims") is False,
        "noGrammaticalCorrectnessGuarantee": policy.get("grammaticalCorrectnessGuarantee") is False,
        "canonicalRegistryUnchanged": registry_before == registry_after,
        "canonicalRegistryRecordCountIs13": len(canonical_ids) == 13,
    }
    return {
        "schemaVersion": "1.0.0",
        "generatedBy": "api/dhatu_semantic_derivation.py",
        "derivationValidationStatus": "PASS" if all(checks.values()) else "FAIL",
        "derivationRecordCount": len(records),
        "relationCount": len(relations),
        "canonicalRegistryRecordCount": len(canonical_ids),
        "duplicateDerivationIds": duplicate_derivation_ids,
        "noncanonicalDhatuIds": noncanonical_dhatu_ids,
        "unresolvedRelationReferences": unresolved_relation_references,
        "invalidConfidenceValues": invalid_confidence_values,
        "nonPlaceholderSources": non_placeholder_sources,
        "nonPlaceholderReviewRecords": non_placeholder_review_records,
        "exactSutraAssertionsPresent": exact_sutra_assertions_present,
        "checks": checks,
    }
