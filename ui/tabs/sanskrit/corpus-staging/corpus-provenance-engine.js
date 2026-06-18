"use strict";

const {
  STAGING_SCHEMA,
  MAX_BULK_CORPUS_RECORDS,
  CORPUS_RECORD_TYPES,
  CORPUS_PROVENANCE_STATES,
  normalizeCorpusProvenanceInput,
  normalizeCorpusProvenanceRecord
} = require("./corpus-provenance-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function allowedRecordTypes() {
  return freeze(Object.values(CORPUS_RECORD_TYPES));
}

function collectProvenanceRecords(input = {}) {
  const manifest = normalizeCorpusProvenanceInput(input);
  const records = [];

  manifest.batches.forEach((batch, batchIndex) => {
    const batchId = String(batch.batchId || "batch-" + batchIndex);
    const batchSource = String(batch.source || "").trim();
    const batchLineage = String(batch.lineage || batchId).trim();
    const batchRecords = Array.isArray(batch.records) ? batch.records : [];

    batchRecords.forEach((record, recordIndex) => {
      const normalizedRecord = normalizeCorpusProvenanceRecord(record);

records.push({
  batchId,
  batchIndex,
  recordIndex,
  batchSource,
  ...normalizedRecord,
  batchLineage: normalizedRecord.batchLineage || batchLineage
});
    });
  });

  return freeze(records);
}

function duplicates(values = []) {
  const seen = new Set();
  const duplicate = new Set();

  values.forEach((value) => {
    if (!value) return;
    if (seen.has(value)) duplicate.add(value);
    seen.add(value);
  });

  return freeze(Array.from(duplicate).sort());
}

function countTypes(records = []) {
  const counts = {
    dhatu: 0,
    sutra: 0,
    stotra: 0
  };

  records.forEach((record) => {
    if (Object.prototype.hasOwnProperty.call(counts, record.type)) {
      counts[record.type] += 1;
    }
  });

  return freeze(counts);
}

function auditCorpusProvenanceManifest(input = {}) {
  const manifest = normalizeCorpusProvenanceInput(input);
  const records = collectProvenanceRecords(manifest);
  const errors = [];
  const warnings = [];

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

  const batchIds = manifest.batches.map((batch, index) =>
    String(batch.batchId || "batch-" + index)
  );
  const duplicateBatchIds = duplicates(batchIds);
  const duplicateRecordIds = duplicates(records.map((record) => record.id));
  const reusedSources = duplicates(records.map((record) => record.source));

  records.forEach((record) => {
    const prefix = record.batchId + ":" + record.recordIndex;

    if (!record.id) errors.push(prefix + ":missingId");
    if (!allowedRecordTypes().includes(record.type)) {
      errors.push(prefix + ":invalidType");
    }
    if (!record.text) errors.push(prefix + ":missingText");
    if (!record.source) errors.push(prefix + ":missingSource");
    if (!record.batchLineage) warnings.push(prefix + ":missingBatchLineage");
  });

  if (duplicateBatchIds.length) errors.push("duplicateBatchIds");
  if (duplicateRecordIds.length) errors.push("duplicateRecordIds");
  if (reusedSources.length) warnings.push("reusedSources");

  const confidenceScore = Math.max(
    0,
    100 - errors.length * 7 - warnings.length * 3
  );

  let state = CORPUS_PROVENANCE_STATES.PROVENANCE_READY;
  if (records.length > MAX_BULK_CORPUS_RECORDS) {
    state = CORPUS_PROVENANCE_STATES.LIMIT_EXCEEDED;
  } else if (errors.length) {
    state = CORPUS_PROVENANCE_STATES.PROVENANCE_INVALID;
  } else if (warnings.length) {
    state = CORPUS_PROVENANCE_STATES.PROVENANCE_WARNING;
  }

  return freeze({
    state,
    valid: errors.length === 0,
    errors,
    warnings,
    duplicateRecordIds,
    duplicateBatchIds,
    reusedSources,
    recordCount: records.length,
    batchCount: manifest.batches.length,
    typeCounts: countTypes(records),
    confidenceScore,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false
  });
}

module.exports = {
  allowedRecordTypes,
  collectProvenanceRecords,
  duplicates,
  countTypes,
  auditCorpusProvenanceManifest
};