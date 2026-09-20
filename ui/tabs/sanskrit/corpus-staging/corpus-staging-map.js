"use strict";

const CORPUS_STAGING_SCHEMA = "sanskrit-bulk-corpus-staging.v1";

const CORPUS_STAGING_STATES = Object.freeze({
  EMPTY: "EMPTY",
  STAGING_READY: "STAGING_READY",
  LIMIT_EXCEEDED: "LIMIT_EXCEEDED",
  INVALID: "INVALID"
});

const MAX_BULK_CORPUS_RECORDS = 2000;

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function normalizeCorpusStagingManifest(input = {}) {
  return freeze({
    schemaVersion: String(input.schemaVersion || CORPUS_STAGING_SCHEMA),
    status: String(input.status || "staging-ready"),
    mode: String(input.mode || "preview-only"),
    canonicalWriteAllowed: false,
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    batches: freeze(asArray(input.batches)),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildCorpusStagingManifest(input = {}) {
  const normalized = normalizeCorpusStagingManifest(input);
  const recordCount = normalized.batches.reduce((total, batch) => {
    const records = Array.isArray(batch.records) ? batch.records : [];
    return total + records.length;
  }, 0);

  return freeze({
    ...normalized,
    state: recordCount > MAX_BULK_CORPUS_RECORDS
      ? CORPUS_STAGING_STATES.LIMIT_EXCEEDED
      : CORPUS_STAGING_STATES.STAGING_READY,
    batchCount: normalized.batches.length,
    recordCount,
    previewOnly: true,
    readOnly: true
  });
}

module.exports = {
  CORPUS_STAGING_SCHEMA,
  CORPUS_STAGING_STATES,
  MAX_BULK_CORPUS_RECORDS,
  normalizeCorpusStagingManifest,
  buildCorpusStagingManifest
};