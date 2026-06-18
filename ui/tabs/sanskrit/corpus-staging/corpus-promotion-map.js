"use strict";

const CORPUS_PROMOTION_SCHEMA = "sanskrit-bulk-corpus-promotion-readiness.v1";

const CORPUS_PROMOTION_STATES = Object.freeze({
  EMPTY: "EMPTY",
  PROMOTION_READY: "PROMOTION_READY",
  PROMOTION_BLOCKED: "PROMOTION_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeCorpusPromotionInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_PROMOTION_SCHEMA,
    promotionStatus: String(input.promotionStatus || "promotion-ready"),
    promotionConfidence: asCount(input.promotionConfidence),
    acceptedRecordCount: asCount(input.acceptedRecordCount),
    rejectedRecordCount: asCount(input.rejectedRecordCount),
    advisory: freeze(asArray(input.advisory)),
    blockers: freeze(asArray(input.blockers)),
    admission: freeze(isObject(input.admission) ? input.admission : {}),
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

function buildCorpusPromotionRecord(input = {}) {
  const normalized = normalizeCorpusPromotionInput(input);

  let state = CORPUS_PROMOTION_STATES.PROMOTION_READY;

  if (normalized.acceptedRecordCount === 0) {
    state = CORPUS_PROMOTION_STATES.EMPTY;
  }

  if (
    normalized.blockers.length ||
    normalized.promotionConfidence < 100 ||
    (normalized.admission && normalized.admission.valid === false)
  ) {
    state = CORPUS_PROMOTION_STATES.PROMOTION_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_PROMOTION_SCHEMA,
  CORPUS_PROMOTION_STATES,
  normalizeCorpusPromotionInput,
  buildCorpusPromotionRecord
};