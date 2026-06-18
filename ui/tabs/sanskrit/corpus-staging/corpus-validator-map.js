"use strict";

const CORPUS_VALIDATOR_SCHEMA = "sanskrit-bulk-corpus-validator.v1";
const STAGING_SCHEMA = "sanskrit-bulk-corpus-staging.v1";
const MAX_BULK_CORPUS_RECORDS = 2000;

const CORPUS_RECORD_TYPES = Object.freeze({
  DHATU: "dhatu",
  SUTRA: "sutra",
  STOTRA: "stotra"
});

const CORPUS_VALIDATOR_STATES = Object.freeze({
  EMPTY: "EMPTY",
  VALID: "VALID",
  INVALID: "INVALID",
  LIMIT_EXCEEDED: "LIMIT_EXCEEDED",
  REVIEW_ONLY: "REVIEW_ONLY"
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

function normalizeCorpusValidatorInput(input = {}) {
  return freeze({
    schemaVersion: String(input.schemaVersion || STAGING_SCHEMA),
    validatorSchemaVersion: CORPUS_VALIDATOR_SCHEMA,
    mode: String(input.mode || "preview-only"),
    canonicalWriteAllowed: false,
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    batches: freeze(asArray(input.batches)),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function normalizeCorpusRecord(record = {}) {
  return freeze({
    id: String(record.id || "").trim(),
    type: String(record.type || "").trim(),
    text: String(record.text || "").trim(),
    source: String(record.source || "").trim(),
    gana: String(record.gana || "").trim(),
    notes: String(record.notes || "").trim()
  });
}

module.exports = {
  CORPUS_VALIDATOR_SCHEMA,
  STAGING_SCHEMA,
  MAX_BULK_CORPUS_RECORDS,
  CORPUS_RECORD_TYPES,
  CORPUS_VALIDATOR_STATES,
  normalizeCorpusValidatorInput,
  normalizeCorpusRecord
};