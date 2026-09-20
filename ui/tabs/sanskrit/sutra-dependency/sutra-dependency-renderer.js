function resolveContainer(containerOrId) {
  if (typeof containerOrId === "string") return document.getElementById(containerOrId);
  return containerOrId || null;
}

function clear(node) {
  while (node?.firstChild) node.removeChild(node.firstChild);
}

function appendText(parent, tagName, text, className) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  node.textContent = String(text ?? "");
  parent.appendChild(node);
  return node;
}

function appendRow(container, className, label, value, detail) {
  const row = document.createElement("div");
  row.className = className;
  appendText(row, "span", label, "sutra-dependency-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

function groupByStage(nodes) {
  return nodes.reduce((groups, node) => {
    const stage = node.stage || "unresolved";
    groups[stage] = groups[stage] || 0;
    groups[stage] += 1;
    return groups;
  }, {});
}

export function renderSutraDependency(containerOrId, dependencyGraph) {
  const container = resolveContainer(containerOrId);
  if (!container) return;
  clear(container);
  container.classList.add("sutra-dependency-panel");
  appendText(container, "h3", "Sutra Dependency");

  if (!dependencyGraph || typeof dependencyGraph !== "object") {
    appendRow(container, "sutra-dependency-unresolved", "empty", "No dependency graph", "Run analysis to inspect deterministic sutra dependencies.");
    return;
  }

  const diagnostics = dependencyGraph.diagnostics || {};
  appendRow(
    container,
    "sutra-dependency-diagnostics",
    "diagnostics",
    `${diagnostics.nodeCount || 0} nodes`,
    `${diagnostics.edgeCount || 0} edges; ${diagnostics.unresolvedCount || 0} unresolved`,
  );

  const nodes = Array.isArray(dependencyGraph.nodes) ? dependencyGraph.nodes : [];
  const edges = Array.isArray(dependencyGraph.edges) ? dependencyGraph.edges : [];
  if (!nodes.length) appendRow(container, "sutra-dependency-unresolved", "nodes", "No dependency nodes", "No deterministic dependency rules were selected.");

  Object.entries(groupByStage(nodes)).forEach(([stage, count]) => {
    appendRow(container, "sutra-dependency-stage", "stage", stage, `${count} nodes`);
  });

  nodes.forEach((node) => {
    appendRow(container, "sutra-dependency-node", node.nodeType || "node", node.label || node.id, node.ruleId || node.referenceId || node.stage);
  });

  edges.forEach((edge) => {
    appendRow(container, "sutra-dependency-edge", edge.dependencyType || "edge", `${edge.source} -> ${edge.target}`, edge.label);
  });

  (Array.isArray(dependencyGraph.unresolved) ? dependencyGraph.unresolved : []).forEach((item) => {
    appendRow(container, "sutra-dependency-unresolved", "unresolved", item.referenceId, item.reason);
  });

  (diagnostics.warnings || []).forEach((warning) => {
    appendRow(container, "sutra-dependency-unresolved", "warning", warning, "Dependency graph remains read-only.");
  });

  const preview = document.createElement("pre");
  preview.className = "sutra-dependency-json";
  preview.textContent = JSON.stringify(dependencyGraph, null, 2);
  container.appendChild(preview);
}

