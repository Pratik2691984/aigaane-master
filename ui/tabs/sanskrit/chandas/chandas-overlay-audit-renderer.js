import { isChandasOverlayAuditReady } from "./chandas-overlay-audit-engine.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderCheckpoints(checkpoints) {
  if (!Array.isArray(checkpoints) || !checkpoints.length) {
    return `<li class="muted">No audit checkpoints emitted.</li>`;
  }

  return checkpoints
    .map(
      (checkpoint) => `
        <li>
          <strong>${escapeHtml(checkpoint.passed ? "pass" : "fail")}</strong>
          <span>${escapeHtml(checkpoint.message)}</span>
        </li>
      `
    )
    .join("");
}

export function renderChandasOverlayAudit(audit) {
  if (!audit) {
    return `
      <section class="chandas-overlay-audit-card">
        <h4>Overlay Audit</h4>
        <p class="muted">No audit data available.</p>
      </section>
    `;
  }

  const ready = isChandasOverlayAuditReady(audit);

  return `
    <section class="chandas-overlay-audit-card">
      <div class="chandas-overlay-audit-header">
        <h4>Overlay Audit</h4>
        <span class="chandas-overlay-audit-status ${ready && audit.verified ? "success" : "warning"}">
          ${audit.verified ? "VERIFIED" : "PARTIAL"}
        </span>
      </div>

      <p class="muted">
        Schema: ${escapeHtml(audit.schemaVersion)}
      </p>

      <dl class="chandas-overlay-audit-grid">
        <div>
          <dt>Verified</dt>
          <dd>${escapeHtml(audit.verified ? "true" : "false")}</dd>
        </div>
        <div>
          <dt>Checkpoints</dt>
          <dd>${escapeHtml(audit.checkpointCount)}</dd>
        </div>
        <div>
          <dt>Replay Available</dt>
          <dd>${escapeHtml(audit.integrity?.replayAvailable ? "true" : "false")}</dd>
        </div>
        <div>
          <dt>Traversal Bounded</dt>
          <dd>${escapeHtml(audit.integrity?.traversalBounded ? "true" : "false")}</dd>
        </div>
      </dl>

      <ul class="chandas-overlay-audit-checkpoints">
        ${renderCheckpoints(audit.checkpoints)}
      </ul>
    </section>
  `;
}