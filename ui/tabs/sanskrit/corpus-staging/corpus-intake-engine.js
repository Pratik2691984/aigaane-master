"use strict";

const {
  buildCorpusIntakeRecord,
  DEFAULT_INTAKE_BATCH_SIZE,
  MAX_BULK_CORPUS_RECORDS
} = require("./corpus-intake-map.js");

const {
  summarizeCorpusImportPreview
} = require("./corpus-import-preview-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function collectIntakeSourceRecords(input = {}) {
  const records = [];

  (Array.isArray(input.batches) ? input.batches : []).forEach((batch, batchIndex) => {
    const sourceBatchId = String(batch.batchId || "batch-" + batchIndex);
    const batchRecords = Array.isArray(batch.records) ? batch.records : [];

    batchRecords.forEach((record, recordIndex) => {
      if (record && typeof record === "object" && !Array.isArray(record)) {
        records.push({
          sourceBatchId,
          sourceRecordIndex: recordIndex,
          record
        });
      }
    });
  });

  return freeze(records);
}

function buildIntakeItems(input = {}) {
  const sourceRecords = collectIntakeSourceRecords(input);
  const seen = new Set();
  const intakeRecords = [];
  const skippedRecords = [];

  sourceRecords.forEach((item, index) => {
    const recordId = String(item.record.id || "").trim();
    const intake = {
      intakeId: "intake-" + String(index + 1).padStart(4, "0"),
      sourceBatchId: item.sourceBatchId,
      sourceRecordIndex: item.sourceRecordIndex,
      recordId,
      type: String(item.record.type || "").trim(),
      previewOnly: true
    };

    if (!recordId) {
      skippedRecords.push({
        ...intake,
        skipReason: "missingId"
      });
      return;
    }

    if (seen.has(recordId)) {
      skippedRecords.push({
        ...intake,
        skipReason: "duplicateId"
      });
      return;
    }

    seen.add(recordId);
    intakeRecords.push(intake);
  });

  return freeze({
    sourceRecordCount: sourceRecords.length,
    intakeRecords: freeze(intakeRecords),
    skippedRecords: freeze(skippedRecords)
  });
}

function partitionIntakeRecords(records = [], batchSize = DEFAULT_INTAKE_BATCH_SIZE) {
  const batches = [];
  const safeBatchSize = Math.max(1, Number(batchSize || DEFAULT_INTAKE_BATCH_SIZE));

  for (let start = 0; start < records.length; start += safeBatchSize) {
    const part = records.slice(start, start + safeBatchSize);
    batches.push({
      intakeBatchId: "intake-batch-" + String(batches.length + 1).padStart(3, "0"),
      startIndex: start,
      recordCount: part.length,
      records: part
    });
  }

  return freeze(batches);
}

function prepareCorpusIntake(input = {}, batchSize = DEFAULT_INTAKE_BATCH_SIZE) {
  const preview = summarizeCorpusImportPreview(input);
  const items = buildIntakeItems(input);
  const intakeBatches = partitionIntakeRecords(items.intakeRecords, batchSize);

  return buildCorpusIntakeRecord({
    sourceRecordCount: items.sourceRecordCount,
    intakeRecordCount: items.intakeRecords.length,
    skippedRecordCount: items.skippedRecords.length,
    intakeBatchCount: intakeBatches.length,
    intakeBatches,
    skippedRecords: items.skippedRecords,
    preview,
    batchSize,
    maxRecords: MAX_BULK_CORPUS_RECORDS
  });
}

function summarizeCorpusIntake(input = {}, batchSize = DEFAULT_INTAKE_BATCH_SIZE) {
  const intake = prepareCorpusIntake(input, batchSize);

  return freeze({
    state: intake.state,
    valid: intake.state !== "INTAKE_BLOCKED",
    sourceRecordCount: intake.sourceRecordCount,
    intakeRecordCount: intake.intakeRecordCount,
    skippedRecordCount: intake.skippedRecordCount,
    intakeBatchCount: intake.intakeBatchCount,
    batchSize: intake.batchSize,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  collectIntakeSourceRecords,
  buildIntakeItems,
  partitionIntakeRecords,
  prepareCorpusIntake,
  summarizeCorpusIntake
};