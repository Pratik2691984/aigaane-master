import { isChandasOverlayHistoryReady } from "./chandas-overlay-history-engine.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderTimeline(history) {
  const entries = Array.isArray(history?.timeline) ? history.timeline : [];

  if (!entries.length) {
    return `<li class="muted">No snapshots captured.</li>`;
  }

  return entries
    .map(
      (entry) => `
        <li>
          <strong>#${escapeHtml(entry.sequence)}</strong>
          <span>${escapeHtml(entry.digest)}</span>
        </li>
      `
    )
    .join("");
}

function renderDiffChain(history) {
  const entries = Array.isArray(history?.diffChain) ? history.diffChain : [];

  if (!entries.length) {
    return `<li class="muted">No diff chain available.</li>`;
  }

  return entries
    .map(
      (entry) => `
        <li>
          <strong>${escapeHtml(entry.changed ? "changed" : "stable")}</strong>
          <span>${escapeHtml(entry.baselineDigest)} → ${escapeHtml(entry.candidateDigest)}</span>
        </li>
      `
    )
    .join("");
}

export function renderChandasOverlayHistory(history) {
  if (!history) {
    return `
      <section class="chandas-overlay-history-card">
        <h4>Overlay History</h4>
        <p class="muted">No history data available.</p>
      </section>
    `;
  }

  const ready = isChandasOverlayHistoryReady(history);

  return `
    <section class="chandas-overlay-history-card">
      <div class="chandas-overlay-history-header">
        <h4>Overlay History</h4>
        <span class="chandas-overlay-history-status ${ready ? "success" : "warning"}">
          ${ready ? "TIMELINE" : "PARTIAL"}
        </span>
      </div>

      <p class="muted">
        Schema: ${escapeHtml(history.schemaVersion)}
      </p>

      <dl class="chandas-overlay-history-grid">
        <div>
          <dt>Snapshots</dt>
          <dd>${escapeHtml(history.summary?.snapshotCount || 0)}</dd>
        </div>
        <div>
          <dt>Diffs</dt>
          <dd>${escapeHtml(history.summary?.diffCount || 0)}</dd>
        </div>
        <div>
          <dt>Changed Diffs</dt>
          <dd>${escapeHtml(history.summary?.changedDiffCount || 0)}</dd>
        </div>
      </dl>

      <h5>Timeline</h5>
      <ul class="chandas-overlay-history-timeline">
        ${renderTimeline(history)}
      </ul>

      <h5>Diff Chain</h5>
      <ul class="chandas-overlay-history-diff-chain">
        ${renderDiffChain(history)}
      </ul>
    </section>
  `;
}