"use strict";

const UI_CERTIFICATION_SCHEMA = "sanskrit-runtime-ui-certification.v1";

const UI_CERTIFICATION_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  UI_CERTIFICATION_READY: "UI_CERTIFICATION_READY",
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

function normalizeRuntimeUiCertificationRecord(input = {}) {
  return freeze({
    uiCertificationId: String(input.uiCertificationId || "runtime-ui-certification"),
    createdAt: String(input.createdAt || "static"),

    sourceUiAuditId: String(input.sourceUiAuditId || "runtime-ui-audit"),
    sourceUiAuditStatus: String(input.sourceUiAuditStatus || "ui-audit-ready"),
    sourceUiAuditMode: String(input.sourceUiAuditMode || "inspection-ui-audit"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    uiCertificationStatus: String(
      input.uiCertificationStatus || "ui-certification-ready"
    ),
    uiCertificationMode: String(
      input.uiCertificationMode || "inspection-ui-certification"
    ),

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

    certificationEntryCount: asCount(input.certificationEntryCount),
    warningCount: asCount(input.warningCount),

    certificationEntries: freeze(
      Array.isArray(input.certificationEntries) ? input.certificationEntries : []
    ),
    warnings: freeze(Array.isArray(input.warnings) ? input.warnings : []),

    diagnostics: freeze(isObject(input.diagnostics) ? input.diagnostics : {}),
    metadata: freeze(isObject(input.metadata) ? input.metadata : {})
  });
}

function buildRuntimeUiCertificationRecord(input = {}) {
  const normalized = normalizeRuntimeUiCertificationRecord(input);

  return freeze({
    schemaVersion: UI_CERTIFICATION_SCHEMA,
    state: normalized.certificationEntries.length > 0
      ? UI_CERTIFICATION_STATES.UI_CERTIFICATION_READY
      : UI_CERTIFICATION_STATES.EMPTY,
    ...normalized
  });
}

function validateRuntimeUiCertificationRecord(record = {}) {
  const errors = [];

  if (!Array.isArray(record.certificationEntries)) {
    errors.push("certificationEntries");
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
  UI_CERTIFICATION_SCHEMA,
  UI_CERTIFICATION_STATES,
  normalizeRuntimeUiCertificationRecord,
  buildRuntimeUiCertificationRecord,
  validateRuntimeUiCertificationRecord
};