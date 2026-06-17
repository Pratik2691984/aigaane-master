"use strict";

const VIEW_SCHEMA = "sanskrit-runtime-view.v1";

const VIEW_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  VIEW_READY: "VIEW_READY",
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

function normalizeRuntimeViewRecord(input = {}) {
  return freeze({
    viewId: String(input.viewId || "runtime-view"),
    createdAt: String(input.createdAt || "static"),

    sourceSessionId: String(input.sourceSessionId || "runtime-session"),
    sourceSessionStatus: String(input.sourceSessionStatus || "session-ready"),
    sourceSessionMode: String(input.sourceSessionMode || "inspection-session"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    viewStatus: String(input.viewStatus || "view-ready"),
    viewMode: String(input.viewMode || "inspection-view"),

    viewAllowed: false,
    sessionAllowed: false,
    workspaceAllowed: false,
    explorerAllowed: false,
    navigatorAllowed: false,
    resolverAllowed: false,
    searchAllowed: false,
    queryAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    viewCount: asCount(input.viewCount),
    warningCount: asCount(input.warningCount),

    views: freeze(Array.isArray(input.views) ? input.views : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeViewRecord(input = {}) {
  const normalized = normalizeRuntimeViewRecord(input);

  return freeze({
    schemaVersion: VIEW_SCHEMA,
    state: normalized.views.length > 0
      ? VIEW_STATES.VIEW_READY
      : VIEW_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeViewRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.views)) errors.push("views");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  VIEW_SCHEMA,
  VIEW_STATES,
  normalizeRuntimeViewRecord,
  buildRuntimeViewRecord,
  validateRuntimeViewRecord
};