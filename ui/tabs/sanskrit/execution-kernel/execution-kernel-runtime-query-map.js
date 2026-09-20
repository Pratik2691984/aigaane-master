"use strict";

const QUERY_SCHEMA = "sanskrit-runtime-query.v1";

const QUERY_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  QUERY_READY: "QUERY_READY",
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

function normalizeRuntimeQueryRecord(input = {}) {
  return freeze({
    queryId: String(input.queryId || "runtime-query"),
    createdAt: String(input.createdAt || "static"),

    sourceLookupId: String(input.sourceLookupId || "runtime-lookup"),
    sourceLookupStatus: String(input.sourceLookupStatus || "lookup-ready"),
    sourceLookupMode: String(input.sourceLookupMode || "inspection-lookup"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    queryStatus: String(input.queryStatus || "query-ready"),
    queryMode: String(input.queryMode || "inspection-query"),

    queryAllowed: false,
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

function buildRuntimeQueryRecord(input = {}) {
  const normalized = normalizeRuntimeQueryRecord(input);

  return freeze({
    schemaVersion: QUERY_SCHEMA,
    state: normalized.entries.length > 0
      ? QUERY_STATES.QUERY_READY
      : QUERY_STATES.EMPTY,

    ...normalized
  });
}

function validateRuntimeQueryRecord(record = {}) {
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
  QUERY_SCHEMA,
  QUERY_STATES,
  normalizeRuntimeQueryRecord,
  buildRuntimeQueryRecord,
  validateRuntimeQueryRecord
};