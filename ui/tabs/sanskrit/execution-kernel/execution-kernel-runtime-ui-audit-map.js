"use strict";

const UI_AUDIT_SCHEMA = "sanskrit-runtime-ui-audit.v1";

const UI_AUDIT_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_AUDIT_READY: "UI_AUDIT_READY",
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

function normalizeRuntimeUiAuditRecord(input = {}) {
  return freeze({
    uiAuditId: String(input.uiAuditId || "runtime-ui-audit"),
    createdAt: String(input.createdAt || "static"),

    sourceUiReplayId: String(input.sourceUiReplayId || "runtime-ui-replay"),
    sourceUiReplayStatus: String(input.sourceUiReplayStatus || "ui-replay-ready"),
    sourceUiReplayMode: String(input.sourceUiReplayMode || "inspection-ui-replay"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    uiAuditStatus: String(input.uiAuditStatus || "ui-audit-ready"),
    uiAuditMode: String(input.uiAuditMode || "inspection-ui-audit"),

    uiAuditAllowed: false,
    uiReplayAllowed: false,
    uiSnapshotAllowed: false,
    controllerAllowed: false,
    panelAllowed: false,
    viewAllowed: false,
    sessionAllowed: false,
    workspaceAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    auditEntryCount: asCount(input.auditEntryCount),
    warningCount: asCount(input.warningCount),

    auditEntries: freeze(Array.isArray(input.auditEntries) ? input.auditEntries : []),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiAuditRecord(input = {}) {
  const normalized = normalizeRuntimeUiAuditRecord(input);

  return freeze({
    schemaVersion: UI_AUDIT_SCHEMA,
    state: normalized.auditEntries.length > 0
      ? UI_AUDIT_STATES.UI_AUDIT_READY
      : UI_AUDIT_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiAuditRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.auditEntries)) errors.push("auditEntries");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  UI_AUDIT_SCHEMA,
  UI_AUDIT_STATES,
  normalizeRuntimeUiAuditRecord,
  buildRuntimeUiAuditRecord,
  validateRuntimeUiAuditRecord
};