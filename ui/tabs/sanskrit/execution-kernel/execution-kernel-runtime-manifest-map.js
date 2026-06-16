"use strict";

const MANIFEST_SCHEMA = "sanskrit-runtime-manifest.v1";

const MANIFEST_STATES = Object.freeze({
  EMPTY: "EMPTY",
  READY: "READY",
  CONTROLLED: "CONTROLLED",
  MANIFEST_READY: "MANIFEST_READY",
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

function normalizeRuntimeManifestRecord(input = {}) {
  return freeze({
    manifestId: String(input.manifestId || "runtime-manifest"),
    createdAt: String(input.createdAt || "static"),

    sourceArchiveId: String(input.sourceArchiveId || "runtime-archive"),
    sourceArchiveStatus: String(input.sourceArchiveStatus || "archive-ready"),
    sourceArchiveMode: String(input.sourceArchiveMode || "inspection-archive"),
    sourceCertificate: String(
      input.sourceCertificate || "controlled-runtime-inspection-only"
    ),

    manifestStatus: String(input.manifestStatus || "manifest-ready"),
    manifestMode: String(input.manifestMode || "inspection-manifest"),

    manifestAllowed: false,
    archiveAllowed: false,
    importAllowed: false,
    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    entryCount: asCount(input.entryCount),
    warningCount: asCount(input.warningCount),

    entries: freeze([
      ...(Array.isArray(input.entries) ? input.entries : [])
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

function buildRuntimeManifestRecord(input = {}) {
  const normalized = normalizeRuntimeManifestRecord(input);

  return freeze({
    schemaVersion: MANIFEST_SCHEMA,
    state: normalized.entries.length > 0
      ? MANIFEST_STATES.MANIFEST_READY
      : MANIFEST_STATES.EMPTY,

    ...normalized,

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
    canonicalWriteAllowed: false
  });
}

function validateRuntimeManifestRecord(record = {}) {
  const errors = [];

  if (!isObject(record)) errors.push("record");

  if (typeof record.manifestStatus !== "string") errors.push("manifestStatus");
  if (typeof record.manifestMode !== "string") errors.push("manifestMode");

  [
    "manifestAllowed",
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
    !Number.isInteger(Number(record.entryCount)) ||
    Number(record.entryCount) < 0
  ) {
    errors.push("entryCount");
  }

  if (
    !Number.isInteger(Number(record.warningCount)) ||
    Number(record.warningCount) < 0
  ) {
    errors.push("warningCount");
  }

  if (!Array.isArray(record.entries)) errors.push("entries");
  if (!Array.isArray(record.warnings)) errors.push("warnings");
  if (!isObject(record.diagnostics)) errors.push("diagnostics");
  if (!isObject(record.metadata)) errors.push("metadata");

  return freeze({
    valid: errors.length === 0,
    errors
  });
}

module.exports = {
  MANIFEST_SCHEMA,
  MANIFEST_STATES,
  normalizeRuntimeManifestRecord,
  buildRuntimeManifestRecord,
  validateRuntimeManifestRecord
};