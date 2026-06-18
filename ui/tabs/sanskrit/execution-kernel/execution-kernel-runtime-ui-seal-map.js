"use strict";

const UI_SEAL_SCHEMA = "sanskrit-runtime-ui-seal.v1";

const UI_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_SEAL_READY: "UI_SEAL_READY",
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

function normalizeRuntimeUiSealRecord(input = {}) {
  return freeze({
    uiSealId: String(input.uiSealId || "runtime-ui-seal"),
    createdAt: String(input.createdAt || "static"),

    sourceUiAssuranceId: String(
      input.sourceUiAssuranceId || "runtime-ui-assurance"
    ),
    sourceUiAssuranceStatus: String(
      input.sourceUiAssuranceStatus || "ui-assurance-ready"
    ),
    sourceUiAssuranceMode: String(
      input.sourceUiAssuranceMode || "inspection-ui-assurance"
    ),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    uiSealStatus: String(input.uiSealStatus || "ui-seal-ready"),
    uiSealMode: String(input.uiSealMode || "inspection-ui-seal"),

    uiSealAllowed: false,
    uiAssuranceAllowed: false,
    uiIntegrityAllowed: false,
    uiGovernanceAllowed: false,
    uiCertificationAllowed: false,
    uiAuditAllowed: false,
    uiReplayAllowed: false,
    uiSnapshotAllowed: false,
    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    sealEntryCount: asCount(input.sealEntryCount),
    warningCount: asCount(input.warningCount),

    sealEntries: freeze(
      Array.isArray(input.sealEntries) ? input.sealEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiSealRecord(input);

  return freeze({
    schemaVersion: UI_SEAL_SCHEMA,
    state: normalized.sealEntries.length > 0
      ? UI_SEAL_STATES.UI_SEAL_READY
      : UI_SEAL_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiSealRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.sealEntries)) errors.push("sealEntries");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  UI_SEAL_SCHEMA,
  UI_SEAL_STATES,
  normalizeRuntimeUiSealRecord,
  buildRuntimeUiSealRecord,
  validateRuntimeUiSealRecord
};