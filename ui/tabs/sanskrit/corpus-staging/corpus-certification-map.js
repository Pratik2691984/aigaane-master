"use strict";

const CORPUS_CERTIFICATION_SCHEMA = "sanskrit-bulk-corpus-certification.v1";

const CORPUS_CERTIFICATION_STATES = Object.freeze({
  EMPTY: "EMPTY",
  CERTIFICATION_READY: "CERTIFICATION_READY",
  CERTIFICATION_BLOCKED: "CERTIFICATION_BLOCKED"
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

function normalizeCorpusCertificationInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_CERTIFICATION_SCHEMA,
    certificationStatus: String(input.certificationStatus || "certification-ready"),
    certificationLedgerCount: asCount(input.certificationLedgerCount),
    certificationLedger: freeze(asArray(input.certificationLedger)),
    acceptedRecordCount: asCount(input.acceptedRecordCount),
    rejectedRecordCount: asCount(input.rejectedRecordCount),
    approvalStatus: String(input.approvalStatus || "approval-blocked"),
    recommendation: String(input.recommendation || "hold"),
    approval: freeze(isObject(input.approval) ? input.approval : {}),
    previewOnly: true,
    readOnly: true,
    certificationExecutionAllowed: false,
    approvalExecutionAllowed: false,
    promotionExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusCertificationRecord(input = {}) {
  const normalized = normalizeCorpusCertificationInput(input);

  let state = CORPUS_CERTIFICATION_STATES.CERTIFICATION_READY;

  if (normalized.certificationLedgerCount === 0) {
    state = CORPUS_CERTIFICATION_STATES.EMPTY;
  }

  if (
    normalized.certificationStatus === "certification-blocked" ||
    (normalized.approval && normalized.approval.valid === false)
  ) {
    state = CORPUS_CERTIFICATION_STATES.CERTIFICATION_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_CERTIFICATION_SCHEMA,
  CORPUS_CERTIFICATION_STATES,
  normalizeCorpusCertificationInput,
  buildCorpusCertificationRecord
};