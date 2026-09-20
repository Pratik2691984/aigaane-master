"use strict";

const UI_AUDIT_SEAL_SCHEMA = "sanskrit-runtime-ui-audit-seal.v1";

const UI_AUDIT_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_AUDIT_SEAL_READY: "UI_AUDIT_SEAL_READY",
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

function normalizeRuntimeUiAuditSealRecord(input = {}) {
  return freeze({
    uiAuditSealId: String(input.uiAuditSealId || "runtime-ui-audit-seal"),
    createdAt: String(input.createdAt || "static"),

    sourceUiReplaySealId: String(input.sourceUiReplaySealId || "runtime-ui-replay-seal"),
    sourceUiReplaySealStatus: String(input.sourceUiReplaySealStatus || "ui-replay-seal-ready"),
    sourceUiSnapshotSealId: String(input.sourceUiSnapshotSealId || "runtime-ui-snapshot-seal"),
    sourceUiSealId: String(input.sourceUiSealId || "runtime-ui-seal"),

    uiAuditSealStatus: String(input.uiAuditSealStatus || "ui-audit-seal-ready"),
    uiAuditSealMode: String(input.uiAuditSealMode || "inspection-ui-audit-seal"),

    auditSealAllowed: false,
    replaySealAllowed: false,
    uiSnapshotSealAllowed: false,
    uiSealAllowed: false,
    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    auditSealEntryCount: asCount(input.auditSealEntryCount),
    warningCount: asCount(input.warningCount),

    auditSealEntries: freeze(
      Array.isArray(input.auditSealEntries) ? input.auditSealEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiAuditSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiAuditSealRecord(input);

  return freeze({
    schemaVersion: UI_AUDIT_SEAL_SCHEMA,
    state: normalized.auditSealEntries.length > 0
      ? UI_AUDIT_SEAL_STATES.UI_AUDIT_SEAL_READY
      : UI_AUDIT_SEAL_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiAuditSealRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.auditSealEntries)) errors.push("auditSealEntries");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  UI_AUDIT_SEAL_SCHEMA,
  UI_AUDIT_SEAL_STATES,
  normalizeRuntimeUiAuditSealRecord,
  buildRuntimeUiAuditSealRecord,
  validateRuntimeUiAuditSealRecord
};