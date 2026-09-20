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

function renderRuntimeAuditPanel(record = {}) {
  const findings = Array.isArray(record.findings) ? record.findings : [];
  const warnings = Array.isArray(record.warnings) ? record.warnings : [];

  const body = [
    "Audit Status: " + escapeHtml(record.auditStatus || "review-only"),
    "Replay Mode: " + escapeHtml(record.replayMode || "inspection-only"),
    "Replay Allowed: " + escapeHtml(record.replayAllowed === true),
    "Step Count: " + escapeHtml(record.stepCount || 0),
    "Source Hash: " + escapeHtml(record.sourceHash || "source-pending"),
    "Target Hash: " + escapeHtml(record.targetHash || "target-pending"),
    "Findings:",
    ...findings.map((finding) => "- " + escapeHtml(finding)),
    "Warnings:",
    ...warnings.map((warning) => "- " + escapeHtml(warning))
  ].join("\n");

  return freeze({
    title: "Runtime Audit",
    status: findings.length > 0 ? "REVIEW_ONLY" : "EMPTY",
    readOnly: true,
    replayAllowed: false,
    body
  });
}

module.exports = {
  renderRuntimeAuditPanel
};