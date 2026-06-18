"use strict";

const CORPUS_WINDOW_SCHEMA = "sanskrit-bulk-corpus-window.v1";

const DEFAULT_CORPUS_WINDOW_SIZE = 250;

const CORPUS_WINDOW_STATES = Object.freeze({
  EMPTY: "EMPTY",
  WINDOW_READY: "WINDOW_READY",
  WINDOW_BLOCKED: "WINDOW_BLOCKED"
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

function normalizeCorpusWindowInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_WINDOW_SCHEMA,
    windowSize: asCount(input.windowSize || DEFAULT_CORPUS_WINDOW_SIZE),
    windowCount: asCount(input.windowCount),
    totalReserved: asCount(input.totalReserved),
    windows: freeze(asArray(input.windows)),
    reservation: freeze(isObject(input.reservation) ? input.reservation : {}),
    previewOnly: true,
    readOnly: true,
    windowExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusWindowRecord(input = {}) {
  const normalized = normalizeCorpusWindowInput(input);

  let state = CORPUS_WINDOW_STATES.WINDOW_READY;

  if (normalized.totalReserved === 0 || normalized.windowCount === 0) {
    state = CORPUS_WINDOW_STATES.EMPTY;
  }

  if (normalized.reservation && normalized.reservation.valid === false) {
    state = CORPUS_WINDOW_STATES.WINDOW_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_WINDOW_SCHEMA,
  CORPUS_WINDOW_STATES,
  DEFAULT_CORPUS_WINDOW_SIZE,
  normalizeCorpusWindowInput,
  buildCorpusWindowRecord
};