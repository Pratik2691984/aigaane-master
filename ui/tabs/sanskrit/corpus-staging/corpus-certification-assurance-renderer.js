"use strict";

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCorpusCertificationAssurancePanel(input = {}) {
  const status = escapeHtml(input.status || "assurance-blocked");
  const assured = input.assured === true;
  const body = [
    "<section class=\"corpus-certification-assurance\">",
    "<h2>Node 38C Certification Assurance</h2>",
    "<p>Status: " + status + "</p>",
    "<p>Assured: " + (assured ? "yes" : "no") + "</p>",
    "<p>Hard stop: CLOSED</p>",
    "<p>Canonical write: BLOCKED</p>",
    "<p>Promotion / import / execution: REFUSED</p>",
    "<p>Certification is not an authorization.</p>",
    "</section>"
  ].join("");

  return {
    title: "Certification Assurance",
    body
  };
}

module.exports = {
  renderCorpusCertificationAssurancePanel
};
