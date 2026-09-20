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

function renderCorpusApprovalPanel(summary = {}) {
  const ledger = Array.isArray(summary.approvalLedger)
    ? summary.approvalLedger
    : [];

  const ledgerLines = ledger.map((item) => {
    return "- "
      + escapeHtml(item.approvalId || "")
      + " ["
      + escapeHtml(item.status || "")
      + "] "
      + escapeHtml(item.message || "");
  });

  const body = [
    "State: " + escapeHtml(summary.state || "EMPTY"),
    "Valid: " + escapeHtml(Boolean(summary.valid)),
    "Approval Status: " + escapeHtml(summary.approvalStatus || "approval-ready"),
    "Recommendation: " + escapeHtml(summary.recommendation || "hold"),
    "Advisory Status: " + escapeHtml(summary.advisoryStatus || "advisory-blocked"),
    "Approval Ledger Count: " + escapeHtml(summary.approvalLedgerCount || 0),
    "Accepted Record Count: " + escapeHtml(summary.acceptedRecordCount || 0),
    "Rejected Record Count: " + escapeHtml(summary.rejectedRecordCount || 0),

    "",
    "Approval Ledger:",
    ...ledgerLines,

    "",
    "Preview Only: true",
    "Read Only: true",
    "Approval Execution Allowed: false",
    "Advisory Execution Allowed: false",
    "Promotion Execution Allowed: false",
    "Execution Allowed: false",
    "Canonical Write Allowed: false",
    "Promotion Allowed: false",
    "Import Allowed: false"
  ].join("\n");

  return freeze({
    title: "Sanskrit Bulk Corpus Promotion Approval",
    status: summary.valid ? "APPROVAL_READY" : "APPROVAL_BLOCKED",
    readOnly: true,
    body
  });
}

module.exports = {
  renderCorpusApprovalPanel
};