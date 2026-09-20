function resolveContainer(containerOrId) {
  if (typeof containerOrId === "string") return document.getElementById(containerOrId);
  return containerOrId || null;
}

function appendText(parent, tagName, text, className) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  node.textContent = text;
  parent.appendChild(node);
  return node;
}

function appendBox(container, className, label, value, detail) {
  const row = document.createElement("div");
  row.className = className;
  appendText(row, "span", label, "sandarbha-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

export function renderSandarbhaContextOverlay(containerOrId, overlay) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("sandarbha-panel");

  appendText(container, "h3", "Sandarbha Context Inspection");

  const diagnostics = overlay?.diagnostics || {};
  const diagnosticsNode = document.createElement("div");
  diagnosticsNode.className = "sandarbha-diagnostics";
  diagnosticsNode.textContent = [
    `tokens: ${diagnostics.tokenCount || 0}`,
    `neighborhoods: ${diagnostics.neighborhoodCount || 0}`,
    `candidates: ${diagnostics.candidateCount || 0}`,
    `edges: ${diagnostics.edgeCount || 0}`,
    `unresolved: ${diagnostics.unresolvedCount || 0}`,
  ].join(" · ");
  container.appendChild(diagnosticsNode);

  const neighborhoods = Array.isArray(overlay?.neighborhoods) ? overlay.neighborhoods : [];
  neighborhoods.forEach((item) => {
    appendBox(container, "sandarbha-neighborhood", item.relation, item.anchor, item.members.join(" -> "));
  });

  const candidates = Array.isArray(overlay?.candidates) ? overlay.candidates : [];
  candidates.forEach((item) => {
    const className = item.candidateType === "pronounAntecedentCandidate"
      || item.relation === "unresolvedContextCandidate"
      ? "sandarbha-unresolved"
      : "sandarbha-candidate";
    appendBox(container, className, item.candidateType, item.token, item.relation);
  });

  const edges = Array.isArray(overlay?.edges) ? overlay.edges : [];
  edges.forEach((edge) => {
    appendBox(container, "sandarbha-edge", edge.relation, `${edge.source} -> ${edge.target}`, edge.label);
  });

  if (neighborhoods.length === 0 && candidates.length === 0 && edges.length === 0) {
    appendBox(container, "sandarbha-unresolved", "empty", "No deterministic context links", "No unrestricted semantic interpretation was attempted.");
  }
}
