import { isChandasOverlayCertificationReady } from "./chandas-overlay-certification-engine.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderSummaries(summaries) {
  if (!Array.isArray(summaries) || !summaries.length) {
    return `<li class="muted">No certification summaries emitted.</li>`;
  }

  return summaries
    .map(
      (summary) => `
        <li>
          <strong>${escapeHtml(summary.label)}</strong>
          <span>${escapeHtml(summary.value)}</span>
        </li>
      `
    )
    .join("");
}

export function renderChandasOverlayCertification(certification) {
  if (!certification) {
    return `
      <section class="chandas-overlay-certification-card">
        <h4>Overlay Certification</h4>
        <p class="muted">No certification data available.</p>
      </section>
    `;
  }

  const ready = isChandasOverlayCertificationReady(certification);

  return `
    <section class="chandas-overlay-certification-card">
      <div class="chandas-overlay-certification-header">
        <h4>Overlay Certification</h4>
        <span class="chandas-overlay-certification-status ${ready && certification.certified ? "success" : "warning"}">
          ${certification.certified ? "CERTIFIED" : "PARTIAL"}
        </span>
      </div>

      <p class="muted">
        Schema: ${escapeHtml(certification.schemaVersion)}
      </p>

      <dl class="chandas-overlay-certification-grid">
        <div>
          <dt>Certified</dt>
          <dd>${escapeHtml(certification.certified ? "true" : "false")}</dd>
        </div>
        <div>
          <dt>Level</dt>
          <dd>${escapeHtml(certification.level)}</dd>
        </div>
        <div>
          <dt>Invariants</dt>
          <dd>${escapeHtml(certification.readiness?.invariantCount || 0)}</dd>
        </div>
        <div>
          <dt>Passed</dt>
          <dd>${escapeHtml(certification.readiness?.passedInvariantCount || 0)}</dd>
        </div>
      </dl>

      <ul class="chandas-overlay-certification-summaries">
        ${renderSummaries(certification.summaries)}
      </ul>
    </section>
  `;
}