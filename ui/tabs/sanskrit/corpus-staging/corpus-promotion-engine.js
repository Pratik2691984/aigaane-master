"use strict";

const {
  buildCorpusPromotionRecord
} = require("./corpus-promotion-map.js");

const {
  summarizeCorpusAdmission,
  buildCorpusAdmission
} = require("./corpus-admission-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function derivePromotionStatus(admission = {}) {
  if (admission.valid === false) {
    return "promotion-blocked";
  }

  if (
    admission.admissionStatus === "admission-ready" &&
    Number(admission.acceptedRecordCount || 0) > 0 &&
    Number(admission.rejectedRecordCount || 0) === 0 &&
    admission.canonicalWriteAllowed === false &&
    admission.promotionAllowed === false
  ) {
    return "promotion-ready";
  }

  return "promotion-review";
}

function computePromotionConfidence(admission = {}) {
  if (derivePromotionStatus(admission) === "promotion-ready") {
    return 100;
  }

  let confidence = 0;

  if (admission.valid === true) confidence += 25;
  if (admission.admissionStatus === "admission-ready") confidence += 25;
  if (Number(admission.acceptedRecordCount || 0) > 0) confidence += 25;
  if (admission.canonicalWriteAllowed === false) confidence += 25;

  return Math.max(0, Math.min(100, confidence));
}

function buildPromotionAdvisory(status) {
  if (status === "promotion-ready") {
    return freeze([
      "admissionReady",
      "promotionPreviewReady",
      "canonicalWriteLocked",
      "manualPromotionReviewRequired"
    ]);
  }

  if (status === "promotion-review") {
    return freeze(["requiresManualReview"]);
  }

  return freeze([]);
}

function buildPromotionBlockers(status) {
  if (status === "promotion-blocked") {
    return freeze(["admissionNotReady"]);
  }

  return freeze([]);
}

function buildCorpusPromotionReadiness(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const admissionSummary = summarizeCorpusAdmission(
    input,
    windowSize,
    secondsPerWindow
  );

  const admission = buildCorpusAdmission(input, windowSize, secondsPerWindow);
  const promotionStatus = derivePromotionStatus(admissionSummary);
  const promotionConfidence = computePromotionConfidence(admissionSummary);

  return buildCorpusPromotionRecord({
    promotionStatus,
    promotionConfidence,
    acceptedRecordCount: admissionSummary.acceptedRecordCount,
    rejectedRecordCount: admissionSummary.rejectedRecordCount,
    advisory: buildPromotionAdvisory(promotionStatus),
    blockers: buildPromotionBlockers(promotionStatus),
    admission
  });
}

function summarizeCorpusPromotionReadiness(input = {}, windowSize = 250, secondsPerWindow = 12.5) {
  const promotion = buildCorpusPromotionReadiness(input, windowSize, secondsPerWindow);

  return freeze({
    state: promotion.state,
    valid: promotion.state !== "PROMOTION_BLOCKED",
    promotionStatus: promotion.promotionStatus,
    promotionConfidence: promotion.promotionConfidence,
    acceptedRecordCount: promotion.acceptedRecordCount,
    rejectedRecordCount: promotion.rejectedRecordCount,
    advisory: promotion.advisory,
    blockers: promotion.blockers,
    previewOnly: true,
    readOnly: true,
    promotionReadinessAllowed: true,
    promotionExecutionAllowed: false,
    admissionExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  derivePromotionStatus,
  computePromotionConfidence,
  buildPromotionAdvisory,
  buildPromotionBlockers,
  buildCorpusPromotionReadiness,
  summarizeCorpusPromotionReadiness
};