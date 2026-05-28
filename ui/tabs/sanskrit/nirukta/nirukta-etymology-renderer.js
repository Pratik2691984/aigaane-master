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
  appendText(row, "span", label, "nirukta-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

export function renderNiruktaOverlay(containerOrId, overlay) {
  const container = resolveContainer(containerOrId);
  if (!container) return;
  clear(container);
  container.classList.add("nirukta-panel");
  appendText(container, "h3", "Nirukta Etymology");

  if (!overlay || typeof overlay !== "object") {
    appendRow(container, "nirukta-unresolved", "empty", "No Nirukta overlay", "Run analysis to inspect deterministic etymology scaffolding.");
    return;
  }

  const diagnostics = overlay.diagnostics || {};
  appendRow(container, "nirukta-diagnostics", "diagnostics", `${diagnostics.candidateCount || 0} candidates`, `${diagnostics.unresolvedCount || 0} unresolved; ${diagnostics.edgeCount || 0} edges`);

  (Array.isArray(overlay.candidates) ? overlay.candidates : []).forEach((candidate) => {
    appendRow(container, "nirukta-candidate", candidate.category, `${candidate.form} -> ${candidate.lemma}`, candidate.gloss);
    appendRow(container, "nirukta-family", "family", candidate.semanticFamily, candidate.lineageType);
    if (candidate.linkedRulefireRules?.length) appendRow(container, "nirukta-entry", "rulefire", candidate.linkedRulefireRules.join(", "), "Linked deterministic rulefire rules.");
    if (candidate.linkedSutraDependencies?.length) appendRow(container, "nirukta-entry", "sutra", candidate.linkedSutraDependencies.join(", "), "Linked deterministic dependency references.");
  });

  (Array.isArray(overlay.edges) ? overlay.edges : []).forEach((edge) => {
    appendRow(container, "nirukta-edge", edge.relation, `${edge.source} -> ${edge.target}`, edge.label);
  });

  (Array.isArray(overlay.unresolved) ? overlay.unresolved : []).forEach((item) => {
    appendRow(container, "nirukta-unresolved", "unresolved", item.form, item.reason);
  });

  (diagnostics.warnings || []).forEach((warning) => {
    appendRow(container, "nirukta-unresolved", "warning", warning, "No authoritative etymology is asserted.");
  });

  const preview = document.createElement("pre");
  preview.className = "nirukta-json";
  preview.textContent = JSON.stringify(overlay, null, 2);
  container.appendChild(preview);
}

