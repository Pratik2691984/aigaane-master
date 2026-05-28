import { isChandasOverlayVerificationReady } from "./chandas-overlay-verification-engine.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderInvariants(invariants) {
  if (!Array.isArray(invariants) || !invariants.length) {
    return `<li class="muted">No verification invariants emitted.</li>`;
  }

  return invariants
    .map(
      (invariant) => `
        <li>
          <strong>${escapeHtml(invariant.passed ? "pass" : "fail")}</strong>
          <span>${escapeHtml(invariant.message)}</span>
        </li>
      `
    )
    .join("");
}

export function renderChandasOverlayVerification(verification) {
  if (!verification) {
    return `
      <section class="chandas-overlay-verification-card">
        <h4>Overlay Verification</h4>
        <p class="muted">No verification data available.</p>
      </section>
    `;
  }

  const ready = isChandasOverlayVerificationReady(verification);

  return `
    <section class="chandas-overlay-verification-card">
      <div class="chandas-overlay-verification-header">
        <h4>Overlay Verification</h4>
        <span class="chandas-overlay-verification-status ${ready && verification.verified ? "success" : "warning"}">
          ${verification.verified ? "VERIFIED" : "PARTIAL"}
        </span>
      </div>

      <p class="muted">
        Schema: ${escapeHtml(verification.schemaVersion)}
      </p>

      <dl class="chandas-overlay-verification-grid">
        <div>
          <dt>Verified</dt>
          <dd>${escapeHtml(verification.verified ? "true" : "false")}</dd>
        </div>
        <div>
          <dt>Invariants</dt>
          <dd>${escapeHtml(verification.invariantCount)}</dd>
        </div>
        <div>
          <dt>Passed</dt>
          <dd>${escapeHtml(verification.summary?.passed || 0)}</dd>
        </div>
        <div>
          <dt>Failed</dt>
          <dd>${escapeHtml(verification.summary?.failed || 0)}</dd>
        </div>
      </dl>

      <ul class="chandas-overlay-verification-invariants">
        ${renderInvariants(verification.invariants)}
      </ul>
    </section>
  `;
}