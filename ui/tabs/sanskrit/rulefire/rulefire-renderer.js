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
  appendText(row, "span", label, "rulefire-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
  return row;
}

function countText(items, label) {
  return `${Array.isArray(items) ? items.length : 0} ${label}`;
}

export function renderRulefire(containerOrId, rulefire) {
  const container = resolveContainer(containerOrId);
  if (!container) return;
  clear(container);
  container.classList.add("rulefire-panel");
  appendText(container, "h3", "Rule-Firing");

  if (!rulefire || typeof rulefire !== "object") {
    appendRow(container, "rulefire-unresolved", "empty", "No rulefire execution", "Run analysis to inspect deterministic rule firing.");
    return;
  }

  const diagnostics = rulefire.diagnostics || {};
  appendRow(
    container,
    "rulefire-diagnostics",
    "diagnostics",
    `fired ${diagnostics.firedCount || 0}`,
    `${diagnostics.snapshotCount || 0} snapshots; ${diagnostics.unresolvedCount || 0} unresolved`,
  );

  const firedRules = Array.isArray(rulefire.firedRules) ? rulefire.firedRules : [];
  if (!firedRules.length) appendRow(container, "rulefire-unresolved", "rules", "No deterministic rule matched", "No hidden grammar inference was attempted.");
  firedRules.forEach((rule) => {
    appendRow(
      container,
      "rulefire-rule",
      rule.category || "rule",
      rule.ruleId,
      `${rule.stage}; priority ${rule.priority}; ${rule.confidence}`,
    );
  });

  (Array.isArray(rulefire.snapshots) ? rulefire.snapshots : []).forEach((snapshot) => {
    appendRow(
      container,
      "rulefire-snapshot",
      `snapshot ${snapshot.order}`,
      snapshot.id,
      snapshot.causedByRuleId || "initial state",
    );
  });

  (Array.isArray(rulefire.trace) ? rulefire.trace : []).forEach((trace) => {
    appendRow(container, "rulefire-trace", `step ${trace.step}`, trace.ruleId || trace.operation, `${trace.before || "-"} -> ${trace.after || "-"}`);
  });

  const graph = rulefire.graphProjection || {};
  appendRow(
    container,
    "rulefire-graph",
    "graph",
    countText(graph.nodes, "nodes"),
    countText(graph.edges, "edges"),
  );

  (Array.isArray(rulefire.reversePreview) ? rulefire.reversePreview : []).forEach((preview) => {
    appendRow(container, "rulefire-trace", "reverse", preview.ruleId, "Structural preview only.");
  });

  (diagnostics.warnings || []).forEach((warning) => {
    appendRow(container, "rulefire-unresolved", "warning", warning, "Rulefire remains read-only.");
  });
}

