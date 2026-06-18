"use strict";

const UI_SNAPSHOT_SEAL_SCHEMA = "sanskrit-runtime-ui-snapshot-seal.v1";

const UI_SNAPSHOT_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_SNAPSHOT_SEAL_READY: "UI_SNAPSHOT_SEAL_READY",
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

function normalizeRuntimeUiSnapshotSealRecord(input = {}) {
  return freeze({
    uiSnapshotSealId: String(input.uiSnapshotSealId || "runtime-ui-snapshot-seal"),
    createdAt: String(input.createdAt || "static"),

    sourceUiSealId: String(input.sourceUiSealId || "runtime-ui-seal"),
    sourceUiSealStatus: String(input.sourceUiSealStatus || "ui-seal-ready"),
    sourceUiSealMode: String(input.sourceUiSealMode || "inspection-ui-seal"),

    sourceUiAssuranceId: String(input.sourceUiAssuranceId || "runtime-ui-assurance"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    uiSnapshotSealStatus: String(
      input.uiSnapshotSealStatus || "ui-snapshot-seal-ready"
    ),
    uiSnapshotSealMode: String(
      input.uiSnapshotSealMode || "inspection-ui-snapshot-seal"
    ),

    uiSnapshotSealAllowed: false,
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

    snapshotSealEntryCount: asCount(input.snapshotSealEntryCount),
    warningCount: asCount(input.warningCount),

    snapshotSealEntries: freeze(
      Array.isArray(input.snapshotSealEntries) ? input.snapshotSealEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiSnapshotSealRecord(input = {}) {
  const normalized = normalizeRuntimeUiSnapshotSealRecord(input);

  return freeze({
    schemaVersion: UI_SNAPSHOT_SEAL_SCHEMA,
    state: normalized.snapshotSealEntries.length > 0
      ? UI_SNAPSHOT_SEAL_STATES.UI_SNAPSHOT_SEAL_READY
      : UI_SNAPSHOT_SEAL_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiSnapshotSealRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.snapshotSealEntries)) {
    errors.push("snapshotSealEntries");
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
  UI_SNAPSHOT_SEAL_SCHEMA,
  UI_SNAPSHOT_SEAL_STATES,
  normalizeRuntimeUiSnapshotSealRecord,
  buildRuntimeUiSnapshotSealRecord,
  validateRuntimeUiSnapshotSealRecord
};