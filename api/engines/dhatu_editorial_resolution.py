from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESOLUTIONS_PATH = ROOT / "data" / "sanskrit" / "ingestion" / "editorial_resolutions.v1.json"
DECISION_ID_RE = re.compile(r"^ED_[A-Z0-9_]+$")
RECOMMENDATION_ID_RE = re.compile(r"^REC_[A-Z0-9_]+$")
ALLOWED_DECISION_STATUSES = {"accepted", "rejected", "deferred", "disputed"}
ALLOWED_REVIEW_STATUSES = {"reviewed", "pending", "needs-review"}
ALLOWED_RECOMMENDED_ACTIONS = {
    "keep-canonical",
    "promote-to-canonical",
    "reject-candidate",
    "defer",
    "manual-review-required",
    "no-action",
}
ALLOWED_RECOMMENDATION_STATUSES = {"defer", "reject", "accept", "needs-review"}
DEFAULT_WEIGHTS = {
    "sourceConfidence": 0.4,
    "recensionSupport": 0.25,
    "canonicalConsistency": 0.2,
    "goldsetAgreement": 0.15,
}
CONFIDENCE_SCORES = {"high": 1.0, "medium": 0.5, "low": 0.0}
NON_MUTATING_ACTIONS = {"keep-canonical", "reject-candidate", "defer", "manual-review-required", "no-action"}


def load_editorial_resolutions(path: Any = DEFAULT_RESOLUTIONS_PATH) -> Dict[str, Any]:
    resolution_path = Path(path)
    with resolution_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return validate_editorial_resolutions(payload)


def validate_editorial_resolutions(
    payload: Dict[str, Any],
    recensions: Dict[str, Any] | None = None,
    source_attribution: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Editorial resolution payload must be a JSON object.")
    for field in ("resolutionVersion", "policy", "scoring", "decisions", "recommendations"):
        if field not in payload:
            raise ValueError(f"Editorial resolution payload missing field: {field}.")

    policy = _require_dict(payload["policy"], "policy")
    _validate_policy(policy)

    scoring = _require_dict(payload["scoring"], "scoring")
    weights = _require_dict(scoring.get("weights"), "scoring.weights")
    _validate_weights(weights)

    decisions = _require_dict(payload["decisions"], "decisions")
    recommendations = _require_dict(payload["recommendations"], "recommendations")
    agents = _source_agents(source_attribution)

    for dhatu_id, decision in decisions.items():
        _validate_decision(dhatu_id, decision, recensions, agents)
    for candidate_id, recommendation in recommendations.items():
        _validate_recommendation(candidate_id, recommendation)

    assert_no_auto_promotion(payload)
    assert_preserves_alternatives(payload)
    return copy.deepcopy(payload)


def get_decision(payload: Dict[str, Any], dhatu_id: str) -> Dict[str, Any] | None:
    decision = payload.get("decisions", {}).get(dhatu_id)
    return copy.deepcopy(decision) if decision else None


def get_recommendation(payload: Dict[str, Any], candidate_id: str) -> Dict[str, Any] | None:
    recommendation = payload.get("recommendations", {}).get(candidate_id)
    return copy.deepcopy(recommendation) if recommendation else None


def list_decisions_by_status(payload: Dict[str, Any], status: str) -> List[Dict[str, Any]]:
    if status not in ALLOWED_DECISION_STATUSES:
        raise ValueError(f"Invalid decision status: {status}.")
    return [
        copy.deepcopy(decision)
        for _, decision in sorted(payload.get("decisions", {}).items())
        if decision.get("status") == status
    ]


def list_recommendations_by_status(payload: Dict[str, Any], status: str) -> List[Dict[str, Any]]:
    if status not in ALLOWED_RECOMMENDATION_STATUSES:
        raise ValueError(f"Invalid recommendation status: {status}.")
    return [
        copy.deepcopy(recommendation)
        for _, recommendation in sorted(payload.get("recommendations", {}).items())
        if recommendation.get("status") == status
    ]


def score_reading_evidence(
    reading: Dict[str, Any],
    attribution: Dict[str, Any] | None = None,
    goldset_ids: set[str] | None = None,
    weights: Dict[str, float] | None = None,
) -> float:
    active_weights = weights or DEFAULT_WEIGHTS
    _validate_weights(active_weights)

    dhatu_id = reading.get("canonicalDhatuId") or reading.get("dhatuId")
    source_confidence = _source_confidence_score(reading, dhatu_id, attribution)
    recension_support = 1.0 if reading.get("recension") == "canonical-seed" else 0.5
    canonical_consistency = 1.0 if reading.get("readingType") == "canonical" else 0.5
    goldset_agreement = 1.0 if goldset_ids and dhatu_id in goldset_ids else 0.0

    score = (
        active_weights["sourceConfidence"] * source_confidence
        + active_weights["recensionSupport"] * recension_support
        + active_weights["canonicalConsistency"] * canonical_consistency
        + active_weights["goldsetAgreement"] * goldset_agreement
    )
    return round(max(0.0, min(1.0, score)), 4)


def rank_readings_for_dhatu(
    recensions_payload: Dict[str, Any],
    dhatu_id: str,
    attribution_payload: Dict[str, Any] | None = None,
    goldset_ids: set[str] | None = None,
) -> List[Dict[str, Any]]:
    entry = recensions_payload.get("variantReadings", {}).get(dhatu_id)
    if not entry:
        return []
    ranked = []
    for reading in entry.get("readings", []):
        item = copy.deepcopy(reading)
        item["canonicalDhatuId"] = dhatu_id
        item["evidenceScore"] = score_reading_evidence(
            item,
            attribution=attribution_payload,
            goldset_ids=goldset_ids,
        )
        ranked.append(item)
    return sorted(ranked, key=lambda reading: (-reading["evidenceScore"], reading["readingId"]))


def build_resolution_summary(payload: Dict[str, Any]) -> Dict[str, int]:
    decisions = payload.get("decisions", {})
    recommendations = payload.get("recommendations", {})
    return {
        "decisionCount": len(decisions),
        "recommendationCount": len(recommendations),
        "acceptedDecisionCount": len(list_decisions_by_status(payload, "accepted")),
        "deferRecommendationCount": len(list_recommendations_by_status(payload, "defer")),
        "reviewedDecisionCount": len(
            [decision for decision in decisions.values() if decision.get("reviewStatus") == "reviewed"]
        ),
    }


def assert_no_auto_promotion(payload: Dict[str, Any]) -> bool:
    policy = payload.get("policy", {})
    if policy.get("autoPromote") is not False:
        raise ValueError("Editorial policy must keep autoPromote false.")
    if policy.get("mutationTarget") != "none":
        raise ValueError("Editorial policy mutationTarget must be none.")
    for decision in payload.get("decisions", {}).values():
        if decision.get("recommendedAction") == "promote-to-canonical" and decision.get("reviewStatus") != "reviewed":
            raise ValueError("Promotion recommendations require reviewed status.")
    for recommendation in payload.get("recommendations", {}).values():
        if recommendation.get("recommendedAction") not in NON_MUTATING_ACTIONS:
            raise ValueError("Recommendations must not directly mutate canonical registry.")
    return True


def assert_preserves_alternatives(payload: Dict[str, Any]) -> bool:
    if payload.get("policy", {}).get("preserveRejectedAlternatives") is not True:
        raise ValueError("Editorial policy must preserve rejected alternatives.")
    for decision_id, decision in _iter_decisions(payload):
        alternatives = decision.get("preservedAlternatives")
        if alternatives is None or not isinstance(alternatives, list):
            raise ValueError(f"Decision must preserve alternatives as a list: {decision_id}.")
    return True


def compare_decision_to_preferred_reading(
    decision: Dict[str, Any],
    recensions_payload: Dict[str, Any],
) -> Dict[str, Any]:
    dhatu_id = decision.get("dhatuId")
    entry = recensions_payload.get("variantReadings", {}).get(dhatu_id, {})
    preferred_id = entry.get("canonicalPreference", {}).get("preferredReadingId")
    matches = decision.get("preferredReadingId") == preferred_id
    return {
        "dhatuId": dhatu_id,
        "decisionPreferredReadingId": decision.get("preferredReadingId"),
        "recensionPreferredReadingId": preferred_id,
        "matches": matches,
    }


def _validate_policy(policy: Dict[str, Any]) -> None:
    if policy.get("autoPromote") is not False:
        raise ValueError("policy.autoPromote must be false.")
    if policy.get("requiresHumanReview") is not True:
        raise ValueError("policy.requiresHumanReview must be true.")
    if policy.get("preserveRejectedAlternatives") is not True:
        raise ValueError("policy.preserveRejectedAlternatives must be true.")
    if policy.get("mutationTarget") != "none":
        raise ValueError('policy.mutationTarget must be "none".')


def _validate_weights(weights: Dict[str, Any]) -> None:
    for field in DEFAULT_WEIGHTS:
        if field not in weights:
            raise ValueError(f"Missing scoring weight: {field}.")
        if not isinstance(weights[field], (int, float)):
            raise ValueError(f"Scoring weight must be numeric: {field}.")
    total = sum(float(weights[field]) for field in DEFAULT_WEIGHTS)
    if abs(total - 1.0) > 0.001:
        raise ValueError("Scoring weights must sum to approximately 1.0.")


def _validate_decision(
    dhatu_id: str,
    decision: Dict[str, Any],
    recensions: Dict[str, Any] | None,
    agents: set[str] | None,
) -> None:
    for field in (
        "decisionId",
        "dhatuId",
        "status",
        "preferredReadingId",
        "evidenceScore",
        "reviewStatus",
        "reviewer",
        "rationale",
        "preservedAlternatives",
        "recommendedAction",
        "notes",
    ):
        if field not in decision:
            raise ValueError(f"Decision {dhatu_id} missing field: {field}.")
    if decision["dhatuId"] != dhatu_id:
        raise ValueError(f"Decision key mismatch for {dhatu_id}.")
    if not DECISION_ID_RE.match(decision["decisionId"]):
        raise ValueError(f"Invalid decisionId for {dhatu_id}.")
    if decision["status"] not in ALLOWED_DECISION_STATUSES:
        raise ValueError(f"Invalid decision status for {dhatu_id}.")
    if decision["reviewStatus"] not in ALLOWED_REVIEW_STATUSES:
        raise ValueError(f"Invalid reviewStatus for {dhatu_id}.")
    if decision["recommendedAction"] not in ALLOWED_RECOMMENDED_ACTIONS:
        raise ValueError(f"Invalid recommendedAction for {dhatu_id}.")
    if not isinstance(decision["evidenceScore"], (int, float)) or not 0.0 <= decision["evidenceScore"] <= 1.0:
        raise ValueError(f"Decision evidenceScore must be within 0.0 and 1.0: {dhatu_id}.")
    if not isinstance(decision["preservedAlternatives"], list):
        raise ValueError(f"Decision preservedAlternatives must be a list: {dhatu_id}.")
    if not isinstance(decision["notes"], list):
        raise ValueError(f"Decision notes must be a list: {dhatu_id}.")
    if agents is not None and decision["reviewer"] not in agents:
        raise ValueError(f"Decision reviewer does not resolve: {decision['reviewer']}.")
    if recensions is not None:
        comparison = compare_decision_to_preferred_reading(decision, recensions)
        if not comparison["matches"]:
            raise ValueError(f"Decision preferredReadingId does not resolve in recensions: {dhatu_id}.")


def _validate_recommendation(candidate_id: str, recommendation: Dict[str, Any]) -> None:
    for field in (
        "recommendationId",
        "status",
        "candidateRoot",
        "candidateCanonicalForm",
        "reason",
        "recommendedAction",
        "notes",
    ):
        if field not in recommendation:
            raise ValueError(f"Recommendation {candidate_id} missing field: {field}.")
    if not RECOMMENDATION_ID_RE.match(recommendation["recommendationId"]):
        raise ValueError(f"Invalid recommendationId for {candidate_id}.")
    if recommendation["status"] not in ALLOWED_RECOMMENDATION_STATUSES:
        raise ValueError(f"Invalid recommendation status for {candidate_id}.")
    if recommendation["recommendedAction"] not in NON_MUTATING_ACTIONS:
        raise ValueError(f"Recommendation must not mutate canonical registry: {candidate_id}.")
    if not isinstance(recommendation["notes"], list):
        raise ValueError(f"Recommendation notes must be a list: {candidate_id}.")


def _source_confidence_score(
    reading: Dict[str, Any],
    dhatu_id: str | None,
    attribution: Dict[str, Any] | None,
) -> float:
    if attribution and dhatu_id:
        record = attribution.get("recordAttributions", {}).get(dhatu_id)
        if record:
            return CONFIDENCE_SCORES.get(record.get("sourceConfidence"), 0.0)
    return CONFIDENCE_SCORES.get(reading.get("confidence"), 0.0)


def _source_agents(source_attribution: Dict[str, Any] | None) -> set[str] | None:
    if source_attribution is None:
        return None
    agents = _require_dict(source_attribution.get("agents"), "source_attribution.agents")
    return set(agents.keys())


def _iter_decisions(payload: Dict[str, Any]) -> List[tuple[str, Dict[str, Any]]]:
    return [
        (decision_id, decision)
        for decision_id, decision in sorted(payload.get("decisions", {}).items())
    ]


def _require_dict(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return value
