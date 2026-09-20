"use strict";

const IMPORT_SCHEMA = "sanskrit-runtime-import.v1";

const IMPORT_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  IMPORT_READY: "IMPORT_READY",
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
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.floor(n));
}

function normalizeRuntimeImportRecord(input = {}) {
  return freeze({
    importId: String(input.importId || "runtime-import"),
    createdAt: String(input.createdAt || "static"),

    sourceExportId: String(input.sourceExportId || "runtime-export"),
    sourceExportStatus: String(input.sourceExportStatus || "export-ready"),
    sourceExportMode: String(input.sourceExportMode || "inspection-export"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    importStatus: String(input.importStatus || "review-only"),
    importMode: String(input.importMode || "inspection-import"),

    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    attestationCount: asCount(input.attestationCount),
    warningCount: asCount(input.warningCount),

    attestations: freeze([
      ...(Array.isArray(input.attestations) ? input.attestations : [])
    ]),

    warnings: freeze([
      ...(Array.isArray(input.warnings) ? input.warnings : [])
    ]),

    diagnostics: freeze({
      ...(isObject(input.diagnostics) ? input.diagnostics : {})
    }),

    metadata: freeze({
      ...(isObject(input.metadata) ? input.metadata : {})
    })
  });
}

function buildRuntimeImportRecord(input = {}) {
  const normalized = normalizeRuntimeImportRecord(input);

  return freeze({
    schemaVersion: IMPORT_SCHEMA,
    state: normalized.attestations.length > 0
      ? IMPORT_STATES.REVIEW_ONLY
      : IMPORT_STATES.EMPTY,

    ...normalized,

    importStatus: "review-only",
    importMode: "inspection-import",

    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false
  });
}

function validateRuntimeImportRecord(record = {}) {
  const errors = [];

  if (!isObject(record)) errors.push("record");

  if (typeof record.importStatus !== "string") errors.push("importStatus");
  if (typeof record.importMode !== "string") errors.push("importMode");

  [
    "importAllowed",
    "replayAllowed",
    "executionAllowed",
    "mutationAllowed",
    "publicationAllowed",
    "rollbackAllowed",
    "canonicalWriteAllowed"
  ].forEach((field) => {
    if (typeof record[field] !== "boolean") errors.push(field);
  });

  if (
    !Number.isInteger(Number(record.attestationCount)) ||
    Number(record.attestationCount) < 0
  ) {
    errors.push("attestationCount");
  }

  if (
    !Number.isInteger(Number(record.warningCount)) ||
    Number(record.warningCount) < 0
  ) {
    errors.push("warningCount");
  }

  if (!Array.isArray(record.attestations)) errors.push("attestations");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  IMPORT_SCHEMA,
  IMPORT_STATES,
  normalizeRuntimeImportRecord,
  buildRuntimeImportRecord,
  validateRuntimeImportRecord
};