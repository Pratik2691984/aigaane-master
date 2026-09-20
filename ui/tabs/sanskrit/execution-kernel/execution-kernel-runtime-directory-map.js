"use strict";

const DIRECTORY_SCHEMA = "sanskrit-runtime-directory.v1";

const DIRECTORY_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  DIRECTORY_READY: "DIRECTORY_READY",
  BLOCKED: "BLOCKED",
  REVIEW_ONLY: "REVIEW_ONLY"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) &&
    typeof v === "object" &&
    !Array.isArray(v);
}

function asCount(v) {
  const n = Number(v || 0);

  return Number.isFinite(n)
    ? Math.max(0, Math.floor(n))
    : 0;
}

function normalizeRuntimeDirectoryRecord(
  input = {}
) {
  return freeze({
    directoryId:
      String(
        input.directoryId ||
        "runtime-directory"
      ),

    createdAt:
      String(
        input.createdAt ||
        "static"
      ),

    sourceIndexId:
      String(
        input.sourceIndexId ||
        "runtime-index"
      ),

    sourceIndexStatus:
      String(
        input.sourceIndexStatus ||
        "index-ready"
      ),

    sourceIndexMode:
      String(
        input.sourceIndexMode ||
        "inspection-index"
      ),

    sourceCertificate:
      String(
        input.sourceCertificate ||
        "controlled-runtime-inspection-only"
      ),

    directoryStatus:
      String(
        input.directoryStatus ||
        "directory-ready"
      ),

    directoryMode:
      String(
        input.directoryMode ||
        "inspection-directory"
      ),

    directoryAllowed: false,
    indexAllowed: false,
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

    entryCount:
      asCount(
        input.entryCount
      ),

    warningCount:
      asCount(
        input.warningCount
      ),

    entries:
      freeze(
        Array.isArray(
          input.entries
        )
          ? input.entries
          : []
      ),

    warnings:
      freeze(
        Array.isArray(
          input.warnings
        )
          ? input.warnings
          : []
      ),

    diagnostics:
      freeze(
        isObject(
          input.diagnostics
        )
          ? input.diagnostics
          : {}
      ),

    metadata:
      freeze(
        isObject(
          input.metadata
        )
          ? input.metadata
          : {}
      )
  });
}

function buildRuntimeDirectoryRecord(
  input = {}
) {
  const normalized =
    normalizeRuntimeDirectoryRecord(
      input
    );

  return freeze({
    schemaVersion:
      DIRECTORY_SCHEMA,

    state:
      normalized.entries.length
        ? DIRECTORY_STATES.DIRECTORY_READY
        : DIRECTORY_STATES.EMPTY,

    ...normalized
  });
}

function validateRuntimeDirectoryRecord(
  record = {}
) {
  const errors = [];

  if (
    !Array.isArray(
      record.entries
    )
  ) {
    errors.push(
      "entries"
    );
  }

  if (
    !Array.isArray(
      record.warnings
    )
  ) {
    errors.push(
      "warnings"
    );
  }

  if (
    !isObject(
      record.diagnostics
    )
  ) {
    errors.push(
      "diagnostics"
    );
  }

  if (
    !isObject(
      record.metadata
    )
  ) {
    errors.push(
      "metadata"
    );
  }

  return freeze({
    valid:
      errors.length === 0,

    errors
  });
}

module.exports = {
  DIRECTORY_SCHEMA,
  DIRECTORY_STATES,
  normalizeRuntimeDirectoryRecord,
  buildRuntimeDirectoryRecord,
  validateRuntimeDirectoryRecord
};