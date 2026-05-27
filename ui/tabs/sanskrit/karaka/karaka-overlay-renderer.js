function resolveContainer(containerOrId) {
  if (typeof containerOrId === "string") {
    return document.getElementById(containerOrId);
  }
  return containerOrId || null;
}

function appendText(parent, tagName, text, className) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  node.textContent = text;
  parent.appendChild(node);
  return node;
}

function appendKarakaRow(container, node) {
  const row = document.createElement("div");
  row.className = "karaka-overlay-node";

  appendText(row, "span", node.karakaLabel, "karaka-badge");
  appendText(row, "strong", node.token || "-", "karaka-link");
  appendText(row, "span", `${node.vibhakti || "-"} -> ${node.karaka || "-"}`);

  const detail = document.createElement("small");
  detail.textContent = `index ${node.index}; source ${node.source}; confidence ${node.confidence}`;
  row.appendChild(detail);

  container.appendChild(row);
}

export function renderKarakaOverlay(containerOrId, overlay) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("karaka-panel");

  appendText(container, "h3", "Kāraka Relation Overlay");

  const diagnostics = overlay?.diagnostics || {};
  const diagnosticsNode = document.createElement("div");
  diagnosticsNode.className = "karaka-diagnostics";
  diagnosticsNode.textContent = [
    `inspected: ${diagnostics.inspectedCount || 0}`,
    `matched: ${diagnostics.matchedCount || 0}`,
    `unmatched: ${diagnostics.unmatchedCount || 0}`,
  ].join(" · ");
  container.appendChild(diagnosticsNode);

  const nodes = Array.isArray(overlay?.nodes) ? overlay.nodes : [];
  if (nodes.length === 0) {
    const empty = document.createElement("div");
    empty.className = "karaka-overlay-node";
    empty.textContent = "No deterministic kāraka relations matched the current morphology transition metadata.";
    container.appendChild(empty);
    return;
  }

  nodes.forEach((node) => appendKarakaRow(container, node));
}
