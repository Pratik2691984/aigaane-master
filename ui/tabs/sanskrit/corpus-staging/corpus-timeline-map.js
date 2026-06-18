"use strict";

const CORPUS_TIMELINE_SCHEMA = "sanskrit-bulk-corpus-timeline.v1";

const CORPUS_TIMELINE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  TIMELINE_READY: "TIMELINE_READY",
  TIMELINE_BLOCKED: "TIMELINE_BLOCKED"
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

function normalizeCorpusTimelineInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_TIMELINE_SCHEMA,
    timelineCount: asCount(input.timelineCount),
    timeline: freeze(asArray(input.timeline)),
    totalEstimatedSeconds: Number(input.totalEstimatedSeconds || 0),
    finalCompletionPercent: Number(input.finalCompletionPercent || 0),
    schedulePlan: freeze(isObject(input.schedulePlan) ? input.schedulePlan : {}),
    previewOnly: true,
    readOnly: true,
    timelineExecutionAllowed: false,
    scheduleExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusTimelineRecord(input = {}) {
  const normalized = normalizeCorpusTimelineInput(input);

  let state = CORPUS_TIMELINE_STATES.TIMELINE_READY;

  if (normalized.timelineCount === 0) {
    state = CORPUS_TIMELINE_STATES.EMPTY;
  }

  if (normalized.schedulePlan && normalized.schedulePlan.valid === false) {
    state = CORPUS_TIMELINE_STATES.TIMELINE_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_TIMELINE_SCHEMA,
  CORPUS_TIMELINE_STATES,
  normalizeCorpusTimelineInput,
  buildCorpusTimelineRecord
};