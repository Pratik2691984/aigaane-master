"use strict";

const CORPUS_EXECUTION_PREVIEW_SCHEMA =
  "sanskrit-bulk-corpus-execution-preview.v1";

const CORPUS_EXECUTION_PREVIEW_STATES = Object.freeze({
  EMPTY: "EMPTY",
  EXECUTION_PREVIEW_READY: "EXECUTION_PREVIEW_READY",
  EXECUTION_PREVIEW_BLOCKED: "EXECUTION_PREVIEW_BLOCKED"
});

const DEFAULT_SECONDS_PER_RECORD = 0.05;

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

function normalizeCorpusExecutionPreviewInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_EXECUTION_PREVIEW_SCHEMA,
    queueItemCount: asCount(input.queueItemCount),
    timeline: freeze(asArray(input.timeline)),
    estimatedSeconds: Number(input.estimatedSeconds || 0),
    estimatedThroughputPerSecond: Number(input.estimatedThroughputPerSecond || 0),
    queue: freeze(isObject(input.queue) ? input.queue : {}),
    previewOnly: true,
    readOnly: true,
    executionAllowed: false,
    queueExecutionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusExecutionPreviewRecord(input = {}) {
  const normalized = normalizeCorpusExecutionPreviewInput(input);

  let state = CORPUS_EXECUTION_PREVIEW_STATES.EXECUTION_PREVIEW_READY;

  if (normalized.queue && normalized.queue.valid === false) {
    state = CORPUS_EXECUTION_PREVIEW_STATES.EXECUTION_PREVIEW_BLOCKED;
  }

  if (normalized.queueItemCount === 0) {
    state = CORPUS_EXECUTION_PREVIEW_STATES.EMPTY;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_EXECUTION_PREVIEW_SCHEMA,
  CORPUS_EXECUTION_PREVIEW_STATES,
  DEFAULT_SECONDS_PER_RECORD,
  normalizeCorpusExecutionPreviewInput,
  buildCorpusExecutionPreviewRecord
};