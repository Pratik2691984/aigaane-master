"use strict";

const CORPUS_ADMISSION_SCHEMA = "sanskrit-bulk-corpus-admission.v1";

const CORPUS_ADMISSION_STATES = Object.freeze({
  EMPTY: "EMPTY",
  ADMISSION_READY: "ADMISSION_READY",
  ADMISSION_BLOCKED: "ADMISSION_BLOCKED"
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

function normalizeCorpusAdmissionInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_ADMISSION_SCHEMA,
    admissionStatus: String(input.admissionStatus || "admission-ready"),
    acceptedRecordCount: asCount(input.acceptedRecordCount),
    rejectedRecordCount: asCount(input.rejectedRecordCount),
    admissionReasons: freeze(asArray(input.admissionReasons)),
    rejectionReasons: freeze(asArray(input.rejectionReasons)),
    forecast: freeze(isObject(input.forecast) ? input.forecast : {}),
    previewOnly: true,
    readOnly: true,
    admissionExecutionAllowed: false,
    forecastExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusAdmissionRecord(input = {}) {
  const normalized = normalizeCorpusAdmissionInput(input);

  let state = CORPUS_ADMISSION_STATES.ADMISSION_READY;

  if (normalized.acceptedRecordCount === 0) {
    state = CORPUS_ADMISSION_STATES.EMPTY;
  }

  if (normalized.forecast && normalized.forecast.valid === false) {
    state = CORPUS_ADMISSION_STATES.ADMISSION_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_ADMISSION_SCHEMA,
  CORPUS_ADMISSION_STATES,
  normalizeCorpusAdmissionInput,
  buildCorpusAdmissionRecord
};