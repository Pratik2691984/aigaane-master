import { isChandasOverlayReplayReady } from "./chandas-overlay-replay-engine.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderDiagnosticList(diagnostics) {
  if (!Array.isArray(diagnostics) || !diagnostics.length) {
    return `<li class="muted">No replay diagnostics emitted.</li>`;
  }

  return diagnostics
    .map(
      (diagnostic) => `
        <li class="chandas-overlay-replay-diagnostic ${escapeHtml(diagnostic.level)}">
          ${escapeHtml(diagnostic.message)}
        </li>
      `
    )
    .join("");
}

export function renderChandasOverlayReplay(replay) {
  if (!replay) {
    return `
      <section class="chandas-overlay-replay-card">
        <h4>Overlay Replay</h4>
        <p class="muted">No replay data available.</p>
      </section>
    `;
  }

  const ready = isChandasOverlayReplayReady(replay);

  return `
    <section class="chandas-overlay-replay-card">
      <div class="chandas-overlay-replay-header">
        <h4>Overlay Replay</h4>
        <span class="chandas-overlay-replay-status ${ready ? "success" : "warning"}">
          ${ready ? "CURSOR" : "PARTIAL"}
        </span>
      </div>

      <p class="muted">
        Schema: ${escapeHtml(replay.schemaVersion)}
      </p>

      <dl class="chandas-overlay-replay-grid">
        <div>
          <dt>Cursor Index</dt>
          <dd>${escapeHtml(replay.cursor?.index ?? 0)}</dd>
        </div>
        <div>
          <dt>Sequence</dt>
          <dd>${escapeHtml(replay.cursor?.sequence ?? 0)}</dd>
        </div>
        <div>
          <dt>Total Steps</dt>
          <dd>${escapeHtml(replay.totalSteps)}</dd>
        </div>
        <div>
          <dt>Digest</dt>
          <dd>${escapeHtml(replay.cursor?.digest || "")}</dd>
        </div>
        <div>
          <dt>Has Previous</dt>
          <dd>${escapeHtml(replay.hasPrevious ? "true" : "false")}</dd>
        </div>
        <div>
          <dt>Has Next</dt>
          <dd>${escapeHtml(replay.hasNext ? "true" : "false")}</dd>
        </div>
      </dl>

      <ul class="chandas-overlay-replay-diagnostics">
        ${renderDiagnosticList(replay.diagnostics)}
      </ul>
    </section>
  `;
}