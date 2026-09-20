const PHASE_LABELS = {
  NORMAL: "NORMAL",
  PRE_COLLAPSE: "PRE_COLLAPSE",
  COLLAPSED: "COLLAPSED"
};

export function PhaseBanner(root) {
  root.innerHTML = `
    <section class="phase-banner phase-normal">
      <div>
        <span class="phase-kicker">Anumana Neuro-Collapse</span>
        <h2 data-phase>Normal</h2>
      </div>
      <dl>
        <div><dt>k</dt><dd data-k>--</dd></div>
        <div><dt>CPI</dt><dd data-cpi>--</dd></div>
        <div><dt>lambda2</dt><dd data-lambda2>--</dd></div>
        <div><dt>H</dt><dd data-entropy>--</dd></div>
        <div><dt>Residual</dt><dd data-residual>--</dd></div>
        <div><dt>Balance</dt><dd data-balance>--</dd></div>
        <div><dt>Sync</dt><dd data-sync>--</dd></div>
      </dl>
    </section>
  `;
  return root.querySelector(".phase-banner");
}

export function renderPhaseBanner(node, phase, metrics) {
  if (!node || !metrics) return;
  node.className = `phase-banner phase-${phase.toLowerCase().replace("_", "-")}`;
  node.querySelector("[data-phase]").textContent = PHASE_LABELS[phase] || phase;
  node.querySelector("[data-k]").textContent = String(metrics.k);
  node.querySelector("[data-cpi]").textContent = metrics.cpi.toFixed(3);
  node.querySelector("[data-lambda2]").textContent = metrics.lambda2.toExponential(2);
  node.querySelector("[data-entropy]").textContent = metrics.entropy.toFixed(3);
  node.querySelector("[data-residual]").textContent = (metrics.residualMass ?? 0).toFixed(3);
  node.querySelector("[data-balance]").textContent = (metrics.clusterBalanceRatio ?? 0).toFixed(3);
  node.querySelector("[data-sync]").textContent = (metrics.syncRatio ?? 0).toFixed(3);
}
