"use strict";

const {
  buildRuntimePanelRecord,
  normalizeRuntimePanelRecord
} = require("./execution-kernel-runtime-panel-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimePanelSections(record = {}) {
  const sections = [
    "runtime-panel-surface",
    "runtime-view-reference",
    "runtime-session-reference",
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
    sections.push("warning-reference-panel");
  }

  return freeze(sections);
}

function createRuntimePanelRecord(record = {}) {
  const sections = deriveRuntimePanelSections(record);

  return buildRuntimePanelRecord({
    ...record,

    panelStatus: "panel-ready",
    panelMode: "inspection-panel",

    sectionCount: sections.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    sections,

    diagnostics: {
      readOnly: true,
      panelBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      panelMetadataOnly: true
    }
  });
}

function inspectRuntimePanelRecord(record = {}) {
  const normalized = normalizeRuntimePanelRecord(record);

  return freeze({
    readOnly: true,
    sectionCount: normalized.sections.length,
    panelBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimePanelRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimePanelSections,
  createRuntimePanelRecord,
  inspectRuntimePanelRecord,
  compareRuntimePanelRecords
};