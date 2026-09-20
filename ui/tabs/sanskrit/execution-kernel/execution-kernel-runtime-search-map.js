"use strict";

const SEARCH_SCHEMA = "sanskrit-runtime-search.v1";

const SEARCH_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  SEARCH_READY: "SEARCH_READY",
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

function normalizeRuntimeSearchRecord(input = {}) {
  return freeze({
    searchId: String(input.searchId || "runtime-search"),
    createdAt: String(input.createdAt || "static"),

    sourceQueryId: String(input.sourceQueryId || "runtime-query"),
    sourceQueryStatus: String(input.sourceQueryStatus || "query-ready"),
    sourceQueryMode: String(input.sourceQueryMode || "inspection-query"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    searchStatus: String(input.searchStatus || "search-ready"),
    searchMode: String(input.searchMode || "inspection-search"),

    searchAllowed: false,
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

    resultCount: asCount(input.resultCount),
    warningCount: asCount(input.warningCount),

    results: freeze(Array.isArray(input.results) ? input.results : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeSearchRecord(input = {}) {
  const normalized = normalizeRuntimeSearchRecord(input);

  return freeze({
    schemaVersion: SEARCH_SCHEMA,
    state: normalized.results.length > 0
      ? SEARCH_STATES.SEARCH_READY
      : SEARCH_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeSearchRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.results)) errors.push("results");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  SEARCH_SCHEMA,
  SEARCH_STATES,
  normalizeRuntimeSearchRecord,
  buildRuntimeSearchRecord,
  validateRuntimeSearchRecord
};