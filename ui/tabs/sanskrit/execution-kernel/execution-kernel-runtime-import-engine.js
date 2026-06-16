"use strict";

const {
  buildRuntimeImportRecord,
  normalizeRuntimeImportRecord
} = require("./execution-kernel-runtime-import-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function stableArray(v) {
  return Array.isArray(v) ? v : [];
}

function deriveRuntimeImportFindings(record = {}) {
  const warnings = stableArray(record.warnings);

  const findings = [
    "inspection-import-reviewed",
    "source-export-readonly-accepted",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (warnings.length > 0) {
    findings.push("warning-review-required");
  }

  return freeze(findings);
}

function createRuntimeImportRecord(record = {}) {
  const warnings = stableArray(record.warnings);
  const attestations = deriveRuntimeImportFindings(record);

  return buildRuntimeImportRecord({
    sourceExportId: record.exportId || record.sourceExportId || "runtime-export",
    sourceExportStatus: record.exportStatus || record.sourceExportStatus || "export-ready",
    sourceExportMode: record.exportMode || record.sourceExportMode || "inspection-export",
    sourceCertificate: record.certificate ||
      record.sourceCertificate ||
      "controlled-runtime-inspection-only",

    importStatus: "review-only",
    importMode: "inspection-import",

    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    attestationCount: attestations.length,
    warningCount: warnings.length,

    attestations,
    warnings,

    diagnostics: {
      importReady: true,
      readOnly: true,
      importBlocked: true,
      replayBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      importedForInspectionOnly: true
    }
  });
}

function inspectRuntimeImportRecord(record = {}) {
  const normalized = normalizeRuntimeImportRecord(record);

  return freeze({
    ready: true,
    importStatus: "review-only",
    importMode: "inspection-import",

    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    attestationCount: normalized.attestations.length,
    warningCount: normalized.warnings.length,

    readOnly: true,
    importBlocked: true,
    replayBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeImportRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(normalizeRuntimeImportRecord(a)) ===
      JSON.stringify(normalizeRuntimeImportRecord(b)),

    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,
    readOnly: true
  });
}

module.exports = {
  deriveRuntimeImportFindings,
  createRuntimeImportRecord,
  inspectRuntimeImportRecord,
  compareRuntimeImportRecords
};