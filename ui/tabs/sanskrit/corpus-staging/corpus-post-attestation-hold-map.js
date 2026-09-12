"use strict";

const CORPUS_POST_ATTESTATION_HOLD_SCHEMA =
  "sanskrit-bulk-corpus-post-attestation-hold.v1";

const CORPUS_POST_ATTESTATION_HOLD_STATES = Object.freeze({
  WAITING: "HOLD_WAITING_ATTESTATION",
  ACTIVE: "HOLD_ACTIVE",
  BLOCKED: "HOLD_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function normalizeCorpusPostAttestationHoldInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_POST_ATTESTATION_HOLD_SCHEMA,
    status: String(input.status || "hold-waiting-attestation"),
    holdActive: input.holdActive !== false,
    holdCompleted: false,
    autoPromote: false,
    waitingAttestation: input.waitingAttestation === true,
    failures: freeze(asArray(input.failures)),
    authorization: freeze({
      holdIsAuthorization: false,
      attestationIsAuthorization: false,
      manualReviewIsExecutionAuthorization: false,
      canonicalWrite: false,
      promotion: false,
      import: false,
      execution: false
    }),
    previewOnly: true,
    readOnly: true,
    hardStop: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false,
    executionAllowed: false,
    holdExecutionAllowed: false
  });
}

function buildCorpusPostAttestationHoldRecord(input = {}) {
  const normalized = normalizeCorpusPostAttestationHoldInput(input);
  let state = CORPUS_POST_ATTESTATION_HOLD_STATES.WAITING;
  if (normalized.status === "hold-blocked" || normalized.failures.length) {
    state = CORPUS_POST_ATTESTATION_HOLD_STATES.BLOCKED;
  } else if (normalized.status === "hold-active") {
    state = CORPUS_POST_ATTESTATION_HOLD_STATES.ACTIVE;
  }
  return freeze({
    ...normalized,
    state,
    nextGate: "38F FINAL GOVERNANCE DECISION"
  });
}

module.exports = {
  CORPUS_POST_ATTESTATION_HOLD_SCHEMA,
  CORPUS_POST_ATTESTATION_HOLD_STATES,
  normalizeCorpusPostAttestationHoldInput,
  buildCorpusPostAttestationHoldRecord
};
