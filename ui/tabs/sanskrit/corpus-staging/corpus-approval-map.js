"use strict";

const CORPUS_APPROVAL_SCHEMA = "sanskrit-bulk-corpus-promotion-approval.v1";

const CORPUS_APPROVAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  APPROVAL_READY: "APPROVAL_READY",
  APPROVAL_BLOCKED: "APPROVAL_BLOCKED"
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

function normalizeCorpusApprovalInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_APPROVAL_SCHEMA,
    approvalStatus: String(input.approvalStatus || "approval-ready"),
    approvalLedgerCount: asCount(input.approvalLedgerCount),
    approvalLedger: freeze(asArray(input.approvalLedger)),
    recommendation: String(input.recommendation || "hold"),
    advisoryStatus: String(input.advisoryStatus || "advisory-blocked"),
    acceptedRecordCount: asCount(input.acceptedRecordCount),
    rejectedRecordCount: asCount(input.rejectedRecordCount),
    advisory: freeze(isObject(input.advisory) ? input.advisory : {}),
    previewOnly: true,
    readOnly: true,
    approvalExecutionAllowed: false,
    advisoryExecutionAllowed: false,
    promotionExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusApprovalRecord(input = {}) {
  const normalized = normalizeCorpusApprovalInput(input);

  let state = CORPUS_APPROVAL_STATES.APPROVAL_READY;

  if (normalized.approvalLedgerCount === 0) {
    state = CORPUS_APPROVAL_STATES.EMPTY;
  }

  if (
    normalized.approvalStatus === "approval-blocked" ||
    (normalized.advisory && normalized.advisory.valid === false)
  ) {
    state = CORPUS_APPROVAL_STATES.APPROVAL_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_APPROVAL_SCHEMA,
  CORPUS_APPROVAL_STATES,
  normalizeCorpusApprovalInput,
  buildCorpusApprovalRecord
};