"use strict";

const CORPUS_INTAKE_SCHEMA = "sanskrit-bulk-corpus-intake.v1";
const MAX_BULK_CORPUS_RECORDS = 2000;
const DEFAULT_INTAKE_BATCH_SIZE = 250;

const CORPUS_INTAKE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  INTAKE_READY: "INTAKE_READY",
  INTAKE_WARNING: "INTAKE_WARNING",
  INTAKE_BLOCKED: "INTAKE_BLOCKED"
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

function normalizeCorpusIntakeInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_INTAKE_SCHEMA,
    sourceRecordCount: asCount(input.sourceRecordCount),
    intakeRecordCount: asCount(input.intakeRecordCount),
    skippedRecordCount: asCount(input.skippedRecordCount),
    intakeBatchCount: asCount(input.intakeBatchCount),
    intakeBatches: freeze(asArray(input.intakeBatches)),
    skippedRecords: freeze(asArray(input.skippedRecords)),
    preview: freeze(isObject(input.preview) ? input.preview : {}),
    batchSize: asCount(input.batchSize || DEFAULT_INTAKE_BATCH_SIZE),
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusIntakeRecord(input = {}) {
  const normalized = normalizeCorpusIntakeInput(input);

  let state = CORPUS_INTAKE_STATES.INTAKE_READY;

  if (
    normalized.sourceRecordCount > MAX_BULK_CORPUS_RECORDS ||
    normalized.preview.valid === false
  ) {
    state = CORPUS_INTAKE_STATES.INTAKE_BLOCKED;
  } else if (normalized.skippedRecordCount > 0) {
    state = CORPUS_INTAKE_STATES.INTAKE_WARNING;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_INTAKE_SCHEMA,
  CORPUS_INTAKE_STATES,
  MAX_BULK_CORPUS_RECORDS,
  DEFAULT_INTAKE_BATCH_SIZE,
  normalizeCorpusIntakeInput,
  buildCorpusIntakeRecord
};