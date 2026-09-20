"use strict";

const CORPUS_IMPORT_PREVIEW_SCHEMA =
  "sanskrit-bulk-corpus-import-preview.v1";

const CORPUS_IMPORT_PREVIEW_STATES = Object.freeze({
  EMPTY: "EMPTY",
  IMPORT_PREVIEW_READY: "IMPORT_PREVIEW_READY",
  IMPORT_PREVIEW_BLOCKED: "IMPORT_PREVIEW_BLOCKED",
  IMPORT_PREVIEW_WARNING: "IMPORT_PREVIEW_WARNING"
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

function normalizeCorpusImportPreviewInput(input = {}) {
  return freeze({
    schemaVersion: CORPUS_IMPORT_PREVIEW_SCHEMA,
    recordCount: asCount(input.recordCount),
    estimatedInsertCount: asCount(input.estimatedInsertCount),
    estimatedSkipCount: asCount(input.estimatedSkipCount),
    duplicateIds: freeze(asArray(input.duplicateIds)),
    typeCounts: freeze(isObject(input.typeCounts)
      ? input.typeCounts
      : { dhatu: 0, sutra: 0, stotra: 0 }),
    estimatedBytes: asCount(input.estimatedBytes),
    readiness: freeze(isObject(input.readiness) ? input.readiness : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {}),
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

function buildCorpusImportPreviewRecord(input = {}) {
  const normalized = normalizeCorpusImportPreviewInput(input);

  let state = CORPUS_IMPORT_PREVIEW_STATES.IMPORT_PREVIEW_READY;
  if (normalized.duplicateIds.length || normalized.estimatedSkipCount > 0) {
    state = CORPUS_IMPORT_PREVIEW_STATES.IMPORT_PREVIEW_WARNING;
  }
  if (
    normalized.readiness &&
    normalized.readiness.valid === false
  ) {
    state = CORPUS_IMPORT_PREVIEW_STATES.IMPORT_PREVIEW_BLOCKED;
  }

  return freeze({
    ...normalized,
    state
  });
}

module.exports = {
  CORPUS_IMPORT_PREVIEW_SCHEMA,
  CORPUS_IMPORT_PREVIEW_STATES,
  normalizeCorpusImportPreviewInput,
  buildCorpusImportPreviewRecord
};