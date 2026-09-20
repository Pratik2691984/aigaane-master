"use strict";

const {
  buildRuntimeArchiveRecord,
  normalizeRuntimeArchiveRecord
} = require("./execution-kernel-runtime-archive-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function stableArray(v) {
  return Array.isArray(v) ? v : [];
}

function deriveRuntimeArchiveAttestations(record = {}) {
  const warnings = stableArray(record.warnings);

  const attestations = [
    "inspection-archive-reviewed",
    "source-import-readonly-accepted",
    "archive-metadata-only",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (warnings.length > 0) {
    attestations.push("warning-carry-forward-archived");
  }

  return freeze(attestations);
}

function createRuntimeArchiveRecord(record = {}) {
  const warnings = stableArray(record.warnings);
  const attestations = deriveRuntimeArchiveAttestations(record);

  return buildRuntimeArchiveRecord({
    sourceImportId: record.importId || record.sourceImportId || "runtime-import",
    sourceImportStatus: record.importStatus || record.sourceImportStatus || "review-only",
    sourceImportMode: record.importMode || record.sourceImportMode || "inspection-import",
    sourceCertificate: record.sourceCertificate ||
      record.certificate ||
      "controlled-runtime-inspection-only",

    archiveStatus: "archive-ready",
    archiveMode: "inspection-archive",

    archiveAllowed: false,
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
      archiveReady: true,
      readOnly: true,
      archiveBlocked: true,
      importBlocked: true,
      replayBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      archiveMetadataOnly: true
    }
  });
}

function inspectRuntimeArchiveRecord(record = {}) {
  const normalized = normalizeRuntimeArchiveRecord(record);

  return freeze({
    ready: true,
    archiveStatus: "archive-ready",
    archiveMode: "inspection-archive",

    archiveAllowed: false,
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
    archiveBlocked: true,
    importBlocked: true,
    replayBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeArchiveRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(normalizeRuntimeArchiveRecord(a)) ===
      JSON.stringify(normalizeRuntimeArchiveRecord(b)),

    archiveAllowed: false,
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
  deriveRuntimeArchiveAttestations,
  createRuntimeArchiveRecord,
  inspectRuntimeArchiveRecord,
  compareRuntimeArchiveRecords
};