"use strict";

const {
  buildRuntimeCatalogRecord,
  normalizeRuntimeCatalogRecord
} = require("./execution-kernel-runtime-catalog-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function stableArray(v) {
  return Array.isArray(v) ? v : [];
}

function deriveRuntimeCatalogRecords(record = {}) {
  const warnings = stableArray(record.warnings);

  const records = [
    "runtime-lineage-catalog",
    "runtime-export-catalog",
    "runtime-import-catalog",
    "runtime-archive-catalog",
    "runtime-manifest-catalog",
    "runtime-readonly-catalog",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (warnings.length > 0) {
    records.push("warning-reference-catalogued");
  }

  return freeze(records);
}

function createRuntimeCatalogRecord(record = {}) {
  const warnings = stableArray(record.warnings);
  const records = deriveRuntimeCatalogRecords(record);

  return buildRuntimeCatalogRecord({
    sourceManifestId: record.manifestId || record.sourceManifestId || "runtime-manifest",
    sourceManifestStatus: record.manifestStatus || record.sourceManifestStatus || "manifest-ready",
    sourceManifestMode: record.manifestMode || record.sourceManifestMode || "inspection-manifest",
    sourceCertificate: record.sourceCertificate ||
      record.certificate ||
      "controlled-runtime-inspection-only",

    catalogStatus: "catalog-ready",
    catalogMode: "inspection-catalog",

    catalogAllowed: false,
    manifestAllowed: false,
    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    recordCount: records.length,
    warningCount: warnings.length,

    records,
    warnings,

    diagnostics: {
      catalogReady: true,
      readOnly: true,
      catalogBlocked: true,
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
      catalogMetadataOnly: true
    }
  });
}

function inspectRuntimeCatalogRecord(record = {}) {
  const normalized = normalizeRuntimeCatalogRecord(record);

  return freeze({
    ready: true,
    catalogStatus: "catalog-ready",
    catalogMode: "inspection-catalog",

    catalogAllowed: false,
    manifestAllowed: false,
    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    recordCount: normalized.records.length,
    warningCount: normalized.warnings.length,

    readOnly: true,
    catalogBlocked: true,
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

function compareRuntimeCatalogRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(normalizeRuntimeCatalogRecord(a)) ===
      JSON.stringify(normalizeRuntimeCatalogRecord(b)),

    catalogAllowed: false,
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
  deriveRuntimeCatalogRecords,
  createRuntimeCatalogRecord,
  inspectRuntimeCatalogRecord,
  compareRuntimeCatalogRecords
};