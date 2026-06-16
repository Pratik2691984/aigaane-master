"use strict";

const RESOLVER_SCHEMA = "sanskrit-runtime-resolver.v1";

const RESOLVER_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  RESOLVER_READY: "RESOLVER_READY",
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

function normalizeRuntimeResolverRecord(input = {}) {
  return freeze({
    resolverId: String(input.resolverId || "runtime-resolver"),
    createdAt: String(input.createdAt || "static"),

    sourceSearchId: String(input.sourceSearchId || "runtime-search"),
    sourceSearchStatus: String(input.sourceSearchStatus || "search-ready"),
    sourceSearchMode: String(input.sourceSearchMode || "inspection-search"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    resolverStatus: String(input.resolverStatus || "resolver-ready"),
    resolverMode: String(input.resolverMode || "inspection-resolver"),

    resolverAllowed: false,
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

    resolutionCount: asCount(input.resolutionCount),
    warningCount: asCount(input.warningCount),

    resolutions: freeze(Array.isArray(input.resolutions) ? input.resolutions : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeResolverRecord(input = {}) {
  const normalized = normalizeRuntimeResolverRecord(input);

  return freeze({
    schemaVersion: RESOLVER_SCHEMA,
    state: normalized.resolutions.length > 0
      ? RESOLVER_STATES.RESOLVER_READY
      : RESOLVER_STATES.EMPTY,

    ...normalized
  });
}

function validateRuntimeResolverRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.resolutions)) errors.push("resolutions");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  RESOLVER_SCHEMA,
  RESOLVER_STATES,
  normalizeRuntimeResolverRecord,
  buildRuntimeResolverRecord,
  validateRuntimeResolverRecord
};