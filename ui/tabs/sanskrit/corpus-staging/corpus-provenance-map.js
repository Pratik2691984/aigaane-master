"use strict";

const CORPUS_PROVENANCE_SCHEMA = "sanskrit-bulk-corpus-provenance-audit.v1";
const STAGING_SCHEMA = "sanskrit-bulk-corpus-staging.v1";
const MAX_BULK_CORPUS_RECORDS = 2000;

const CORPUS_PROVENANCE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  PROVENANCE_READY: "PROVENANCE_READY",
  PROVENANCE_WARNING: "PROVENANCE_WARNING",
  PROVENANCE_INVALID: "PROVENANCE_INVALID",
  LIMIT_EXCEEDED: "LIMIT_EXCEEDED"
});

const CORPUS_RECORD_TYPES = Object.freeze({
  DHATU: "dhatu",
  SUTRA: "sutra",
  STOTRA: "stotra"
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

function normalizeCorpusProvenanceInput(input = {}) {
  return freeze({
    schemaVersion: String(input.schemaVersion || STAGING_SCHEMA),
    provenanceSchemaVersion: CORPUS_PROVENANCE_SCHEMA,
    mode: String(input.mode || "preview-only"),
    canonicalWriteAllowed: false,
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    batches: freeze(asArray(input.batches)),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function normalizeCorpusProvenanceRecord(record = {}) {
  return freeze({
    id: String(record.id || "").trim(),
    type: String(record.type || "").trim(),
    text: String(record.text || "").trim(),
    source: String(record.source || "").trim(),
    sourceKind: String(record.sourceKind || "manual").trim(),
    batchLineage: String(record.batchLineage || "").trim(),
    notes: String(record.notes || "").trim()
  });
}

module.exports = {
  CORPUS_PROVENANCE_SCHEMA,
  STAGING_SCHEMA,
  MAX_BULK_CORPUS_RECORDS,
  CORPUS_PROVENANCE_STATES,
  CORPUS_RECORD_TYPES,
  normalizeCorpusProvenanceInput,
  normalizeCorpusProvenanceRecord
};