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

function renderRuntimeUiGovernancePanel(record = {}) {
  const governanceEntries = Array.isArray(record.governanceEntries)
    ? record.governanceEntries
    : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "UI Governance Status: " + escapeHtml(record.uiGovernanceStatus),
    "UI Governance Mode: " + escapeHtml(record.uiGovernanceMode),
    "Source UI Certification Status: " + escapeHtml(
      record.sourceUiCertificationStatus
    ),
    "Source UI Certification Mode: " + escapeHtml(
      record.sourceUiCertificationMode
    ),
    "Source Certificate: " + escapeHtml(record.sourceCertificate),

    "",
    "Allowed Flags:",
    "UI Governance Allowed: false",
    "UI Certification Allowed: false",
    "UI Audit Allowed: false",
    "UI Replay Allowed: false",
    "UI Snapshot Allowed: false",
    "Controller Allowed: false",
    "Panel Allowed: false",
    "View Allowed: false",
    "Session Allowed: false",
    "Execution Allowed: false",
    "Mutation Allowed: false",
    "Publication Allowed: false",
    "Rollback Allowed: false",
    "Canonical Write Allowed: false",

    "",
    "Governance Entry Count: " + escapeHtml(
      record.governanceEntryCount || governanceEntries.length || 0
    ),
    "Warning Count: " + escapeHtml(record.warningCount || warnings.length || 0),

    "",
    "Governance Entries:",
    ...governanceEntries.map((entry) => "- " + escapeHtml(entry)),

    "",
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime UI Governance",
    status: governanceEntries.length ? "UI_GOVERNANCE_READY" : "EMPTY",
    readOnly: true,
    body
  });
}

module.exports = {
  renderRuntimeUiGovernancePanel
};