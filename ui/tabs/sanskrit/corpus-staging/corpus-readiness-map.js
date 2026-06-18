"use strict";

const CORPUS_READINESS_SCHEMA = "sanskrit-bulk-corpus-readiness.v1";
const MAX_BULK_CORPUS_RECORDS = 2000;

const CORPUS_READINESS_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  WARNING: "WARNING",
  BLOCKED: "BLOCKED",
  LIMIT_EXCEEDED: "LIMIT_EXCEEDED"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function normalizeCorpusReadinessInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_READINESS_SCHEMA,
    recordCount: asCount(input.recordCount),
    batchCount: asCount(input.batchCount),
    errors: freeze(asArray(input.errors)),
    warnings: freeze(asArray(input.warnings)),
    staging: freeze(isObject(input.staging) ? input.staging : {}),
    validator: freeze(isObject(input.validator) ? input.validator : {}),
    provenance: freeze(isObject(input.provenance) ? input.provenance : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {}),
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false
  });
}

function buildCorpusReadinessRecord(input = {}) {
  const normalized = normalizeCorpusReadinessInput(input);

  let state = CORPUS_READINESS_STATES.READY;
  if (normalized.recordCount > MAX_BULK_CORPUS_RECORDS) {
    state = CORPUS_READINESS_STATES.LIMIT_EXCEEDED;
  } else if (normalized.errors.length) {
    state = CORPUS_READINESS_STATES.BLOCKED;
  } else if (normalized.warnings.length) {
    state = CORPUS_READINESS_STATES.WARNING;
  }

  return freeze({
    ...normalized,
    state,
    maxRecords: MAX_BULK_CORPUS_RECORDS
  });
}

module.exports = {
  CORPUS_READINESS_SCHEMA,
  CORPUS_READINESS_STATES,
  MAX_BULK_CORPUS_RECORDS,
  normalizeCorpusReadinessInput,
  buildCorpusReadinessRecord
};