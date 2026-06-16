"use strict";

const {
  buildRuntimeWorkspaceRecord,
  normalizeRuntimeWorkspaceRecord
} = require("./execution-kernel-runtime-workspace-map.js");

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeWorkspacePanels(record = {}) {
  const panels = [
    "runtime-workspace-surface",
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
    panels.push("warning-reference-workspace");
  }

  return freeze(panels);
}

function createRuntimeWorkspaceRecord(record = {}) {
  const panels = deriveRuntimeWorkspacePanels(record);

  return buildRuntimeWorkspaceRecord({
    ...record,

    workspaceStatus: "workspace-ready",
    workspaceMode: "inspection-workspace",

    panelCount: panels.length,
    warningCount: Array.isArray(record.warnings) ? record.warnings.length : 0,

    panels,

    diagnostics: {
      readOnly: true,
      workspaceBlocked: true,
      executionBlocked: true,
      mutationBlocked: true,
      publicationBlocked: true,
      rollbackBlocked: true,
      canonicalWriteBlocked: true
    },

    metadata: {
      workspaceMetadataOnly: true
    }
  });
}

function inspectRuntimeWorkspaceRecord(record = {}) {
  const normalized = normalizeRuntimeWorkspaceRecord(record);

  return freeze({
    readOnly: true,
    panelCount: normalized.panels.length,
    workspaceBlocked: true,
    executionBlocked: true,
    mutationBlocked: true,
    publicationBlocked: true,
    rollbackBlocked: true,
    canonicalWriteBlocked: true
  });
}

function compareRuntimeWorkspaceRecords(a = {}, b = {}) {
  return freeze({
    stable: JSON.stringify(a) === JSON.stringify(b)
  });
}

module.exports = {
  deriveRuntimeWorkspacePanels,
  createRuntimeWorkspaceRecord,
  inspectRuntimeWorkspaceRecord,
  compareRuntimeWorkspaceRecords
};