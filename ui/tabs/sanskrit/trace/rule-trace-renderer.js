function appendTraceRow(container, label, value, detail) {
  const row = document.createElement("div");
  row.className = "inspection-row";

  const title = document.createElement("strong");
  title.textContent = label;

  const body = document.createElement("span");
  body.textContent = String(value ?? "-");

  row.append(title, document.createTextNode(": "), body);

  if (detail) {
    const small = document.createElement("small");
    small.textContent = detail;
    row.appendChild(small);
  }

  container.appendChild(row);
}

export function renderRuleTraceList(container, analysis) {
  if (!container || !analysis) return;

  (analysis.traceGraph?.nodes || []).forEach((node) => {
    appendTraceRow(
      container,
      node.label,
      node.stage,
      `${node.type}; ${node.id}`,
    );
  });

  (analysis.traceGraph?.edges || []).forEach((edge) => {
    appendTraceRow(
      container,
      edge.relation,
      `${edge.source} -> ${edge.target}`,
      "Deterministic read-only trace edge.",
    );
  });

  const summary = analysis.summary || {};
  appendTraceRow(
    container,
    "Overlay Summary",
    `${summary.sutraReferenceNodeCount || 0} sūtra refs; ${summary.derivationNodeCount || 0} derivation nodes; ${summary.semanticNodeCount || 0} semantic nodes`,
    "Deterministic read-only rendering only.",
  );
}
