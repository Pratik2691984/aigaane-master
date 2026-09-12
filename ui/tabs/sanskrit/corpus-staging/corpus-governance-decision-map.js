"use strict";

const CORPUS_GOVERNANCE_DECISION_SCHEMA =
  "sanskrit-bulk-corpus-governance-decision.v1";

const CORPUS_GOVERNANCE_DECISION_STATES = Object.freeze({
  PENDING: "PENDING",
  BLOCKED: "BLOCKED",
  CLEARED_FOR_AUTHORIZATION: "CLEARED_FOR_AUTHORIZATION"
});

function freeze(v) {
  return Object.freeze(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function normalizeCorpusGovernanceDecisionInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_GOVERNANCE_DECISION_SCHEMA,
    status: String(input.status || "governance-decision-pending"),
    decision: input.decision == null ? null : String(input.decision),
    hardStop: true,
    failures: freeze(asArray(input.failures)),
    authorization: freeze({
      governanceDecisionIsAuthorization: false,
      governanceDecisionIsExecutionAuthorization: false,
      governanceClearanceIsWriteAuthorization: false,
      governanceClearanceIsPromotionAuthorization: false,
      governanceClearanceIsImportAuthorization: false,
      governanceClearanceIsExecutionAuthorization: false,
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
    governanceExecutionAllowed: false
  });
}

function buildCorpusGovernanceDecisionRecord(input = {}) {
  const normalized = normalizeCorpusGovernanceDecisionInput(input);
  let state = CORPUS_GOVERNANCE_DECISION_STATES.PENDING;
  if (
    normalized.status === "governance-blocked" ||
    normalized.status === "governance-decision-blocked" ||
    normalized.failures.length
  ) {
    state = CORPUS_GOVERNANCE_DECISION_STATES.BLOCKED;
  } else if (
    normalized.status === "governance-cleared-for-authorization" ||
    normalized.status === "governance-decision-cleared-for-authorization"
  ) {
    state = CORPUS_GOVERNANCE_DECISION_STATES.CLEARED_FOR_AUTHORIZATION;
  }
  return freeze({
    ...normalized,
    state,
    nextGate: "38G PROMOTION AUTHORIZATION",
    isNonAuthorizing:
      normalized.canonicalWriteAllowed === false &&
      normalized.promotionAllowed === false &&
      normalized.importAllowed === false &&
      normalized.executionAllowed === false
  });
}

module.exports = {
  CORPUS_GOVERNANCE_DECISION_SCHEMA,
  CORPUS_GOVERNANCE_DECISION_STATES,
  normalizeCorpusGovernanceDecisionInput,
  buildCorpusGovernanceDecisionRecord
};
