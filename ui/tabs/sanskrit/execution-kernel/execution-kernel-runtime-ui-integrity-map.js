"use strict";

const UI_INTEGRITY_SCHEMA = "sanskrit-runtime-ui-integrity.v1";

const UI_INTEGRITY_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_INTEGRITY_READY: "UI_INTEGRITY_READY",
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

function normalizeRuntimeUiIntegrityRecord(input = {}) {
  return freeze({
    uiIntegrityId: String(input.uiIntegrityId || "runtime-ui-integrity"),
    createdAt: String(input.createdAt || "static"),

    sourceUiGovernanceId: String(
      input.sourceUiGovernanceId || "runtime-ui-governance"
    ),
    sourceUiGovernanceStatus: String(
      input.sourceUiGovernanceStatus || "ui-governance-ready"
    ),
    sourceUiGovernanceMode: String(
      input.sourceUiGovernanceMode || "inspection-ui-governance"
    ),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    uiIntegrityStatus: String(input.uiIntegrityStatus || "ui-integrity-ready"),
    uiIntegrityMode: String(input.uiIntegrityMode || "inspection-ui-integrity"),

    uiIntegrityAllowed: false,
    uiGovernanceAllowed: false,
    uiCertificationAllowed: false,
    uiAuditAllowed: false,
    uiReplayAllowed: false,
    uiSnapshotAllowed: false,
    controllerAllowed: false,
    panelAllowed: false,
    viewAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    integrityEntryCount: asCount(input.integrityEntryCount),
    warningCount: asCount(input.warningCount),

    integrityEntries: freeze(
      Array.isArray(input.integrityEntries) ? input.integrityEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiIntegrityRecord(input = {}) {
  const normalized = normalizeRuntimeUiIntegrityRecord(input);

  return freeze({
    schemaVersion: UI_INTEGRITY_SCHEMA,
    state: normalized.integrityEntries.length > 0
      ? UI_INTEGRITY_STATES.UI_INTEGRITY_READY
      : UI_INTEGRITY_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiIntegrityRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.integrityEntries)) {
    errors.push("integrityEntries");
  }
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  UI_INTEGRITY_SCHEMA,
  UI_INTEGRITY_STATES,
  normalizeRuntimeUiIntegrityRecord,
  buildRuntimeUiIntegrityRecord,
  validateRuntimeUiIntegrityRecord
};