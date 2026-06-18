"use strict";

const {
  buildCorpusIntakeQueueRecord,
  DEFAULT_SECONDS_PER_RECORD
} = require("./corpus-intake-queue-map.js");

const {
  prepareCorpusIntake
} = require("./corpus-intake-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function buildQueueItemsFromIntake(intake = {}) {
  const queueItems = [];
  let sequence = 0;

  const intakeBatches = Array.isArray(intake.intakeBatches)
    ? intake.intakeBatches
    : [];

  intakeBatches.forEach((batch) => {
    const records = Array.isArray(batch.records) ? batch.records : [];

    records.forEach((record) => {
      sequence += 1;
      queueItems.push({
        queueId: "queue-" + String(sequence).padStart(4, "0"),
        queueOrder: sequence,
        intakeBatchId: String(batch.intakeBatchId || ""),
        intakeId: String(record.intakeId || ""),
        recordId: String(record.recordId || ""),
        type: String(record.type || ""),
        previewOnly: true
      });
    });
  });

  return freeze(queueItems);
}

function estimateQueueSeconds(queueItems = [], secondsPerRecord = DEFAULT_SECONDS_PER_RECORD) {
  return Math.round(queueItems.length * Number(secondsPerRecord || 0) * 1000) / 1000;
}

function buildCorpusIntakeQueue(input = {}, batchSize = 250) {
  const intake = prepareCorpusIntake(input, batchSize);
  const queueItems = buildQueueItemsFromIntake(intake);
  const estimatedSeconds = estimateQueueSeconds(queueItems);

  return buildCorpusIntakeQueueRecord({
    queueItemCount: queueItems.length,
    queueItems,
    intake,
    estimatedSeconds,
    secondsPerRecord: DEFAULT_SECONDS_PER_RECORD
  });
}

function summarizeCorpusIntakeQueue(input = {}, batchSize = 250) {
  const queue = buildCorpusIntakeQueue(input, batchSize);

  return freeze({
    state: queue.state,
    valid: queue.state !== "QUEUE_BLOCKED",
    queueItemCount: queue.queueItemCount,
    estimatedSeconds: queue.estimatedSeconds,
    secondsPerRecord: queue.secondsPerRecord,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false,
    queueExecutionAllowed: false
  });
}

module.exports = {
  buildQueueItemsFromIntake,
  estimateQueueSeconds,
  buildCorpusIntakeQueue,
  summarizeCorpusIntakeQueue
};