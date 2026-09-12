"use strict";

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCorpusManualReviewPanel(input = {}) {
  const status = escapeHtml(input.status || "manual-review-pending");
  const attested = input.attested === true;
  const body = [
    "<section class=\"corpus-manual-review\">",
    "<h2>Node 38D Manual Review</h2>",
    "<p>Status: " + status + "</p>",
    "<p>Attested: " + (attested ? "yes" : "no") + "</p>",
    "<p>Hard stop: CLOSED</p>",
    "<p>Human attestation is not write authorization.</p>",
    "<p>Canonical write / promotion / import / execution: REFUSED</p>",
    "</section>"
  ].join("");
  return { title: "Manual Review", body };
}

module.exports = {
  renderCorpusManualReviewPanel
};
