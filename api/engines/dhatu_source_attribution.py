from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ATTRIBUTION_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "source_attribution.v1.json"
VALID_REVIEW_STATUSES = {"approved", "deferred", "rejected"}
VALID_SOURCE_CONFIDENCE = {"high", "medium", "low"}


def load_source_attribution(path: Any = DEFAULT_ATTRIBUTION_PATH) -> Dict[str, Any]:
    attribution_path = Path(path)
    with attribution_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return validate_source_attribution(payload)


def validate_source_attribution(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Source attribution payload must be a JSON object.")
    for field in ("attributionVersion", "entities", "agents", "activities", "recordAttributions"):
        if field not in payload:
            raise ValueError(f"Source attribution missing field: {field}.")

    entities = _require_dict(payload["entities"], "entities")
    agents = _require_dict(payload["agents"], "agents")
    activities = _require_dict(payload["activities"], "activities")
    attributions = _require_dict(payload["recordAttributions"], "recordAttributions")

    for entity_id, entity in entities.items():
        _validate_entity(entity_id, entity)
    for agent_id, agent in agents.items():
        _validate_agent(agent_id, agent)
    for activity_id, activity in activities.items():
        _validate_activity(activity_id, activity, entities, agents)
    for dhatu_id, attribution in attributions.items():
        _validate_record_attribution(dhatu_id, attribution, entities, agents, activities)
    assert_no_network_derived_sources(payload)
    return payload


def get_record_attribution(payload: Dict[str, Any], dhatu_id: str) -> Dict[str, Any] | None:
    return payload.get("recordAttributions", {}).get(dhatu_id)


def list_records_by_review_status(payload: Dict[str, Any], status: str) -> List[str]:
    if status not in VALID_REVIEW_STATUSES:
        raise ValueError(f"Invalid reviewStatus: {status}.")
    return _sorted_records_matching(payload, "reviewStatus", status)


def list_records_by_source_confidence(payload: Dict[str, Any], confidence: str) -> List[str]:
    if confidence not in VALID_SOURCE_CONFIDENCE:
        raise ValueError(f"Invalid sourceConfidence: {confidence}.")
    return _sorted_records_matching(payload, "sourceConfidence", confidence)


def list_records_by_source_entity(payload: Dict[str, Any], source_entity: str) -> List[str]:
    return [
        dhatu_id
        for dhatu_id, attribution in sorted(payload.get("recordAttributions", {}).items())
        if source_entity in attribution.get("sourceEntities", [])
    ]


def summarize_attribution(payload: Dict[str, Any]) -> Dict[str, int]:
    attributions = payload.get("recordAttributions", {})
    return {
        "entityCount": len(payload.get("entities", {})),
        "agentCount": len(payload.get("agents", {})),
        "activityCount": len(payload.get("activities", {})),
        "recordCount": len(attributions),
        "approved": len(list_records_by_review_status(payload, "approved")),
        "deferred": len(list_records_by_review_status(payload, "deferred")),
        "rejected": len(list_records_by_review_status(payload, "rejected")),
    }


def assert_no_network_derived_sources(payload: Dict[str, Any]) -> bool:
    for entity_id, entity in payload.get("entities", {}).items():
        if entity.get("networkDerived") is not False:
            raise ValueError(f"Entity must not be network-derived: {entity_id}.")
    return True


def validate_record_against_promotion(
    attribution: Dict[str, Any],
    promotion_payload: Dict[str, Any],
) -> Dict[str, Any]:
    promotion_records = {
        record["id"]: record
        for record in promotion_payload.get("records", [])
    }
    errors = []
    for dhatu_id, record_attribution in attribution.get("recordAttributions", {}).items():
        promotion_record = promotion_records.get(dhatu_id)
        if not promotion_record:
            continue
        if record_attribution.get("reviewStatus") != promotion_record.get("status"):
            errors.append(f"{dhatu_id}: reviewStatus does not match promotion status.")
        if record_attribution.get("sourceConfidence") != promotion_record.get("sourceConfidence"):
            errors.append(f"{dhatu_id}: sourceConfidence does not match promotion record.")
    return {"valid": not errors, "errors": errors}


def _validate_entity(entity_id: str, entity: Dict[str, Any]) -> None:
    for field in ("entityType", "sourceMode", "networkDerived"):
        if field not in entity:
            raise ValueError(f"Entity {entity_id} missing field: {field}.")
    if entity["networkDerived"] is not False:
        raise ValueError(f"Entity {entity_id} must set networkDerived to false.")


def _validate_agent(agent_id: str, agent: Dict[str, Any]) -> None:
    for field in ("agentType", "name", "role"):
        if field not in agent:
            raise ValueError(f"Agent {agent_id} missing field: {field}.")


def _validate_activity(
    activity_id: str,
    activity: Dict[str, Any],
    entities: Dict[str, Any],
    agents: Dict[str, Any],
) -> None:
    for field in ("activityType", "usedEntities", "associatedAgents", "result"):
        if field not in activity:
            raise ValueError(f"Activity {activity_id} missing field: {field}.")
    for entity_id in activity["usedEntities"]:
        if entity_id not in entities:
            raise ValueError(f"Activity {activity_id} references unknown entity: {entity_id}.")
    for agent_id in activity["associatedAgents"]:
        if agent_id not in agents:
            raise ValueError(f"Activity {activity_id} references unknown agent: {agent_id}.")


def _validate_record_attribution(
    dhatu_id: str,
    attribution: Dict[str, Any],
    entities: Dict[str, Any],
    agents: Dict[str, Any],
    activities: Dict[str, Any],
) -> None:
    for field in (
        "sourceEntities",
        "reviewStatus",
        "sourceConfidence",
        "reviewAgents",
        "validationActivities",
        "canonicalizationRationale",
    ):
        if field not in attribution:
            raise ValueError(f"Record attribution {dhatu_id} missing field: {field}.")
    if attribution["reviewStatus"] not in VALID_REVIEW_STATUSES:
        raise ValueError(f"Record attribution {dhatu_id} has invalid reviewStatus.")
    if attribution["sourceConfidence"] not in VALID_SOURCE_CONFIDENCE:
        raise ValueError(f"Record attribution {dhatu_id} has invalid sourceConfidence.")
    for entity_id in attribution["sourceEntities"]:
        if entity_id not in entities:
            raise ValueError(f"Record attribution {dhatu_id} references unknown entity: {entity_id}.")
    for agent_id in attribution["reviewAgents"]:
        if agent_id not in agents:
            raise ValueError(f"Record attribution {dhatu_id} references unknown agent: {agent_id}.")
    for activity_id in attribution["validationActivities"]:
        if activity_id not in activities:
            raise ValueError(f"Record attribution {dhatu_id} references unknown activity: {activity_id}.")


def _require_dict(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return value


def _sorted_records_matching(payload: Dict[str, Any], field: str, value: str) -> List[str]:
    return [
        dhatu_id
        for dhatu_id, attribution in sorted(payload.get("recordAttributions", {}).items())
        if attribution.get(field) == value
    ]
