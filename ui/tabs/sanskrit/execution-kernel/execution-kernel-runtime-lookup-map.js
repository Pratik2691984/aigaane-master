"use strict";

const LOOKUP_SCHEMA = "sanskrit-runtime-lookup.v1";

const LOOKUP_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  LOOKUP_READY: "LOOKUP_READY",
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

function normalizeRuntimeLookupRecord(input = {}) {
  return freeze({
    lookupId: String(input.lookupId || "runtime-lookup"),
    createdAt: String(input.createdAt || "static"),

    sourceDirectoryId: String(input.sourceDirectoryId || "runtime-directory"),
    sourceDirectoryStatus: String(input.sourceDirectoryStatus || "directory-ready"),
    sourceDirectoryMode: String(input.sourceDirectoryMode || "inspection-directory"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    lookupStatus: String(input.lookupStatus || "lookup-ready"),
    lookupMode: String(input.lookupMode || "inspection-lookup"),

    lookupAllowed: false,
    directoryAllowed: false,
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

    entries: freeze(Array.isArray(input.entries) ? input.entries : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeLookupRecord(input = {}) {
  const normalized = normalizeRuntimeLookupRecord(input);

  return freeze({
    schemaVersion: LOOKUP_SCHEMA,
    state: normalized.entries.length > 0
      ? LOOKUP_STATES.LOOKUP_READY
      : LOOKUP_STATES.EMPTY,

    ...normalized
  });
}

function validateRuntimeLookupRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.entries)) errors.push("entries");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  LOOKUP_SCHEMA,
  LOOKUP_STATES,
  normalizeRuntimeLookupRecord,
  buildRuntimeLookupRecord,
  validateRuntimeLookupRecord
};