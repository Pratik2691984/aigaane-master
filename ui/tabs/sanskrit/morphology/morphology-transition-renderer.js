function appendMorphologyRow(container, label, value, detail) {
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

function renderNodeGroup(container, label, nodes) {
  appendMorphologyRow(
    container,
    label,
    nodes.map((node) => node.label).join(" ") || "-",
    "Deterministic read-only morphology metadata.",
  );
}

export function renderMorphologyTransitionList(container, analysis) {
  if (!container || !analysis) return;

  const morphology = analysis.morphology || {};
  renderNodeGroup(container, "Roots", morphology.roots || []);
  renderNodeGroup(container, "Stems", morphology.stems || []);
  renderNodeGroup(container, "Suffixes", morphology.suffixes || []);
  renderNodeGroup(container, "Surface Forms", morphology.surfaceForms || []);

  (analysis.graph?.edges || []).forEach((edge) => {
    appendMorphologyRow(
      container,
      edge.relation,
      `${edge.source} -> ${edge.target}`,
      "Placeholder structural transition edge.",
    );
  });

  const summary = analysis.summary || {};
  appendMorphologyRow(
    container,
    "Overlay Summary",
    `${summary.traceNodeCount || 0} trace nodes; ${summary.semanticNodeCount || 0} semantic nodes`,
    "Deterministic read-only rendering only.",
  );
}
