"use strict";

const CORPUS_CANONICAL_SCHEMA = "sanskrit-bulk-corpus-canonical-preview.v1";

const CORPUS_CANONICAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  CANONICAL_PREVIEW_READY: "CANONICAL_PREVIEW_READY",
  CANONICAL_PREVIEW_BLOCKED: "CANONICAL_PREVIEW_BLOCKED"
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

function normalizeCorpusCanonicalInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_CANONICAL_SCHEMA,
    canonicalStatus: String(input.canonicalStatus || "canonical-preview-ready"),
    canonicalLedgerCount: asCount(input.canonicalLedgerCount),
    canonicalLedger: freeze(asArray(input.canonicalLedger)),
    acceptedRecordCount: asCount(input.acceptedRecordCount),
    rejectedRecordCount: asCount(input.rejectedRecordCount),
    certificationStatus: String(input.certificationStatus || "certification-blocked"),
    recommendation: String(input.recommendation || "hold"),
    certification: freeze(isObject(input.certification) ? input.certification : {}),
    previewOnly: true,
    readOnly: true,
    canonicalExecutionAllowed: false,
    certificationExecutionAllowed: false,
    promotionExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusCanonicalRecord(input = {}) {
  const normalized = normalizeCorpusCanonicalInput(input);

  let state = CORPUS_CANONICAL_STATES.CANONICAL_PREVIEW_READY;

  if (normalized.canonicalLedgerCount === 0) {
    state = CORPUS_CANONICAL_STATES.EMPTY;
  }

  if (
    normalized.canonicalStatus === "canonical-preview-blocked" ||
    (normalized.certification && normalized.certification.valid === false)
  ) {
    state = CORPUS_CANONICAL_STATES.CANONICAL_PREVIEW_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_CANONICAL_SCHEMA,
  CORPUS_CANONICAL_STATES,
  normalizeCorpusCanonicalInput,
  buildCorpusCanonicalRecord
};