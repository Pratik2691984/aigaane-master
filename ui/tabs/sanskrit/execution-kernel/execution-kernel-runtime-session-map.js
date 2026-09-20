"use strict";

const SESSION_SCHEMA = "sanskrit-runtime-session.v1";

const SESSION_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  SESSION_READY: "SESSION_READY",
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

function normalizeRuntimeSessionRecord(input = {}) {
  return freeze({
    sessionId: String(input.sessionId || "runtime-session"),
    createdAt: String(input.createdAt || "static"),

    sourceWorkspaceId: String(input.sourceWorkspaceId || "runtime-workspace"),
    sourceWorkspaceStatus: String(input.sourceWorkspaceStatus || "workspace-ready"),
    sourceWorkspaceMode: String(input.sourceWorkspaceMode || "inspection-workspace"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    sessionStatus: String(input.sessionStatus || "session-ready"),
    sessionMode: String(input.sessionMode || "inspection-session"),

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

    frameCount: asCount(input.frameCount),
    warningCount: asCount(input.warningCount),

    frames: freeze(Array.isArray(input.frames) ? input.frames : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeSessionRecord(input = {}) {
  const normalized = normalizeRuntimeSessionRecord(input);

  return freeze({
    schemaVersion: SESSION_SCHEMA,
    state: normalized.frames.length > 0
      ? SESSION_STATES.SESSION_READY
      : SESSION_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeSessionRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.frames)) errors.push("frames");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  SESSION_SCHEMA,
  SESSION_STATES,
  normalizeRuntimeSessionRecord,
  buildRuntimeSessionRecord,
  validateRuntimeSessionRecord
};