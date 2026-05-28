import { serializePrakriyaTraceGraph } from "./prakriya-trace-graph.js";

function resolveContainer(containerOrId) {
  if (typeof containerOrId === "string") return document.getElementById(containerOrId);
  return containerOrId || null;
}

function appendText(parent, tagName, text, className) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  node.textContent = String(text ?? "");
  parent.appendChild(node);
  return node;
}

function appendBox(container, className, label, value, detail) {
  const row = document.createElement("div");
  row.className = className;
  appendText(row, "span", label, "prakriya-graph-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

export function renderPrakriyaTraceGraph(containerOrId, graph) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("prakriya-graph-panel");
  appendText(container, "h3", "Prakriya Trace Graph");

  const diagnostics = graph?.diagnostics || {};
  const diagnosticsNode = document.createElement("div");
  diagnosticsNode.className = "prakriya-graph-diagnostics";
  diagnosticsNode.textContent = [
    `nodes: ${diagnostics.nodeCount || 0}`,
    `edges: ${diagnostics.edgeCount || 0}`,
    `overlays: ${diagnostics.overlayCount || 0}`,
    `unresolved: ${diagnostics.unresolvedCount || 0}`,
  ].join(" · ");
  container.appendChild(diagnosticsNode);

  if (!graph) {
    appendBox(container, "prakriya-graph-unresolved", "empty", "No graph available", "Run analysis to render deterministic graph metadata.");
    return;
  }

  const nodes = Array.isArray(graph.nodes) ? [...graph.nodes].sort((left, right) => (left.order || 0) - (right.order || 0)) : [];
  const edges = Array.isArray(graph.edges) ? [...graph.edges].sort((left, right) => (left.order || 0) - (right.order || 0)) : [];
  const overlays = Array.isArray(graph.overlays) ? graph.overlays : [];

  if (nodes.length === 0) appendBox(container, "prakriya-graph-unresolved", "empty", "No graph nodes", "No deterministic trace graph nodes were available.");

  nodes.forEach((node) => {
    appendBox(
      container,
      node.type === "unresolved" ? "prakriya-graph-unresolved" : "prakriya-graph-node",
      node.type,
      node.label,
      `${node.id}; stage ${node.stage}; order ${node.order}`,
    );
  });

  edges.forEach((edge) => {
    appendBox(container, "prakriya-graph-edge", edge.type, `${edge.source} -> ${edge.target}`, edge.label);
  });

  overlays.forEach((overlay) => {
    appendBox(container, "prakriya-graph-stage", overlay.sourceLayer || "overlay", overlay.id, "Attached deterministic overlay annotation.");
  });

  (diagnostics.warnings || []).forEach((warning) => {
    appendBox(container, "prakriya-graph-unresolved", "warning", warning, "Graph projection remains read-only.");
  });

  const preview = document.createElement("pre");
  preview.className = "prakriya-graph-json";
  preview.textContent = serializePrakriyaTraceGraph(graph);
  container.appendChild(preview);
}
