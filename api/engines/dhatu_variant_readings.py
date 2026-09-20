from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RECENSIONS_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "recensions.v1.json"
DHATU_ROOT = ROOT / "data" / "sanskrit" / "dhatus"
READING_ID_RE = re.compile(r"^VR_[A-Z0-9_]+$")
ALLOWED_READING_TYPES = {
    "canonical",
    "variant",
    "alternate-meaning",
    "alternate-upadesha",
    "alternate-gana",
    "alternate-order",
}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_PREFERENCE_STATUSES = {"accepted", "disputed", "deferred", "rejected"}
ALLOWED_UNRESOLVED_STATUSES = {"deferred", "rejected", "needs-review"}
NETWORK_PREFIXES = ("http://", "https://")


def load_recensions(path: Any = DEFAULT_RECENSIONS_PATH) -> Dict[str, Any]:
    recension_path = Path(path)
    with recension_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return validate_recensions(payload)


def validate_recensions(
    payload: Dict[str, Any],
    source_attribution: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Recensions payload must be a JSON object.")
    for field in ("recensionVersion", "recensions", "variantReadings", "unresolvedReadings"):
        if field not in payload:
            raise ValueError(f"Recensions payload missing field: {field}.")

    recensions = _require_dict(payload["recensions"], "recensions")
    variant_readings = _require_dict(payload["variantReadings"], "variantReadings")
    unresolved_readings = _require_dict(payload["unresolvedReadings"], "unresolvedReadings")

    source_entities = _source_entities(source_attribution)
    for recension_id, recension in recensions.items():
        _validate_recension(recension_id, recension, source_entities)
    for dhatu_id, entry in variant_readings.items():
        _validate_variant_entry(dhatu_id, entry, recensions, source_entities)
    for unresolved_id, entry in unresolved_readings.items():
        _validate_unresolved_entry(unresolved_id, entry, source_entities)

    assert_no_network_sources(payload)
    _validate_canonical_seed_against_registry(variant_readings)
    _validate_unresolved_controlled_batch(unresolved_readings)
    return copy.deepcopy(payload)


def get_variant_readings(payload: Dict[str, Any], dhatu_id: str) -> List[Dict[str, Any]]:
    entry = payload.get("variantReadings", {}).get(dhatu_id)
    if not entry:
        return []
    return copy.deepcopy(entry.get("readings", []))


def get_preferred_reading(payload: Dict[str, Any], dhatu_id: str) -> Dict[str, Any] | None:
    entry = payload.get("variantReadings", {}).get(dhatu_id)
    if not entry:
        return None
    preferred_id = entry.get("canonicalPreference", {}).get("preferredReadingId")
    for reading in entry.get("readings", []):
        if reading.get("readingId") == preferred_id:
            return copy.deepcopy(reading)
    return None


def list_variants_by_field(payload: Dict[str, Any], field: str) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for dhatu_id, entry in sorted(payload.get("variantReadings", {}).items()):
        for reading in entry.get("readings", []):
            if reading.get("field") == field:
                item = copy.deepcopy(reading)
                item["canonicalDhatuId"] = dhatu_id
                matches.append(item)
    return matches


def list_variants_by_recension(payload: Dict[str, Any], recension: str) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for dhatu_id, entry in sorted(payload.get("variantReadings", {}).items()):
        for reading in entry.get("readings", []):
            if reading.get("recension") == recension:
                item = copy.deepcopy(reading)
                item["canonicalDhatuId"] = dhatu_id
                matches.append(item)
    return matches


def list_unresolved_readings(payload: Dict[str, Any], status: str | None = None) -> List[Dict[str, Any]]:
    if status is not None and status not in ALLOWED_UNRESOLVED_STATUSES:
        raise ValueError(f"Invalid unresolved status: {status}.")
    matches: List[Dict[str, Any]] = []
    for unresolved_id, entry in sorted(payload.get("unresolvedReadings", {}).items()):
        if status is None or entry.get("status") == status:
            item = copy.deepcopy(entry)
            item["unresolvedId"] = unresolved_id
            matches.append(item)
    return matches


def summarize_recensions(payload: Dict[str, Any]) -> Dict[str, int]:
    readings = [
        reading
        for entry in payload.get("variantReadings", {}).values()
        for reading in entry.get("readings", [])
    ]
    canonical_readings = [reading for reading in readings if reading.get("readingType") == "canonical"]
    return {
        "recensionCount": len(payload.get("recensions", {})),
        "variantEntryCount": len(payload.get("variantReadings", {})),
        "readingCount": len(readings),
        "canonicalReadingCount": len(canonical_readings),
        "unresolvedReadingCount": len(payload.get("unresolvedReadings", {})),
        "deferredUnresolvedCount": len(list_unresolved_readings(payload, "deferred")),
    }


def assert_no_network_sources(payload: Dict[str, Any]) -> bool:
    source_values: List[str] = []
    for recension in payload.get("recensions", {}).values():
        source_values.append(recension.get("sourceEntity", ""))
    for entry in payload.get("variantReadings", {}).values():
        for reading in entry.get("readings", []):
            source_values.extend(reading.get("sourceEntities", []))
    for entry in payload.get("unresolvedReadings", {}).values():
        source_values.extend(entry.get("sourceEntities", []))

    for source in source_values:
        if isinstance(source, str) and source.startswith(NETWORK_PREFIXES):
            raise ValueError(f"Network source is not allowed in recensions: {source}.")
    return True


def compare_variant_to_canonical(record: Dict[str, Any], variant_entry: Dict[str, Any]) -> Dict[str, Any]:
    identity = record.get("identity", {}) if isinstance(record, dict) else {}
    canonical_root = variant_entry.get("canonicalRoot")
    canonical_upadesha = variant_entry.get("canonicalUpadesha")
    root_matches = _unknown_or_empty(identity.get("root")) or identity.get("root") == canonical_root
    upadesha_matches = (
        _unknown_or_empty(identity.get("upadesha"))
        or canonical_upadesha is None
        or identity.get("upadesha") == canonical_upadesha
    )
    return {
        "dhatuId": record.get("id"),
        "rootMatches": root_matches,
        "upadeshaMatches": upadesha_matches,
        "matches": root_matches and upadesha_matches,
    }


def build_variant_index(payload: Dict[str, Any]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    index: Dict[str, Dict[str, List[Dict[str, Any]]]] = {"byField": {}, "byRecension": {}}
    for dhatu_id, entry in sorted(payload.get("variantReadings", {}).items()):
        for reading in entry.get("readings", []):
            item = copy.deepcopy(reading)
            item["canonicalDhatuId"] = dhatu_id
            index["byField"].setdefault(reading["field"], []).append(copy.deepcopy(item))
            index["byRecension"].setdefault(reading["recension"], []).append(copy.deepcopy(item))
    return index


def _validate_recension(
    recension_id: str,
    recension: Dict[str, Any],
    source_entities: set[str] | None,
) -> None:
    for field in ("label", "sourceType", "description"):
        if field not in recension:
            raise ValueError(f"Recension {recension_id} missing field: {field}.")
    source_entity = recension.get("sourceEntity")
    if source_entity:
        _validate_source_entity(source_entity, source_entities, f"Recension {recension_id}")


def _validate_variant_entry(
    dhatu_id: str,
    entry: Dict[str, Any],
    recensions: Dict[str, Any],
    source_entities: set[str] | None,
) -> None:
    for field in ("canonicalDhatuId", "canonicalRoot", "readings", "canonicalPreference"):
        if field not in entry:
            raise ValueError(f"Variant entry {dhatu_id} missing field: {field}.")
    if entry["canonicalDhatuId"] != dhatu_id:
        raise ValueError(f"Variant entry key mismatch for {dhatu_id}.")

    readings = entry["readings"]
    if not isinstance(readings, list) or not readings:
        raise ValueError(f"Variant entry {dhatu_id} must include readings.")
    reading_ids = set()
    for reading in readings:
        _validate_reading(dhatu_id, reading, recensions, source_entities)
        reading_ids.add(reading["readingId"])

    preference = _require_dict(entry["canonicalPreference"], f"{dhatu_id}.canonicalPreference")
    for field in ("preferredReadingId", "status", "rationale"):
        if field not in preference:
            raise ValueError(f"Canonical preference {dhatu_id} missing field: {field}.")
    if preference["preferredReadingId"] not in reading_ids:
        raise ValueError(f"Preferred reading does not resolve for {dhatu_id}.")
    if preference["status"] not in ALLOWED_PREFERENCE_STATUSES:
        raise ValueError(f"Invalid canonical preference status for {dhatu_id}.")


def _validate_reading(
    dhatu_id: str,
    reading: Dict[str, Any],
    recensions: Dict[str, Any],
    source_entities: set[str] | None,
) -> None:
    for field in ("readingId", "recension", "field", "value", "readingType", "confidence", "sourceEntities", "notes"):
        if field not in reading:
            raise ValueError(f"Reading for {dhatu_id} missing field: {field}.")
    if not READING_ID_RE.match(reading["readingId"]):
        raise ValueError(f"Invalid readingId for {dhatu_id}: {reading['readingId']}.")
    if reading["recension"] not in recensions:
        raise ValueError(f"Reading {reading['readingId']} references unknown recension.")
    if reading["readingType"] not in ALLOWED_READING_TYPES:
        raise ValueError(f"Invalid readingType for {reading['readingId']}.")
    if reading["confidence"] not in ALLOWED_CONFIDENCE:
        raise ValueError(f"Invalid confidence for {reading['readingId']}.")
    if not isinstance(reading["sourceEntities"], list):
        raise ValueError(f"Reading {reading['readingId']} sourceEntities must be a list.")
    if not isinstance(reading["notes"], list):
        raise ValueError(f"Reading {reading['readingId']} notes must be a list.")
    for entity_id in reading["sourceEntities"]:
        _validate_source_entity(entity_id, source_entities, f"Reading {reading['readingId']}")


def _validate_unresolved_entry(
    unresolved_id: str,
    entry: Dict[str, Any],
    source_entities: set[str] | None,
) -> None:
    for field in ("candidateRoot", "candidateCanonicalForm", "candidateGanaId", "status", "reason", "sourceEntities"):
        if field not in entry:
            raise ValueError(f"Unresolved reading {unresolved_id} missing field: {field}.")
    if entry["status"] not in ALLOWED_UNRESOLVED_STATUSES:
        raise ValueError(f"Invalid unresolved status for {unresolved_id}.")
    for entity_id in entry["sourceEntities"]:
        _validate_source_entity(entity_id, source_entities, f"Unresolved reading {unresolved_id}")


def _validate_source_entity(entity_id: str, source_entities: set[str] | None, context: str) -> None:
    if isinstance(entity_id, str) and entity_id.startswith(NETWORK_PREFIXES):
        raise ValueError(f"{context} introduces a network source: {entity_id}.")
    if source_entities is not None and entity_id not in source_entities:
        raise ValueError(f"{context} references unknown source entity: {entity_id}.")


def _source_entities(source_attribution: Dict[str, Any] | None) -> set[str] | None:
    if source_attribution is None:
        return None
    entities = _require_dict(source_attribution.get("entities"), "source_attribution.entities")
    return set(entities.keys())


def _validate_canonical_seed_against_registry(variant_readings: Dict[str, Any]) -> None:
    canonical_records = _load_registry_records()
    for dhatu_id, entry in variant_readings.items():
        record = canonical_records.get(dhatu_id)
        if not record:
            continue
        comparison = compare_variant_to_canonical(record, entry)
        if not comparison["matches"]:
            raise ValueError(f"Canonical seed reading does not match registry where possible: {dhatu_id}.")


def _validate_unresolved_controlled_batch(unresolved_readings: Dict[str, Any]) -> None:
    for unresolved_id, entry in unresolved_readings.items():
        source_entities = entry.get("sourceEntities", [])
        if "raw/dhatupatha_controlled_batch_01.csv" in source_entities and entry.get("status") != "deferred":
            raise ValueError(f"Controlled batch reading must remain deferred: {unresolved_id}.")


def _load_registry_records() -> Dict[str, Dict[str, Any]]:
    records: Dict[str, Dict[str, Any]] = {}
    if not DHATU_ROOT.exists():
        return records
    for path in sorted(DHATU_ROOT.glob("*.json")):
        if path.name == "index.json":
            continue
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        for record in payload.get("records", []):
            records[record.get("id")] = record
    return records


def _unknown_or_empty(value: Any) -> bool:
    return not isinstance(value, str) or not value or set(value) == {"?"}


def _require_dict(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return value
