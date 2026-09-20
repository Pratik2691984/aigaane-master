"use strict";

const {
  buildCorpusExecutionPreviewRecord,
  DEFAULT_SECONDS_PER_RECORD
} = require("./corpus-execution-preview-map.js");

const {
  buildCorpusIntakeQueue
} = require("./corpus-intake-queue-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function buildExecutionTimeline(queueItems = [], secondsPerRecord = DEFAULT_SECONDS_PER_RECORD) {
  let elapsed = 0;

  const timeline = queueItems.map((item) => {
    const startSecond = Math.round(elapsed * 1000) / 1000;
    elapsed += Number(secondsPerRecord || DEFAULT_SECONDS_PER_RECORD);
    const endSecond = Math.round(elapsed * 1000) / 1000;

    return {
      queueId: String(item.queueId || ""),
      queueOrder: Number(item.queueOrder || 0),
      recordId: String(item.recordId || ""),
      type: String(item.type || ""),
      startSecond,
      endSecond,
      previewOnly: true
    };
  });

  return freeze(timeline);
}

function estimateExecutionThroughput(queueItemCount = 0, estimatedSeconds = 0) {
  if (!estimatedSeconds) return 0;
  return Math.round((Number(queueItemCount || 0) / estimatedSeconds) * 1000) / 1000;
}

function previewCorpusExecution(input = {}, batchSize = 250) {
  const queue = buildCorpusIntakeQueue(input, batchSize);
  const queueItems = Array.isArray(queue.queueItems) ? queue.queueItems : [];
  const timeline = buildExecutionTimeline(queueItems);
  const estimatedSeconds = timeline.length
    ? timeline[timeline.length - 1].endSecond
    : 0;

  return buildCorpusExecutionPreviewRecord({
    queueItemCount: queueItems.length,
    timeline,
    estimatedSeconds,
    estimatedThroughputPerSecond: estimateExecutionThroughput(
      queueItems.length,
      estimatedSeconds
    ),
    queue
  });
}

function summarizeCorpusExecutionPreview(input = {}, batchSize = 250) {
  const preview = previewCorpusExecution(input, batchSize);

  return freeze({
    state: preview.state,
    valid: preview.state !== "EXECUTION_PREVIEW_BLOCKED",
    queueItemCount: preview.queueItemCount,
    estimatedSeconds: preview.estimatedSeconds,
    estimatedThroughputPerSecond: preview.estimatedThroughputPerSecond,
    previewOnly: true,
    readOnly: true,
    executionAllowed: false,
    queueExecutionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  buildExecutionTimeline,
  estimateExecutionThroughput,
  previewCorpusExecution,
  summarizeCorpusExecutionPreview
};