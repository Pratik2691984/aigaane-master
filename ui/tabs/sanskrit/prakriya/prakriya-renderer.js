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
  appendText(row, "span", label, "prakriya-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

export function renderPrakriya(containerOrId, execution) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("prakriya-panel");
  appendText(container, "h3", "Prakriya Composition Pipeline");

  const diagnostics = execution?.diagnostics || {};
  const diagnosticsNode = document.createElement("div");
  diagnosticsNode.className = "prakriya-diagnostics";
  diagnosticsNode.textContent = [
    `padas: ${diagnostics.generatedPadaCount || 0}`,
    `sandhi: ${diagnostics.sandhiAppliedCount || 0}`,
    `unresolved: ${diagnostics.unresolvedCount || 0}`,
  ].join(" · ");
  container.appendChild(diagnosticsNode);

  if (!execution) {
    appendBox(container, "prakriya-unresolved", "empty", "No prakriya execution", "Run analysis to render deterministic composition metadata.");
    return;
  }

  const padas = Array.isArray(execution.generatedPadas) ? execution.generatedPadas : [];
  if (padas.length === 0) {
    appendBox(container, "prakriya-unresolved", "empty", "No padas generated", "No deterministic components were available.");
  }

  padas.forEach((pada) => {
    appendBox(
      container,
      pada.generatedForm ? "prakriya-pada" : "prakriya-unresolved",
      pada.sourceType,
      pada.generatedForm || "unresolved",
      pada.sourceRuleId || (pada.diagnostics?.warnings || []).join("; "),
    );
  });

  const sentence = execution.sentenceAssembly || {};
  appendBox(container, "prakriya-sentence", "pre-sandhi", sentence.preSandhiText || "-", "Structural pada assembly.");
  appendBox(container, "prakriya-sentence", "post-sandhi", sentence.postSandhiText || "-", "Deterministic sandhi preview where supported.");

  (execution.stages || []).forEach((stage) => {
    appendBox(container, "prakriya-stage", stage.id, stage.label, stage.description);
  });

  (execution.trace || []).forEach((node) => {
    appendBox(container, "prakriya-trace", `step ${node.step}`, node.after, `${node.stage}; ${node.operation}`);
  });

  (execution.reversePreview || []).forEach((node) => {
    appendBox(container, "prakriya-reverse", "reverse", node.generated, JSON.stringify(node.reconstructed || ""));
  });

  (diagnostics.warnings || []).forEach((warning) => {
    appendBox(container, "prakriya-unresolved", "warning", warning, "Composition remains read-only.");
  });
}
