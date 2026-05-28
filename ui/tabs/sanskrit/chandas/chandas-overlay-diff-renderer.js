import { isChandasOverlayDiffReady } from "./chandas-overlay-diff-engine.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderChangeList(changes) {
  if (!Array.isArray(changes) || !changes.length) {
    return `<li class="muted">No deterministic snapshot changes detected.</li>`;
  }

  return changes
    .map(
      (change) => `
        <li>
          <strong>${escapeHtml(change.field)}</strong>
          <span>${escapeHtml(change.before)} → ${escapeHtml(change.after)}</span>
        </li>
      `
    )
    .join("");
}

function renderDiagnosticList(diagnostics) {
  if (!Array.isArray(diagnostics) || !diagnostics.length) {
    return `<li class="muted">No diff diagnostics emitted.</li>`;
  }

  return diagnostics
    .map(
      (diagnostic) => `
        <li class="chandas-overlay-diff-diagnostic ${escapeHtml(diagnostic.level)}">
          ${escapeHtml(diagnostic.message)}
        </li>
      `
    )
    .join("");
}

export function renderChandasOverlayDiff(diff) {
  if (!diff) {
    return `
      <section class="chandas-overlay-diff-card">
        <h4>Overlay Diff</h4>
        <p class="muted">No diff data available.</p>
      </section>
    `;
  }

  const ready = isChandasOverlayDiffReady(diff);

  return `
    <section class="chandas-overlay-diff-card">
      <div class="chandas-overlay-diff-header">
        <h4>Overlay Diff</h4>
        <span class="chandas-overlay-diff-status ${ready ? "success" : "warning"}">
          ${ready ? "COMPARED" : "PARTIAL"}
        </span>
      </div>

      <p class="muted">
        Schema: ${escapeHtml(diff.schemaVersion)}
      </p>

      <dl class="chandas-overlay-diff-grid">
        <div>
          <dt>Changed</dt>
          <dd>${escapeHtml(diff.changed ? "true" : "false")}</dd>
        </div>
        <div>
          <dt>Change Count</dt>
          <dd>${escapeHtml(diff.changeCount)}</dd>
        </div>
        <div>
          <dt>Baseline Digest</dt>
          <dd>${escapeHtml(diff.baselineDigest)}</dd>
        </div>
        <div>
          <dt>Candidate Digest</dt>
          <dd>${escapeHtml(diff.candidateDigest)}</dd>
        </div>
      </dl>

      <ul class="chandas-overlay-diff-changes">
        ${renderChangeList(diff.changes)}
      </ul>

      <ul class="chandas-overlay-diff-diagnostics">
        ${renderDiagnosticList(diff.diagnostics)}
      </ul>
    </section>
  `;
}