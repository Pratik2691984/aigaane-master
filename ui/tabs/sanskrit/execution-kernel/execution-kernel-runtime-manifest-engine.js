"use strict";

const {
  buildRuntimeManifestRecord,
  normalizeRuntimeManifestRecord
} = require("./execution-kernel-runtime-manifest-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function stableArray(v) {
  return Array.isArray(v) ? v : [];
}

function deriveRuntimeManifestEntries(record = {}) {
  const warnings = stableArray(record.warnings);

  const entries = [
    "runtime-inspection-lineage",
    "runtime-export-reference",
    "runtime-import-reference",
    "runtime-archive-reference",
    "runtime-readonly-reference",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (warnings.length > 0) {
    entries.push("warning-reference-added");
  }

  return freeze(entries);
}

function createRuntimeManifestRecord(record = {}) {
  const warnings = stableArray(record.warnings);
  const entries = deriveRuntimeManifestEntries(record);

  return buildRuntimeManifestRecord({
    sourceArchiveId: record.archiveId || record.sourceArchiveId || "runtime-archive",
    sourceArchiveStatus: record.archiveStatus || record.sourceArchiveStatus || "archive-ready",
    sourceArchiveMode: record.archiveMode || record.sourceArchiveMode || "inspection-archive",
    sourceCertificate: record.sourceCertificate ||
      record.certificate ||
      "controlled-runtime-inspection-only",

    manifestStatus: "manifest-ready",
    manifestMode: "inspection-manifest",

    manifestAllowed: false,
    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    entryCount: entries.length,
    warningCount: warnings.length,

    entries,
    warnings,

    diagnostics: {
      manifestReady: true,
      readOnly: true,
      manifestBlocked: true,
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
      manifestMetadataOnly: true
    }
  });
}

function inspectRuntimeManifestRecord(record = {}) {
  const normalized = normalizeRuntimeManifestRecord(record);

  return freeze({
    ready: true,
    manifestStatus: "manifest-ready",
    manifestMode: "inspection-manifest",

    manifestAllowed: false,
    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    entryCount: normalized.entries.length,
    warningCount: normalized.warnings.length,

    readOnly: true,
    manifestBlocked: true,
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

function compareRuntimeManifestRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(normalizeRuntimeManifestRecord(a)) ===
      JSON.stringify(normalizeRuntimeManifestRecord(b)),

    manifestAllowed: false,
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
  deriveRuntimeManifestEntries,
  createRuntimeManifestRecord,
  inspectRuntimeManifestRecord,
  compareRuntimeManifestRecords
};