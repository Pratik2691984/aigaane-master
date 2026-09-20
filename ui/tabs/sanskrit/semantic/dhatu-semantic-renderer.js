function appendSemanticRow(container, label, value, detail) {
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

export function renderDhatuSemanticList(container, analysis) {
  if (!container || !analysis) return;

  const clusters = analysis.clusters || [];
  appendSemanticRow(
    container,
    "Semantic Clusters",
    clusters.map((cluster) => cluster.label).join(" ") || "-",
    "Read-only deterministic placeholder clusters.",
  );

  (analysis.graph?.edges || []).forEach((edge) => {
    appendSemanticRow(
      container,
      edge.relation,
      `${edge.source} -> ${edge.target}`,
      "Deterministic semantic graph edge.",
    );
  });

  const derivationSummary = analysis.derivationOverlay?.summary || {};
  appendSemanticRow(
    container,
    "Derivation Overlay Summary",
    `${derivationSummary.nodeCount || 0} nodes / ${derivationSummary.edgeCount || 0} edges`,
    "Integrated structural derivation overlay summary.",
  );
}
