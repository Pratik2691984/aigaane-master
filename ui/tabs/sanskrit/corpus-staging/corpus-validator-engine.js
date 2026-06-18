"use strict";

const {
  STAGING_SCHEMA,
  MAX_BULK_CORPUS_RECORDS,
  CORPUS_RECORD_TYPES,
  CORPUS_VALIDATOR_STATES,
  normalizeCorpusValidatorInput,
  normalizeCorpusRecord
} = require("./corpus-validator-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function allowedRecordTypes() {
  return freeze(Object.values(CORPUS_RECORD_TYPES));
}

function collectCorpusRecords(input = {}) {
  const manifest = normalizeCorpusValidatorInput(input);
  const records = [];

  manifest.batches.forEach((batch, batchIndex) => {
    const batchId = String(batch.batchId || "batch-" + batchIndex);
    const batchRecords = Array.isArray(batch.records) ? batch.records : [];

    batchRecords.forEach((record, recordIndex) => {
      records.push({
        batchId,
        recordIndex,
        ...normalizeCorpusRecord(record)
      });
    });
  });

  return freeze(records);
}

function findDuplicateRecordIds(records = []) {
  const seen = new Set();
  const duplicates = new Set();

  records.forEach((record) => {
    if (!record.id) return;
    if (seen.has(record.id)) {
      duplicates.add(record.id);
    }
    seen.add(record.id);
  });

  return freeze(Array.from(duplicates));
}

function validateCorpusRecord(record = {}) {
  const errors = [];
  const prefix = String(record.batchId || "batch") + ":" + String(record.recordIndex || 0);

  if (!record.id) {
    errors.push(prefix + ":missingId");
  }

  if (!allowedRecordTypes().includes(record.type)) {
    errors.push(prefix + ":invalidType");
  }

  if (!record.text) {
    errors.push(prefix + ":missingText");
  }

  if (!record.source) {
    errors.push(prefix + ":missingSource");
  }

  return freeze(errors);
}

function validateBulkCorpusManifest(input = {}) {
  const manifest = normalizeCorpusValidatorInput(input);
  const records = collectCorpusRecords(manifest);
  const duplicateIds = findDuplicateRecordIds(records);
  const errors = [];

  if (manifest.schemaVersion !== STAGING_SCHEMA) {
    errors.push("schemaVersion");
  }

  if (manifest.mode !== "preview-only") {
    errors.push("mode");
  }

  if (manifest.canonicalWriteAllowed !== false) {
    errors.push("canonicalWriteAllowed");
  }

  if (records.length > MAX_BULK_CORPUS_RECORDS) {
    errors.push("recordLimitExceeded");
  }

  records.forEach((record) => {
    errors.push(...validateCorpusRecord(record));
  });

  if (duplicateIds.length) {
    errors.push("duplicateRecordIds");
  }

  const readinessScore = errors.length
    ? Math.max(0, 100 - errors.length * 5)
    : 100;

  return freeze({
    state: errors.length
      ? (records.length > MAX_BULK_CORPUS_RECORDS
        ? CORPUS_VALIDATOR_STATES.LIMIT_EXCEEDED
        : CORPUS_VALIDATOR_STATES.INVALID)
      : CORPUS_VALIDATOR_STATES.VALID,
    valid: errors.length === 0,
    errors,
    duplicateIds,
    recordCount: records.length,
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    readinessScore,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false
  });
}

module.exports = {
  allowedRecordTypes,
  collectCorpusRecords,
  findDuplicateRecordIds,
  validateCorpusRecord,
  validateBulkCorpusManifest
};