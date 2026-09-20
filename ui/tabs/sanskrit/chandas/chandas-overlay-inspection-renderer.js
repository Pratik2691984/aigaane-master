import { isChandasOverlayInspectionReady } from "./chandas-overlay-inspection-engine.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderSummaryRow(summary) {
  const statusClass = summary.available ? "success" : summary.required ? "warning" : "muted";

  return `
    <tr>
      <td>${escapeHtml(summary.label)}</td>
      <td>${escapeHtml(summary.required ? "required" : "optional")}</td>
      <td><span class="chandas-overlay-inspection-status ${statusClass}">${escapeHtml(summary.status)}</span></td>
    </tr>
  `;
}

function renderDiagnosticItem(diagnostic) {
  return `
    <li class="chandas-overlay-inspection-diagnostic ${escapeHtml(diagnostic.level)}">
      ${escapeHtml(diagnostic.message)}
    </li>
  `;
}

export function renderChandasOverlayInspection(inspection) {
  if (!inspection) {
    return `
      <section class="chandas-overlay-inspection-card">
        <h4>Overlay Inspection</h4>
        <p class="muted">No inspection data available.</p>
      </section>
    `;
  }

  const ready = isChandasOverlayInspectionReady(inspection);

  return `
    <section class="chandas-overlay-inspection-card">
      <div class="chandas-overlay-inspection-header">
        <h4>Overlay Inspection</h4>
        <span class="chandas-overlay-inspection-status ${ready ? "success" : "warning"}">
          ${ready ? "READY" : "PARTIAL"}
        </span>
      </div>

      <p class="muted">
        Schema: ${escapeHtml(inspection.schemaVersion)}
      </p>

      <table class="chandas-overlay-inspection-table">
        <thead>
          <tr>
            <th>Layer</th>
            <th>Requirement</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${(inspection.summaries || []).map(renderSummaryRow).join("")}
        </tbody>
      </table>

      <ul class="chandas-overlay-inspection-diagnostics">
        ${(inspection.diagnostics || []).map(renderDiagnosticItem).join("")}
      </ul>
    </section>
  `;
}