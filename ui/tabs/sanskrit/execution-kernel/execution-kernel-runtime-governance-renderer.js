"use strict";

function freeze(v) {
  return Object.freeze(v);
}

function escapeHtml(v) {
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderFlag(label, value) {
  return label + ": " + escapeHtml(value === true);
}

function renderRuntimeGovernancePanel(decision = {}) {
  const controls = Array.isArray(decision.controls) ? decision.controls : [];
  const warnings = Array.isArray(decision.warnings) ? decision.warnings : [];

  const body = [
    "Governance Status: " + escapeHtml(decision.governanceStatus || "inspection-approved"),
    "Decision: " + escapeHtml(decision.decision || "approve-inspection-only"),

    renderFlag("Replay Allowed", false),
    renderFlag("Execution Allowed", false),
    renderFlag("Mutation Allowed", false),
    renderFlag("Publication Allowed", false),
    renderFlag("Rollback Allowed", false),
    renderFlag("Canonical Write Allowed", false),

    "Finding Count: " + escapeHtml(decision.findingCount || 0),
    "Warning Count: " + escapeHtml(decision.warningCount || 0),

    "Controls:",
    ...controls.map((control) => "- " + escapeHtml(control)),

    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Governance",
    status: controls.length > 0 ? "APPROVED_FOR_INSPECTION" : "EMPTY",
    readOnly: true,

    replayAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,
    canonicalWriteAllowed: false,

    body
  });
}

module.exports = {
  renderRuntimeGovernancePanel
};