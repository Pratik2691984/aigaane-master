"use strict";

const UI_ASSURANCE_SCHEMA = "sanskrit-runtime-ui-assurance.v1";

const UI_ASSURANCE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_ASSURANCE_READY: "UI_ASSURANCE_READY",
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

function normalizeRuntimeUiAssuranceRecord(input = {}) {
  return freeze({
    uiAssuranceId: String(input.uiAssuranceId || "runtime-ui-assurance"),
    createdAt: String(input.createdAt || "static"),

    sourceUiIntegrityId: String(
      input.sourceUiIntegrityId || "runtime-ui-integrity"
    ),
    sourceUiIntegrityStatus: String(
      input.sourceUiIntegrityStatus || "ui-integrity-ready"
    ),
    sourceUiIntegrityMode: String(
      input.sourceUiIntegrityMode || "inspection-ui-integrity"
    ),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    uiAssuranceStatus: String(input.uiAssuranceStatus || "ui-assurance-ready"),
    uiAssuranceMode: String(input.uiAssuranceMode || "inspection-ui-assurance"),

    uiAssuranceAllowed: false,
    uiIntegrityAllowed: false,
    uiGovernanceAllowed: false,
    uiCertificationAllowed: false,
    uiAuditAllowed: false,
    uiReplayAllowed: false,
    uiSnapshotAllowed: false,
    controllerAllowed: false,
    panelAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    assuranceEntryCount: asCount(input.assuranceEntryCount),
    warningCount: asCount(input.warningCount),

    assuranceEntries: freeze(
      Array.isArray(input.assuranceEntries) ? input.assuranceEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiAssuranceRecord(input = {}) {
  const normalized = normalizeRuntimeUiAssuranceRecord(input);

  return freeze({
    schemaVersion: UI_ASSURANCE_SCHEMA,
    state: normalized.assuranceEntries.length > 0
      ? UI_ASSURANCE_STATES.UI_ASSURANCE_READY
      : UI_ASSURANCE_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiAssuranceRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.assuranceEntries)) {
    errors.push("assuranceEntries");
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
  UI_ASSURANCE_SCHEMA,
  UI_ASSURANCE_STATES,
  normalizeRuntimeUiAssuranceRecord,
  buildRuntimeUiAssuranceRecord,
  validateRuntimeUiAssuranceRecord
};