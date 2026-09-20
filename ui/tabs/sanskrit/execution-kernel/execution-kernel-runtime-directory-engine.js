"use strict";

const {
  buildRuntimeDirectoryRecord,
  normalizeRuntimeDirectoryRecord
} = require(
  "./execution-kernel-runtime-directory-map.js"
);

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeDirectoryEntries(
  record = {}
) {
  const entries = [
    "runtime-directory-surface",
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

  if (
    Array.isArray(
      record.warnings
    ) &&
    record.warnings.length
  ) {
    entries.push(
      "warning-reference-directory"
    );
  }

  return freeze(
    entries
  );
}

function createRuntimeDirectoryRecord(
  record = {}
) {
  const entries =
    deriveRuntimeDirectoryEntries(
      record
    );

  return buildRuntimeDirectoryRecord({
    ...record,

    directoryStatus:
      "directory-ready",

    directoryMode:
      "inspection-directory",

    entryCount:
      entries.length,

    warningCount:
      Array.isArray(
        record.warnings
      )
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
      directoryMetadataOnly: true
    }
  });
}

function inspectRuntimeDirectoryRecord(
  record = {}
) {
  const normalized =
    normalizeRuntimeDirectoryRecord(
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

function compareRuntimeDirectoryRecords(
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
  deriveRuntimeDirectoryEntries,
  createRuntimeDirectoryRecord,
  inspectRuntimeDirectoryRecord,
  compareRuntimeDirectoryRecords
};