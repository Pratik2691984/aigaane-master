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
  appendText(row, "span", label, "vakya-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

export function renderVakyaDependencyOverlay(containerOrId, overlay) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("vakya-panel");

  appendText(container, "h3", "Vākya Dependency Inspection");

  const diagnostics = overlay?.diagnostics || {};
  const diagnosticsNode = document.createElement("div");
  diagnosticsNode.className = "vakya-diagnostics";
  diagnosticsNode.textContent = [
    `tokens: ${diagnostics.tokenCount || 0}`,
    `anchors: ${diagnostics.anchorCount || 0}`,
    `nodes: ${diagnostics.nodeCount || 0}`,
    `edges: ${diagnostics.edgeCount || 0}`,
    `unresolved: ${diagnostics.unresolvedCount || 0}`,
  ].join(" · ");
  container.appendChild(diagnosticsNode);

  const anchors = Array.isArray(overlay?.anchors) ? overlay.anchors : [];
  if (anchors.length === 0) {
    appendBox(container, "vakya-unresolved", "anchor", "No finite verb anchor", "No dependency edges are guessed.");
  } else {
    anchors.forEach((anchor) => {
      appendBox(
        container,
        "vakya-anchor",
        anchor.anchorType,
        anchor.token,
        `index ${anchor.index}; ${anchor.source}; ${anchor.confidence}`,
      );
    });
  }

  const edges = Array.isArray(overlay?.edges) ? overlay.edges : [];
  if (edges.length === 0) {
    appendBox(container, "vakya-edge", "dependencies", "No deterministic dependency edges", "Edges require explicit kāraka metadata and a finite verb anchor.");
  } else {
    edges.forEach((edge) => {
      appendBox(container, "vakya-edge", edge.relation, `${edge.source} -> ${edge.target}`, edge.label);
    });
  }

  const unresolved = (Array.isArray(overlay?.nodes) ? overlay.nodes : []).filter((node) => node.role === "unresolvedCandidate");
  if (unresolved.length > 0) {
    unresolved.forEach((node) => {
      appendBox(container, "vakya-unresolved", "unresolved", node.token, `${node.karaka || "-"}; ${node.morphology || "-"}`);
    });
  }

  if (anchors.length === 0 && edges.length === 0 && unresolved.length === 0) {
    appendBox(container, "vakya-node", "empty", "No dependency candidates", "No deterministic metadata was available for inspection.");
  }
}
