"use strict";

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCorpusGovernanceDecisionPanel(input = {}) {
  const status = escapeHtml(input.status || "governance-decision-pending");
  const decision = escapeHtml(input.decision == null ? "none" : input.decision);
  const body = [
    "<section class=\"corpus-governance-decision\">",
    "<h2>Node 38F Governance Decision</h2>",
    "<p>Status: " + status + "</p>",
    "<p>Decision: " + decision + "</p>",
    "<p>CLEARED FOR AUTHORIZATION IS NOT AUTHORIZED TO WRITE</p>",
    "<p>Hard stop: CLOSED</p>",
    "<p>Not authorized: canonical write / promotion / import / execution</p>",
    "<p>Next: 38G PROMOTION AUTHORIZATION</p>",
    "</section>"
  ].join("");
  return { title: "Governance Decision", body };
}

module.exports = {
  renderCorpusGovernanceDecisionPanel
};
