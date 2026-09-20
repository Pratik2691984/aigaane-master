"use strict";

const {
  buildRuntimeIndexRecord,
  normalizeRuntimeIndexRecord
} = require(
  "./execution-kernel-runtime-index-map.js"
);

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeIndexEntries(
  record = {}
) {
  const entries = [
    "runtime-index-surface",
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

  if (
    Array.isArray(record.warnings) &&
    record.warnings.length
  ) {
    entries.push(
      "warning-reference-indexed"
    );
  }

  return freeze(entries);
}

function createRuntimeIndexRecord(
  record = {}
) {
  const entries =
    deriveRuntimeIndexEntries(record);

  return buildRuntimeIndexRecord({
    ...record,

    indexStatus:
      "index-ready",

    indexMode:
      "inspection-index",

    entryCount:
      entries.length,

    warningCount:
      Array.isArray(record.warnings)
        ? record.warnings.length
        : 0,

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
      indexMetadataOnly: true
    }
  });
}

function inspectRuntimeIndexRecord(
  record = {}
) {
  const normalized =
    normalizeRuntimeIndexRecord(
      record
    );

  return freeze({
    readOnly: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true,

    entryCount:
      normalized.entries.length
  });
}

function compareRuntimeIndexRecords(
  a = {},
  b = {}
) {
  return freeze({
    stable:
      JSON.stringify(a) ===
      JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeIndexEntries,
  createRuntimeIndexRecord,
  inspectRuntimeIndexRecord,
  compareRuntimeIndexRecords
};