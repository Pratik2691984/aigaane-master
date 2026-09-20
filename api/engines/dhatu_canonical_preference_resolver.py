from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PREFERENCES_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "canonical_preferences.v1.json"
ALLOWED_PREFERENCE_STATUSES = {"canonical", "deferred", "rejected", "disputed", "needs-review"}
ALLOWED_RECOMMENDED_ACTIONS = {
    "keep-canonical",
    "promote-to-canonical",
    "reject-candidate",
    "defer",
    "manual-review-required",
    "no-action",
}


def load_canonical_preferences(path: Any = DEFAULT_PREFERENCES_PATH) -> Dict[str, Any]:
    preference_path = Path(path)
    with preference_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return validate_canonical_preferences(payload)


def validate_canonical_preferences(
    payload: Dict[str, Any],
    editorial_payload: Dict[str, Any] | None = None,
    recension_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Canonical preferences payload must be a JSON object.")
    for field in ("preferenceVersion", "policy", "preferences", "candidatePreferences"):
        if field not in payload:
            raise ValueError(f"Canonical preferences payload missing field: {field}.")

    policy = _require_dict(payload["policy"], "policy")
    if policy.get("autoPromote") is not False:
        raise ValueError("policy.autoPromote must be false.")
    if policy.get("mutationTarget") != "none":
        raise ValueError('policy.mutationTarget must be "none".')
    if policy.get("requiresHumanReview") is not True:
        raise ValueError("policy.requiresHumanReview must be true.")

    preferences = _require_dict(payload["preferences"], "preferences")
    candidate_preferences = _require_dict(payload["candidatePreferences"], "candidatePreferences")

    for dhatu_id, preference in preferences.items():
        _validate_preference(dhatu_id, preference, editorial_payload, recension_payload)
    for candidate_id, preference in candidate_preferences.items():
        _validate_candidate_preference(candidate_id, preference, editorial_payload)

    assert_no_auto_promotion(payload)
    assert_no_canonical_mutation(payload)
    return copy.deepcopy(payload)


def resolve_preference_for_dhatu(
    dhatu_id: str,
    editorial_payload: Dict[str, Any],
    recension_payload: Dict[str, Any],
    attribution_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any] | None:
    decision = editorial_payload.get("decisions", {}).get(dhatu_id)
    if not decision:
        return None
    if not _decision_matches_recension(decision, recension_payload):
        return {
            "dhatuId": dhatu_id,
            "preferredReadingId": decision.get("preferredReadingId"),
            "decisionId": decision.get("decisionId"),
            "preferenceStatus": "needs-review",
            "confidence": "low",
            "recommendedAction": "manual-review-required",
            "rationale": "Editorial decision does not match recension preference",
        }

    confidence = _confidence_for_decision(decision, dhatu_id, attribution_payload)
    status = _preference_status_for_decision(decision)
    return {
        "dhatuId": dhatu_id,
        "preferredReadingId": decision.get("preferredReadingId"),
        "decisionId": decision.get("decisionId"),
        "preferenceStatus": status,
        "confidence": confidence,
        "recommendedAction": decision.get("recommendedAction", "no-action"),
        "rationale": _rationale_for_decision(decision, status),
    }


def resolve_candidate_preference(
    candidate_id: str,
    editorial_payload: Dict[str, Any],
    recension_payload: Dict[str, Any],
    attribution_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any] | None:
    recommendation = editorial_payload.get("recommendations", {}).get(candidate_id)
    unresolved = recension_payload.get("unresolvedReadings", {}).get(candidate_id, {})
    if not recommendation and not unresolved:
        return None

    status = _candidate_status(recommendation, unresolved)
    return {
        "candidateId": candidate_id,
        "preferenceStatus": status,
        "confidence": _candidate_confidence(candidate_id, attribution_payload),
        "recommendedAction": (recommendation or {}).get("recommendedAction", "manual-review-required"),
        "rationale": (recommendation or unresolved).get("reason", "Candidate requires manual review"),
    }


def list_preferences_by_status(payload: Dict[str, Any], status: str) -> List[Dict[str, Any]]:
    if status not in ALLOWED_PREFERENCE_STATUSES:
        raise ValueError(f"Invalid preferenceStatus: {status}.")
    return [
        copy.deepcopy(preference)
        for _, preference in sorted(payload.get("preferences", {}).items())
        if preference.get("preferenceStatus") == status
    ]


def list_candidate_preferences_by_status(payload: Dict[str, Any], status: str) -> List[Dict[str, Any]]:
    if status not in ALLOWED_PREFERENCE_STATUSES:
        raise ValueError(f"Invalid preferenceStatus: {status}.")
    return [
        copy.deepcopy(preference)
        for _, preference in sorted(payload.get("candidatePreferences", {}).items())
        if preference.get("preferenceStatus") == status
    ]


def build_preference_summary(payload: Dict[str, Any]) -> Dict[str, int]:
    return {
        "preferenceCount": len(payload.get("preferences", {})),
        "candidatePreferenceCount": len(payload.get("candidatePreferences", {})),
        "canonicalCount": len(list_preferences_by_status(payload, "canonical")),
        "deferredCandidateCount": len(list_candidate_preferences_by_status(payload, "deferred")),
        "needsReviewCandidateCount": len(list_candidate_preferences_by_status(payload, "needs-review")),
    }


def assert_no_auto_promotion(payload: Dict[str, Any]) -> bool:
    if payload.get("policy", {}).get("autoPromote") is not False:
        raise ValueError("Canonical preference resolver must not auto-promote.")
    for preference in payload.get("candidatePreferences", {}).values():
        if preference.get("preferenceStatus") == "canonical":
            raise ValueError("Candidate preferences must not become canonical automatically.")
    return True


def assert_no_canonical_mutation(payload: Dict[str, Any]) -> bool:
    if payload.get("policy", {}).get("mutationTarget") != "none":
        raise ValueError("Canonical preference resolver must not mutate canonical records.")
    for collection_name in ("preferences", "candidatePreferences"):
        for item_id, item in payload.get(collection_name, {}).items():
            if item.get("recommendedAction") == "promote-to-canonical" and collection_name == "candidatePreferences":
                raise ValueError(f"Candidate preference cannot directly promote canonical data: {item_id}.")
    return True


def compare_preference_to_editorial_decision(
    preference: Dict[str, Any],
    editorial_payload: Dict[str, Any],
) -> Dict[str, Any]:
    dhatu_id = preference.get("dhatuId")
    decision = editorial_payload.get("decisions", {}).get(dhatu_id, {})
    matches = (
        bool(decision)
        and preference.get("decisionId") == decision.get("decisionId")
        and preference.get("preferredReadingId") == decision.get("preferredReadingId")
    )
    return {
        "dhatuId": dhatu_id,
        "preferenceDecisionId": preference.get("decisionId"),
        "editorialDecisionId": decision.get("decisionId"),
        "matches": matches,
    }


def _validate_preference(
    dhatu_id: str,
    preference: Dict[str, Any],
    editorial_payload: Dict[str, Any] | None,
    recension_payload: Dict[str, Any] | None,
) -> None:
    for field in (
        "dhatuId",
        "preferredReadingId",
        "decisionId",
        "preferenceStatus",
        "confidence",
        "recommendedAction",
        "rationale",
    ):
        if field not in preference:
            raise ValueError(f"Preference {dhatu_id} missing field: {field}.")
    if preference["dhatuId"] != dhatu_id:
        raise ValueError(f"Preference key mismatch for {dhatu_id}.")
    _validate_common_statuses(preference, f"Preference {dhatu_id}")
    if editorial_payload is not None:
        comparison = compare_preference_to_editorial_decision(preference, editorial_payload)
        if not comparison["matches"]:
            raise ValueError(f"Preference does not reference a valid editorial decision: {dhatu_id}.")
    if recension_payload is not None:
        entry = recension_payload.get("variantReadings", {}).get(dhatu_id, {})
        reading_ids = {reading.get("readingId") for reading in entry.get("readings", [])}
        if preference["preferredReadingId"] not in reading_ids:
            raise ValueError(f"Preference preferredReadingId does not resolve in recensions: {dhatu_id}.")


def _validate_candidate_preference(
    candidate_id: str,
    preference: Dict[str, Any],
    editorial_payload: Dict[str, Any] | None,
) -> None:
    for field in ("candidateId", "preferenceStatus", "confidence", "recommendedAction", "rationale"):
        if field not in preference:
            raise ValueError(f"Candidate preference {candidate_id} missing field: {field}.")
    if preference["candidateId"] != candidate_id:
        raise ValueError(f"Candidate preference key mismatch for {candidate_id}.")
    _validate_common_statuses(preference, f"Candidate preference {candidate_id}")
    if preference["preferenceStatus"] == "canonical":
        raise ValueError(f"Candidate preference cannot be canonical without explicit promotion: {candidate_id}.")
    if editorial_payload is not None and candidate_id not in editorial_payload.get("recommendations", {}):
        raise ValueError(f"Candidate preference does not reference an editorial recommendation: {candidate_id}.")


def _validate_common_statuses(item: Dict[str, Any], context: str) -> None:
    if item["preferenceStatus"] not in ALLOWED_PREFERENCE_STATUSES:
        raise ValueError(f"{context} has invalid preferenceStatus.")
    if item["recommendedAction"] not in ALLOWED_RECOMMENDED_ACTIONS:
        raise ValueError(f"{context} has invalid recommendedAction.")
    if item["confidence"] not in {"high", "medium", "low"}:
        raise ValueError(f"{context} has invalid confidence.")


def _decision_matches_recension(decision: Dict[str, Any], recension_payload: Dict[str, Any]) -> bool:
    dhatu_id = decision.get("dhatuId")
    entry = recension_payload.get("variantReadings", {}).get(dhatu_id, {})
    return decision.get("preferredReadingId") == entry.get("canonicalPreference", {}).get("preferredReadingId")


def _confidence_for_decision(
    decision: Dict[str, Any],
    dhatu_id: str,
    attribution_payload: Dict[str, Any] | None,
) -> str:
    if decision.get("evidenceScore", 0.0) >= 0.8:
        return "high"
    if attribution_payload:
        attribution = attribution_payload.get("recordAttributions", {}).get(dhatu_id, {})
        if attribution.get("sourceConfidence") in {"high", "medium", "low"}:
            return attribution["sourceConfidence"]
    return "medium" if decision.get("evidenceScore", 0.0) >= 0.5 else "low"


def _preference_status_for_decision(decision: Dict[str, Any]) -> str:
    status = decision.get("status")
    if status == "accepted" and decision.get("recommendedAction") == "keep-canonical":
        return "canonical"
    if status == "rejected":
        return "rejected"
    if status == "deferred":
        return "deferred"
    if status == "disputed":
        return "disputed"
    return "needs-review"


def _candidate_status(recommendation: Dict[str, Any] | None, unresolved: Dict[str, Any]) -> str:
    status = (recommendation or {}).get("status") or unresolved.get("status")
    if status in {"defer", "deferred"}:
        return "deferred"
    if status in {"reject", "rejected"}:
        return "rejected"
    if status in {"needs-review", "pending"}:
        return "needs-review"
    return "needs-review"


def _candidate_confidence(candidate_id: str, attribution_payload: Dict[str, Any] | None) -> str:
    if attribution_payload:
        attribution = attribution_payload.get("recordAttributions", {}).get(candidate_id, {})
        confidence = attribution.get("sourceConfidence")
        if confidence in {"high", "medium", "low"}:
            return confidence
    return "medium"


def _rationale_for_decision(decision: Dict[str, Any], status: str) -> str:
    if status == "canonical":
        return "Accepted editorial decision with canonical seed support"
    return decision.get("rationale", "Editorial decision requires review")


def _require_dict(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return value
