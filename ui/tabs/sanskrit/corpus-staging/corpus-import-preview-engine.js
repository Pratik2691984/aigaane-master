"use strict";

const {
  buildCorpusImportPreviewRecord
} = require("./corpus-import-preview-map.js");

const {
  summarizeCorpusReadiness
} = require("./corpus-readiness-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function collectImportPreviewRecords(input = {}) {
  const records = [];

  for (const batch of Array.isArray(input.batches) ? input.batches : []) {
    for (const record of Array.isArray(batch.records) ? batch.records : []) {
      if (record && typeof record === "object" && !Array.isArray(record)) {
        records.push(record);
      }
    }
  }

  return freeze(records);
}

function estimateRecordBytes(record = {}) {
  return Buffer.byteLength(
    JSON.stringify(record),
    "utf8"
  );
}

function previewCorpusImport(input = {}) {
  const readiness = summarizeCorpusReadiness(input);
  const records = collectImportPreviewRecords(input);

  const seen = new Set();
  const duplicateIds = new Set();

  const typeCounts = {
    dhatu: 0,
    sutra: 0,
    stotra: 0
  };

  let estimatedInsertCount = 0;
  let estimatedSkipCount = 0;
  let estimatedBytes = 0;

  records.forEach((record) => {
    const id = String(record.id || "").trim();
    const type = String(record.type || "").trim();

    estimatedBytes += estimateRecordBytes(record);

    if (Object.prototype.hasOwnProperty.call(typeCounts, type)) {
      typeCounts[type] += 1;
    }

    if (!id) {
      estimatedSkipCount += 1;
      return;
    }

    if (seen.has(id)) {
      duplicateIds.add(id);
      estimatedSkipCount += 1;
      return;
    }

    seen.add(id);
    estimatedInsertCount += 1;
  });

  return buildCorpusImportPreviewRecord({
    recordCount: records.length,
    estimatedInsertCount,
    estimatedSkipCount,
    duplicateIds: Array.from(duplicateIds).sort(),
    typeCounts,
    estimatedBytes,
    readiness
  });
}

function summarizeCorpusImportPreview(input = {}) {
  const preview = previewCorpusImport(input);

  return freeze({
    state: preview.state,
    valid: preview.state !== "IMPORT_PREVIEW_BLOCKED",
    recordCount: preview.recordCount,
    estimatedInsertCount: preview.estimatedInsertCount,
    estimatedSkipCount: preview.estimatedSkipCount,
    duplicateIds: preview.duplicateIds,
    typeCounts: preview.typeCounts,
    estimatedBytes: preview.estimatedBytes,
    estimatedKilobytes: Math.round((preview.estimatedBytes / 1024) * 1000) / 1000,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  collectImportPreviewRecords,
  estimateRecordBytes,
  previewCorpusImport,
  summarizeCorpusImportPreview
};