"use strict";

const CORPUS_MANUAL_REVIEW_SCHEMA = "sanskrit-bulk-corpus-manual-review.v1";

const CORPUS_MANUAL_REVIEW_STATES = Object.freeze({
  PENDING: "MANUAL_REVIEW_PENDING",
  ATTESTED: "MANUAL_REVIEW_ATTESTED",
  BLOCKED: "MANUAL_REVIEW_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function normalizeCorpusManualReviewInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_MANUAL_REVIEW_SCHEMA,
    status: String(input.status || "manual-review-pending"),
    attested: input.attested === true,
    hardStop: true,
    failures: freeze(asArray(input.failures)),
    authorization: freeze({
      manualReviewIsAuthorization: false,
      manualReviewIsExecutionAuthorization: false,
      certificationIsAuthorization: false,
      canonicalWrite: false,
      promotion: false,
      import: false,
      execution: false
    }),
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false,
    executionAllowed: false,
    manualReviewExecutionAllowed: false
  });
}

function buildCorpusManualReviewRecord(input = {}) {
  const normalized = normalizeCorpusManualReviewInput(input);
  let state = CORPUS_MANUAL_REVIEW_STATES.PENDING;
  if (normalized.status === "manual-review-blocked" || normalized.failures.length) {
    state = CORPUS_MANUAL_REVIEW_STATES.BLOCKED;
  } else if (normalized.attested && normalized.status === "manual-review-attested") {
    state = CORPUS_MANUAL_REVIEW_STATES.ATTESTED;
  }
  return freeze({
    ...normalized,
    state,
    nextGate: "POST-ATTESTATION HOLD"
  });
}

module.exports = {
  CORPUS_MANUAL_REVIEW_SCHEMA,
  CORPUS_MANUAL_REVIEW_STATES,
  normalizeCorpusManualReviewInput,
  buildCorpusManualReviewRecord
};
