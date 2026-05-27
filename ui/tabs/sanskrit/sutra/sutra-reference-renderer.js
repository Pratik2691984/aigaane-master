function appendSutraReferenceRow(container, label, value, detail) {
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

export function renderSutraReferenceList(container, analysis) {
  if (!container || !analysis) return;

  (analysis.overlay?.nodes || []).forEach((node) => {
    appendSutraReferenceRow(
      container,
      node.referenceCode,
      node.label,
      `${node.type}; ${node.id}`,
    );
  });

  (analysis.overlay?.edges || []).forEach((edge) => {
    appendSutraReferenceRow(
      container,
      edge.relation,
      `${edge.source} -> ${edge.target}`,
      "Deterministic read-only reference edge.",
    );
  });

  appendSutraReferenceRow(
    container,
    "Symbolic Compression Summary",
    `${analysis.symbolicCompression?.summary?.classCount || 0} classes`,
    "Read-only symbolic compression summary integration.",
  );

  appendSutraReferenceRow(
    container,
    "Semantic Graph Summary",
    `${analysis.semanticGraph?.nodes?.length || 0} nodes / ${analysis.semanticGraph?.edges?.length || 0} edges`,
    "Read-only semantic graph summary integration.",
  );
}
