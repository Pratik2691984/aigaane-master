"use strict";

const {
  buildRuntimeLookupRecord,
  normalizeRuntimeLookupRecord
} = require("./execution-kernel-runtime-lookup-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeLookupEntries(record = {}) {
  const entries = [
    "runtime-lookup-surface",
    "runtime-directory-reference",
    "runtime-index-reference",
    "runtime-registry-reference",
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

  if (Array.isArray(record.warnings) && record.warnings.length) {
    entries.push("warning-reference-lookup");
  }

  return freeze(entries);
}

function createRuntimeLookupRecord(record = {}) {
  const entries = deriveRuntimeLookupEntries(record);

  return buildRuntimeLookupRecord({
    ...record,

    lookupStatus: "lookup-ready",
    lookupMode: "inspection-lookup",

    entryCount: entries.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    entries,

    diagnostics: {
      readOnly: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      lookupMetadataOnly: true
    }
  });
}

function inspectRuntimeLookupRecord(record = {}) {
  const normalized = normalizeRuntimeLookupRecord(record);

  return freeze({
    readOnly: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true,

    entryCount: normalized.entries.length
  });
}

function compareRuntimeLookupRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeLookupEntries,
  createRuntimeLookupRecord,
  inspectRuntimeLookupRecord,
  compareRuntimeLookupRecords
};