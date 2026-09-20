"use strict";

const CORPUS_INTAKE_QUEUE_SCHEMA = "sanskrit-bulk-corpus-intake-queue.v1";

const CORPUS_INTAKE_QUEUE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  QUEUE_READY: "QUEUE_READY",
  QUEUE_WARNING: "QUEUE_WARNING",
  QUEUE_BLOCKED: "QUEUE_BLOCKED"
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

function normalizeCorpusIntakeQueueInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_INTAKE_QUEUE_SCHEMA,
    queueItemCount: asCount(input.queueItemCount),
    queueItems: freeze(asArray(input.queueItems)),
    intake: freeze(isObject(input.intake) ? input.intake : {}),
    estimatedSeconds: Number(input.estimatedSeconds || 0),
    secondsPerRecord: Number(input.secondsPerRecord || DEFAULT_SECONDS_PER_RECORD),
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false,
    queueExecutionAllowed: false
  });
}

function buildCorpusIntakeQueueRecord(input = {}) {
  const normalized = normalizeCorpusIntakeQueueInput(input);

  let state = CORPUS_INTAKE_QUEUE_STATES.QUEUE_READY;

  if (normalized.intake && normalized.intake.valid === false) {
    state = CORPUS_INTAKE_QUEUE_STATES.QUEUE_BLOCKED;
  } else if (
    normalized.intake &&
    Number(normalized.intake.skippedRecordCount || 0) > 0
  ) {
    state = CORPUS_INTAKE_QUEUE_STATES.QUEUE_WARNING;
  }

  if (normalized.queueItemCount === 0) {
    state = CORPUS_INTAKE_QUEUE_STATES.EMPTY;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_INTAKE_QUEUE_SCHEMA,
  CORPUS_INTAKE_QUEUE_STATES,
  DEFAULT_SECONDS_PER_RECORD,
  normalizeCorpusIntakeQueueInput,
  buildCorpusIntakeQueueRecord
};