"use strict";

const {
  buildRuntimeSessionRecord,
  normalizeRuntimeSessionRecord
} = require("./execution-kernel-runtime-session-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeSessionFrames(record = {}) {
  const frames = [
    "runtime-session-surface",
    "runtime-workspace-reference",
    "runtime-explorer-reference",
    "runtime-navigator-reference",
    "runtime-resolver-reference",
    "runtime-search-reference",
    "runtime-query-reference",
    "runtime-readonly-reference",
    "execution-denied",
    "mutation-denied",
    "publication-denied",
    "rollback-denied",
    "canonical-write-denied"
  ];

  if (Array.isArray(record.warnings) && record.warnings.length) {
    frames.push("warning-reference-session");
  }

  return freeze(frames);
}

function createRuntimeSessionRecord(record = {}) {
  const frames = deriveRuntimeSessionFrames(record);

  return buildRuntimeSessionRecord({
    ...record,

    sessionStatus: "session-ready",
    sessionMode: "inspection-session",

    frameCount: frames.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    frames,

    diagnostics: {
      readOnly: true,
      sessionBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      sessionMetadataOnly: true
    }
  });
}

function inspectRuntimeSessionRecord(record = {}) {
  const normalized = normalizeRuntimeSessionRecord(record);

  return freeze({
    readOnly: true,
    frameCount: normalized.frames.length,
    sessionBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeSessionRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeSessionFrames,
  createRuntimeSessionRecord,
  inspectRuntimeSessionRecord,
  compareRuntimeSessionRecords
};