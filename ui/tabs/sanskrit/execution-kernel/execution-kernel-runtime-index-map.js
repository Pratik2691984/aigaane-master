"use strict";

const INDEX_SCHEMA = "sanskrit-runtime-index.v1";

const INDEX_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  INDEX_READY: "INDEX_READY",
  BLOCKED: "BLOCKED",
  REVIEW_ONLY: "REVIEW_ONLY"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

function asCount(v) {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : 0;
}

function normalizeRuntimeIndexRecord(input = {}) {
  return freeze({
    indexId: String(input.indexId || "runtime-index"),
    createdAt: String(input.createdAt || "static"),

    sourceRegistryId: String(
      input.sourceRegistryId || "runtime-registry"
    ),

    sourceRegistryStatus: String(
      input.sourceRegistryStatus || "registry-ready"
    ),

    sourceRegistryMode: String(
      input.sourceRegistryMode || "inspection-registry"
    ),

    sourceCertificate: String(
      input.sourceCertificate ||
      "controlled-runtime-inspection-only"
    ),

    indexStatus: String(
      input.indexStatus || "index-ready"
    ),

    indexMode: String(
      input.indexMode || "inspection-index"
    ),

    indexAllowed: false,
    registryAllowed: false,
    catalogAllowed: false,
    manifestAllowed: false,
    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    entryCount: asCount(input.entryCount),
    warningCount: asCount(input.warningCount),

    entries: freeze(
      Array.isArray(input.entries)
        ? input.entries
        : []
    ),

    warnings: freeze(
      Array.isArray(input.warnings)
        ? input.warnings
        : []
    ),

    diagnostics: freeze(
      isObject(input.diagnostics)
        ? input.diagnostics
        : {}
    ),

    metadata: freeze(
      isObject(input.metadata)
        ? input.metadata
        : {}
    )
  });
}

function buildRuntimeIndexRecord(input = {}) {
  const normalized =
    normalizeRuntimeIndexRecord(input);

  return freeze({
    schemaVersion: INDEX_SCHEMA,

    state:
      normalized.entries.length > 0
        ? INDEX_STATES.INDEX_READY
        : INDEX_STATES.EMPTY,

    ...normalized
  });
}

function validateRuntimeIndexRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.entries)) {
    errors.push("entries");
  }

  if (!Array.isArray(record.warnings)) {
    errors.push("warnings");
  }

  if (!isObject(record.diagnostics)) {
    errors.push("diagnostics");
  }

  if (!isObject(record.metadata)) {
    errors.push("metadata");
  }

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  INDEX_SCHEMA,
  INDEX_STATES,
  normalizeRuntimeIndexRecord,
  buildRuntimeIndexRecord,
  validateRuntimeIndexRecord
};