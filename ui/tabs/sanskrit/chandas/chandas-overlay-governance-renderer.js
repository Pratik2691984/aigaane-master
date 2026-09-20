import { isChandasOverlayGovernanceReady } from "./chandas-overlay-governance-engine.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderPolicies(policies) {
  if (!Array.isArray(policies) || !policies.length) {
    return `<li class="muted">No governance policies emitted.</li>`;
  }

  return policies
    .map(
      (policy) => `
        <li>
          <strong>${escapeHtml(policy.passed ? "pass" : "fail")}</strong>
          <span>${escapeHtml(policy.message)}</span>
        </li>
      `
    )
    .join("");
}

export function renderChandasOverlayGovernance(governance) {
  if (!governance) {
    return `
      <section class="chandas-overlay-governance-card">
        <h4>Overlay Governance</h4>
        <p class="muted">No governance data available.</p>
      </section>
    `;
  }

  const ready = isChandasOverlayGovernanceReady(governance);

  return `
    <section class="chandas-overlay-governance-card">
      <div class="chandas-overlay-governance-header">
        <h4>Overlay Governance</h4>
        <span class="chandas-overlay-governance-status ${ready && governance.governed ? "success" : "warning"}">
          ${governance.governed ? "GOVERNED" : "PARTIAL"}
        </span>
      </div>

      <p class="muted">
        Schema: ${escapeHtml(governance.schemaVersion)}
      </p>

      <dl class="chandas-overlay-governance-grid">
        <div>
          <dt>Governed</dt>
          <dd>${escapeHtml(governance.governed ? "true" : "false")}</dd>
        </div>
        <div>
          <dt>Classification</dt>
          <dd>${escapeHtml(governance.classification)}</dd>
        </div>
        <div>
          <dt>Policies</dt>
          <dd>${escapeHtml(governance.policyCount)}</dd>
        </div>
        <div>
          <dt>Passed</dt>
          <dd>${escapeHtml(governance.passedPolicyCount)}</dd>
        </div>
      </dl>

      <ul class="chandas-overlay-governance-policies">
        ${renderPolicies(governance.policies)}
      </ul>
    </section>
  `;
}