"use strict";

const {
  buildRuntimeRegistryRecord,
  normalizeRuntimeRegistryRecord
} = require("./execution-kernel-runtime-registry-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function stableArray(v) {
  return Array.isArray(v) ? v : [];
}

function deriveRuntimeRegistryEntries(record = {}) {
  const warnings = stableArray(record.warnings);

  const entries = [
    "runtime-registry-index",
    "runtime-catalog-reference",
    "runtime-manifest-reference",
    "runtime-archive-reference",
    "runtime-import-reference",
    "runtime-export-reference",
    "runtime-readonly-reference",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (warnings.length > 0) {
    entries.push("warning-reference-registered");
  }

  return freeze(entries);
}

function createRuntimeRegistryRecord(record = {}) {
  const warnings = stableArray(record.warnings);
  const entries = deriveRuntimeRegistryEntries(record);

  return buildRuntimeRegistryRecord({
    sourceCatalogId: record.catalogId || record.sourceCatalogId || "runtime-catalog",
    sourceCatalogStatus: record.catalogStatus || record.sourceCatalogStatus || "catalog-ready",
    sourceCatalogMode: record.catalogMode || record.sourceCatalogMode || "inspection-catalog",
    sourceCertificate: record.sourceCertificate ||
      record.certificate ||
      "controlled-runtime-inspection-only",

    registryStatus: "registry-ready",
    registryMode: "inspection-registry",

    registryAllowed: false,
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

    entryCount: entries.length,
    warningCount: warnings.length,

    entries,
    warnings,

    diagnostics: {
      registryReady: true,
      readOnly: true,
      registryBlocked: true,
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
      registryMetadataOnly: true
    }
  });
}

function inspectRuntimeRegistryRecord(record = {}) {
  const normalized = normalizeRuntimeRegistryRecord(record);

  return freeze({
    ready: true,
    registryStatus: "registry-ready",
    registryMode: "inspection-registry",

    registryAllowed: false,
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

    entryCount: normalized.entries.length,
    warningCount: normalized.warnings.length,

    readOnly: true,
    registryBlocked: true,
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

function compareRuntimeRegistryRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(normalizeRuntimeRegistryRecord(a)) ===
      JSON.stringify(normalizeRuntimeRegistryRecord(b)),

    registryAllowed: false,
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
  deriveRuntimeRegistryEntries,
  createRuntimeRegistryRecord,
  inspectRuntimeRegistryRecord,
  compareRuntimeRegistryRecords
};