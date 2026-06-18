"use strict";

const CORPUS_SCHEDULE_SCHEMA = "sanskrit-bulk-corpus-schedule.v1";

const DEFAULT_SECONDS_PER_WINDOW = 12.5;

const CORPUS_SCHEDULE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  SCHEDULE_READY: "SCHEDULE_READY",
  SCHEDULE_BLOCKED: "SCHEDULE_BLOCKED"
});

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

function normalizeCorpusScheduleInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_SCHEDULE_SCHEMA,
    scheduleCount: asCount(input.scheduleCount),
    schedule: freeze(asArray(input.schedule)),
    totalEstimatedSeconds: Number(input.totalEstimatedSeconds || 0),
    secondsPerWindow: Number(input.secondsPerWindow || DEFAULT_SECONDS_PER_WINDOW),
    windowPlan: freeze(isObject(input.windowPlan) ? input.windowPlan : {}),
    previewOnly: true,
    readOnly: true,
    scheduleExecutionAllowed: false,
    windowExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusScheduleRecord(input = {}) {
  const normalized = normalizeCorpusScheduleInput(input);

  let state = CORPUS_SCHEDULE_STATES.SCHEDULE_READY;

  if (normalized.scheduleCount === 0) {
    state = CORPUS_SCHEDULE_STATES.EMPTY;
  }

  if (normalized.windowPlan && normalized.windowPlan.valid === false) {
    state = CORPUS_SCHEDULE_STATES.SCHEDULE_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_SCHEDULE_SCHEMA,
  CORPUS_SCHEDULE_STATES,
  DEFAULT_SECONDS_PER_WINDOW,
  normalizeCorpusScheduleInput,
  buildCorpusScheduleRecord
};