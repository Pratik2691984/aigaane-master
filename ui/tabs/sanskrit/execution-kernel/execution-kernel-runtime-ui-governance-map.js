"use strict";

const UI_GOVERNANCE_SCHEMA = "sanskrit-runtime-ui-governance.v1";

const UI_GOVERNANCE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_GOVERNANCE_READY: "UI_GOVERNANCE_READY",
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

function normalizeRuntimeUiGovernanceRecord(input = {}) {
  return freeze({
    uiGovernanceId: String(input.uiGovernanceId || "runtime-ui-governance"),
    createdAt: String(input.createdAt || "static"),

    sourceUiCertificationId: String(
      input.sourceUiCertificationId || "runtime-ui-certification"
    ),
    sourceUiCertificationStatus: String(
      input.sourceUiCertificationStatus || "ui-certification-ready"
    ),
    sourceUiCertificationMode: String(
      input.sourceUiCertificationMode || "inspection-ui-certification"
    ),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    uiGovernanceStatus: String(input.uiGovernanceStatus || "ui-governance-ready"),
    uiGovernanceMode: String(input.uiGovernanceMode || "inspection-ui-governance"),

    uiGovernanceAllowed: false,
    uiCertificationAllowed: false,
    uiAuditAllowed: false,
    uiReplayAllowed: false,
    uiSnapshotAllowed: false,
    controllerAllowed: false,
    panelAllowed: false,
    viewAllowed: false,
    sessionAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    governanceEntryCount: asCount(input.governanceEntryCount),
    warningCount: asCount(input.warningCount),

    governanceEntries: freeze(
      Array.isArray(input.governanceEntries) ? input.governanceEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiGovernanceRecord(input = {}) {
  const normalized = normalizeRuntimeUiGovernanceRecord(input);

  return freeze({
    schemaVersion: UI_GOVERNANCE_SCHEMA,
    state: normalized.governanceEntries.length > 0
      ? UI_GOVERNANCE_STATES.UI_GOVERNANCE_READY
      : UI_GOVERNANCE_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiGovernanceRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.governanceEntries)) {
    errors.push("governanceEntries");
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
  UI_GOVERNANCE_SCHEMA,
  UI_GOVERNANCE_STATES,
  normalizeRuntimeUiGovernanceRecord,
  buildRuntimeUiGovernanceRecord,
  validateRuntimeUiGovernanceRecord
};