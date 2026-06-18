"use strict";

const {
  buildCorpusStagingManifest,
  MAX_BULK_CORPUS_RECORDS
} = require("./corpus-staging-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function collectCorpusRecordIds(manifest = {}) {
  const ids = [];

  for (const batch of Array.isArray(manifest.batches) ? manifest.batches : []) {
    for (const record of Array.isArray(batch.records) ? batch.records : []) {
      ids.push(String(record.id || ""));
    }
  }

  return freeze(ids.filter(Boolean));
}

function findDuplicateCorpusRecordIds(manifest = {}) {
  const seen = new Set();
  const duplicates = new Set();

  for (const id of collectCorpusRecordIds(manifest)) {
    if (seen.has(id)) {
      duplicates.add(id);
    }
    seen.add(id);
  }

  return freeze(Array.from(duplicates));
}

function inspectCorpusStagingManifest(input = {}) {
  const manifest = buildCorpusStagingManifest(input);
  const duplicateIds = findDuplicateCorpusRecordIds(manifest);
  const errors = [];

  if (manifest.schemaVersion !== "sanskrit-bulk-corpus-staging.v1") {
    errors.push("schemaVersion");
  }

  if (manifest.mode !== "preview-only") {
    errors.push("mode");
  }

  if (manifest.canonicalWriteAllowed !== false) {
    errors.push("canonicalWriteAllowed");
  }

  if (manifest.recordCount > MAX_BULK_CORPUS_RECORDS) {
    errors.push("recordLimitExceeded");
  }

  if (duplicateIds.length) {
    errors.push("duplicateRecordIds");
  }

  return freeze({
    valid: errors.length === 0,
    errors,
    duplicateIds,
    batchCount: manifest.batchCount,
    recordCount: manifest.recordCount,
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false
  });
}

function createCorpusStagingPreview(input = {}) {
  const manifest = buildCorpusStagingManifest(input);
  const inspection = inspectCorpusStagingManifest(manifest);

  return freeze({
    title: "Sanskrit Bulk Corpus Staging",
    state: manifest.state,
    valid: inspection.valid,
    batchCount: inspection.batchCount,
    recordCount: inspection.recordCount,
    duplicateIds: inspection.duplicateIds,
    errors: inspection.errors,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false
  });
}

module.exports = {
  collectCorpusRecordIds,
  findDuplicateCorpusRecordIds,
  inspectCorpusStagingManifest,
  createCorpusStagingPreview
};