"use strict";

const ARCHIVE_SCHEMA = "sanskrit-runtime-archive.v1";

const ARCHIVE_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  ARCHIVE_READY: "ARCHIVE_READY",
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

function normalizeRuntimeArchiveRecord(input = {}) {
  return freeze({
    archiveId: String(input.archiveId || "runtime-archive"),
    createdAt: String(input.createdAt || "static"),

    sourceImportId: String(input.sourceImportId || "runtime-import"),
    sourceImportStatus: String(input.sourceImportStatus || "review-only"),
    sourceImportMode: String(input.sourceImportMode || "inspection-import"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    archiveStatus: String(input.archiveStatus || "archive-ready"),
    archiveMode: String(input.archiveMode || "inspection-archive"),

    archiveAllowed: false,
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

function buildRuntimeArchiveRecord(input = {}) {
  const normalized = normalizeRuntimeArchiveRecord(input);

  return freeze({
    schemaVersion: ARCHIVE_SCHEMA,
    state: normalized.attestations.length > 0
      ? ARCHIVE_STATES.ARCHIVE_READY
      : ARCHIVE_STATES.EMPTY,

    ...normalized,

    archiveStatus: "archive-ready",
    archiveMode: "inspection-archive",

    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false
  });
}

function validateRuntimeArchiveRecord(record = {}) {
  const errors = [];

  if (!isObject(record)) errors.push("record");

  if (typeof record.archiveStatus !== "string") errors.push("archiveStatus");
  if (typeof record.archiveMode !== "string") errors.push("archiveMode");

  [
    "archiveAllowed",
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
  ARCHIVE_SCHEMA,
  ARCHIVE_STATES,
  normalizeRuntimeArchiveRecord,
  buildRuntimeArchiveRecord,
  validateRuntimeArchiveRecord
};