"use strict";

const NAVIGATOR_SCHEMA = "sanskrit-runtime-navigator.v1";

const NAVIGATOR_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  NAVIGATOR_READY: "NAVIGATOR_READY",
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

function normalizeRuntimeNavigatorRecord(input = {}) {
  return freeze({
    navigatorId: String(input.navigatorId || "runtime-navigator"),
    createdAt: String(input.createdAt || "static"),

    sourceResolverId: String(input.sourceResolverId || "runtime-resolver"),
    sourceResolverStatus: String(input.sourceResolverStatus || "resolver-ready"),
    sourceResolverMode: String(input.sourceResolverMode || "inspection-resolver"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    navigatorStatus: String(input.navigatorStatus || "navigator-ready"),
    navigatorMode: String(input.navigatorMode || "inspection-navigator"),

    navigatorAllowed: false,
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

    routeCount: asCount(input.routeCount),
    warningCount: asCount(input.warningCount),

    routes: freeze(Array.isArray(input.routes) ? input.routes : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeNavigatorRecord(input = {}) {
  const normalized = normalizeRuntimeNavigatorRecord(input);

  return freeze({
    schemaVersion: NAVIGATOR_SCHEMA,
    state: normalized.routes.length > 0
      ? NAVIGATOR_STATES.NAVIGATOR_READY
      : NAVIGATOR_STATES.EMPTY,

    ...normalized
  });
}

function validateRuntimeNavigatorRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.routes)) errors.push("routes");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  NAVIGATOR_SCHEMA,
  NAVIGATOR_STATES,
  normalizeRuntimeNavigatorRecord,
  buildRuntimeNavigatorRecord,
  validateRuntimeNavigatorRecord
};