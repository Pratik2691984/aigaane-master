import { isChandasOverlaySnapshotReady } from "./chandas-overlay-snapshot-engine.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderConsistencyList(consistency) {
  const entries = Object.entries(consistency || {});

  if (!entries.length) {
    return `<li class="muted">No consistency fields captured.</li>`;
  }

  return entries
    .map(
      ([key, value]) => `
        <li>
          <span>${escapeHtml(key)}</span>
          <strong>${escapeHtml(value ? "true" : "false")}</strong>
        </li>
      `
    )
    .join("");
}

export function renderChandasOverlaySnapshot(snapshot) {
  if (!snapshot) {
    return `
      <section class="chandas-overlay-snapshot-card">
        <h4>Overlay Snapshot</h4>
        <p class="muted">No snapshot data available.</p>
      </section>
    `;
  }

  const ready = isChandasOverlaySnapshotReady(snapshot);

  return `
    <section class="chandas-overlay-snapshot-card">
      <div class="chandas-overlay-snapshot-header">
        <h4>Overlay Snapshot</h4>
        <span class="chandas-overlay-snapshot-status ${ready ? "success" : "warning"}">
          ${ready ? "IMMUTABLE" : "PARTIAL"}
        </span>
      </div>

      <p class="muted">
        Schema: ${escapeHtml(snapshot.schemaVersion)}
      </p>

      <dl class="chandas-overlay-snapshot-grid">
        <div>
          <dt>Sequence</dt>
          <dd>${escapeHtml(snapshot.sequence)}</dd>
        </div>
        <div>
          <dt>Summaries</dt>
          <dd>${escapeHtml(snapshot.summaryCount)}</dd>
        </div>
        <div>
          <dt>Diagnostics</dt>
          <dd>${escapeHtml(snapshot.diagnosticCount)}</dd>
        </div>
        <div>
          <dt>Digest</dt>
          <dd>${escapeHtml(snapshot.digest)}</dd>
        </div>
      </dl>

      <ul class="chandas-overlay-snapshot-consistency">
        ${renderConsistencyList(snapshot.consistency)}
      </ul>
    </section>
  `;
}