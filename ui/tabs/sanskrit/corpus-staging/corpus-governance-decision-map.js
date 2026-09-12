"use strict";

const CORPUS_GOVERNANCE_DECISION_SCHEMA =
  "sanskrit-bulk-corpus-governance-decision.v1";

const CORPUS_GOVERNANCE_DECISION_STATES = Object.freeze({
  PENDING: "GOVERNANCE_DECISION_PENDING",
  BLOCKED: "GOVERNANCE_DECISION_BLOCKED",
  CLEARED: "GOVERNANCE_DECISION_CLEARED_FOR_AUTHORIZATION"
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
      clearedForAuthorizationIsWrite: false,
      clearedForAuthorizationIsImport: false,
      clearedForAuthorizationIsExecution: false,
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
    normalized.status === "governance-decision-blocked" ||
    normalized.failures.length
  ) {
    state = CORPUS_GOVERNANCE_DECISION_STATES.BLOCKED;
  } else if (
    normalized.status === "governance-decision-cleared-for-authorization"
  ) {
    state = CORPUS_GOVERNANCE_DECISION_STATES.CLEARED;
  }
  return freeze({
    ...normalized,
    state,
    nextGate: "38G PROMOTION AUTHORIZATION"
  });
}

module.exports = {
  CORPUS_GOVERNANCE_DECISION_SCHEMA,
  CORPUS_GOVERNANCE_DECISION_STATES,
  normalizeCorpusGovernanceDecisionInput,
  buildCorpusGovernanceDecisionRecord
};
