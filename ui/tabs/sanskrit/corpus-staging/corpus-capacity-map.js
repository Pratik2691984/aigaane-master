"use strict";

const CORPUS_CAPACITY_SCHEMA = "sanskrit-bulk-corpus-capacity.v1";

const MAX_BULK_CORPUS_RECORDS = 2000;
const DEFAULT_CAPACITY_BATCH_SIZE = 250;

const CORPUS_CAPACITY_STATES = Object.freeze({
  EMPTY: "EMPTY",
  CAPACITY_READY: "CAPACITY_READY",
  CAPACITY_WARNING: "CAPACITY_WARNING",
  CAPACITY_EXCEEDED: "CAPACITY_EXCEEDED",
  CAPACITY_BLOCKED: "CAPACITY_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeCorpusCapacityInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_CAPACITY_SCHEMA,
    recordCount: asCount(input.recordCount),
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    remainingCapacity: asCount(input.remainingCapacity),
    utilizationPercent: Number(input.utilizationPercent || 0),
    defaultBatchSize: asCount(input.defaultBatchSize || DEFAULT_CAPACITY_BATCH_SIZE),
    projectedBatchCount: asCount(input.projectedBatchCount),
    execution: freeze(isObject(input.execution) ? input.execution : {}),
    previewOnly: true,
    readOnly: true,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusCapacityRecord(input = {}) {
  const normalized = normalizeCorpusCapacityInput(input);

  let state = CORPUS_CAPACITY_STATES.CAPACITY_READY;

  if (normalized.recordCount === 0) {
    state = CORPUS_CAPACITY_STATES.EMPTY;
  } else if (normalized.recordCount > MAX_BULK_CORPUS_RECORDS) {
    state = CORPUS_CAPACITY_STATES.CAPACITY_EXCEEDED;
  } else if (normalized.execution && normalized.execution.valid === false) {
    state = CORPUS_CAPACITY_STATES.CAPACITY_BLOCKED;
  } else if (normalized.utilizationPercent >= 90) {
    state = CORPUS_CAPACITY_STATES.CAPACITY_WARNING;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_CAPACITY_SCHEMA,
  CORPUS_CAPACITY_STATES,
  MAX_BULK_CORPUS_RECORDS,
  DEFAULT_CAPACITY_BATCH_SIZE,
  normalizeCorpusCapacityInput,
  buildCorpusCapacityRecord
};