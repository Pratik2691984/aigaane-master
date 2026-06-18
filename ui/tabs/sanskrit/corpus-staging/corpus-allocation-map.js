"use strict";

const CORPUS_ALLOCATION_SCHEMA = "sanskrit-bulk-corpus-allocation.v1";

const MAX_BULK_CORPUS_RECORDS = 2000;

const DEFAULT_CORPUS_ALLOCATION = Object.freeze({
  dhatu: 1400,
  sutra: 400,
  stotra: 200
});

const CORPUS_ALLOCATION_STATES = Object.freeze({
  EMPTY: "EMPTY",
  ALLOCATION_READY: "ALLOCATION_READY",
  ALLOCATION_WARNING: "ALLOCATION_WARNING",
  ALLOCATION_BLOCKED: "ALLOCATION_BLOCKED"
});

function freeze(v) {
  return Object.freeze(v);
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function normalizeCorpusAllocationInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_ALLOCATION_SCHEMA,
    allocation: freeze(isObject(input.allocation) ? input.allocation : {}),
    typeCounts: freeze(isObject(input.typeCounts)
      ? input.typeCounts
      : { dhatu: 0, sutra: 0, stotra: 0 }),
    totalReserved: asCount(input.totalReserved),
    totalUsed: asCount(input.totalUsed),
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    freeCapacity: asCount(input.freeCapacity),
    warnings: freeze(asArray(input.warnings)),
    errors: freeze(asArray(input.errors)),
    capacity: freeze(isObject(input.capacity) ? input.capacity : {}),
    previewOnly: true,
    readOnly: true,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false,
    allocationWriteAllowed: false
  });
}

function buildCorpusAllocationRecord(input = {}) {
  const normalized = normalizeCorpusAllocationInput(input);

  let state = CORPUS_ALLOCATION_STATES.ALLOCATION_READY;

  if (normalized.totalUsed === 0) {
    state = CORPUS_ALLOCATION_STATES.EMPTY;
  }

  if (
    normalized.errors.length ||
    (normalized.capacity && normalized.capacity.valid === false)
  ) {
    state = CORPUS_ALLOCATION_STATES.ALLOCATION_BLOCKED;
  } else if (normalized.warnings.length) {
    state = CORPUS_ALLOCATION_STATES.ALLOCATION_WARNING;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_ALLOCATION_SCHEMA,
  CORPUS_ALLOCATION_STATES,
  MAX_BULK_CORPUS_RECORDS,
  DEFAULT_CORPUS_ALLOCATION,
  normalizeCorpusAllocationInput,
  buildCorpusAllocationRecord
};