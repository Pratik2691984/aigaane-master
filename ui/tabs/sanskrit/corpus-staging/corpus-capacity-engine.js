"use strict";

const {
  buildCorpusCapacityRecord,
  MAX_BULK_CORPUS_RECORDS,
  DEFAULT_CAPACITY_BATCH_SIZE
} = require("./corpus-capacity-map.js");

const {
  summarizeCorpusExecutionPreview
} = require("./corpus-execution-preview-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function computeProjectedBatchCount(recordCount = 0, batchSize = DEFAULT_CAPACITY_BATCH_SIZE) {
  const safeRecordCount = Math.max(0, Number(recordCount || 0));
  const safeBatchSize = Math.max(1, Number(batchSize || DEFAULT_CAPACITY_BATCH_SIZE));

  return safeRecordCount
    ? Math.ceil(safeRecordCount / safeBatchSize)
    : 0;
}

function computeUtilizationPercent(recordCount = 0, maxRecords = MAX_BULK_CORPUS_RECORDS) {
  const safeMax = Math.max(1, Number(maxRecords || MAX_BULK_CORPUS_RECORDS));
  return Math.round((Number(recordCount || 0) / safeMax) * 100000) / 1000;
}

function planCorpusCapacity(input = {}, batchSize = DEFAULT_CAPACITY_BATCH_SIZE) {
  const execution = summarizeCorpusExecutionPreview(input, batchSize);
  const recordCount = Number(execution.queueItemCount || 0);
  const remainingCapacity = Math.max(0, MAX_BULK_CORPUS_RECORDS - recordCount);
  const utilizationPercent = computeUtilizationPercent(recordCount);

  return buildCorpusCapacityRecord({
    recordCount,
    maxRecords: MAX_BULK_CORPUS_RECORDS,
    remainingCapacity,
    utilizationPercent,
    defaultBatchSize: batchSize,
    projectedBatchCount: computeProjectedBatchCount(recordCount, batchSize),
    execution
  });
}

function summarizeCorpusCapacity(input = {}, batchSize = DEFAULT_CAPACITY_BATCH_SIZE) {
  const capacity = planCorpusCapacity(input, batchSize);

  return freeze({
    state: capacity.state,
    valid: !["CAPACITY_EXCEEDED", "CAPACITY_BLOCKED"].includes(capacity.state),
    recordCount: capacity.recordCount,
    maxRecords: capacity.maxRecords,
    remainingCapacity: capacity.remainingCapacity,
    utilizationPercent: capacity.utilizationPercent,
    defaultBatchSize: capacity.defaultBatchSize,
    projectedBatchCount: capacity.projectedBatchCount,
    previewOnly: true,
    readOnly: true,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  computeProjectedBatchCount,
  computeUtilizationPercent,
  planCorpusCapacity,
  summarizeCorpusCapacity
};