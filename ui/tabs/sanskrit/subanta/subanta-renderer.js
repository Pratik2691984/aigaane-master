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
  appendText(row, "span", label, "subanta-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

export function renderSubanta(containerOrId, generation) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("subanta-panel");

  appendText(container, "h3", "Subanta Morphology Generator");

  const diagnostics = generation?.diagnostics || {};
  const diagnosticsNode = document.createElement("div");
  diagnosticsNode.className = "subanta-diagnostics";
  diagnosticsNode.textContent = diagnostics.supported
    ? "supported deterministic generation"
    : `unsupported deterministic generation; ${(diagnostics.warnings || []).length} warnings`;
  container.appendChild(diagnosticsNode);

  if (!generation) {
    appendBox(container, "subanta-unsupported", "empty", "No generation available", "Run analysis to render deterministic subanta metadata.");
    return;
  }

  const input = generation.input || {};
  if (generation.matched) {
    appendBox(container, "subanta-form", "form", generation.generatedForm, `${input.stem}; ${input.linga}; ${input.vibhakti}; ${input.vacana}`);
    appendBox(container, "subanta-suffix", "suffix", generation.suffix, generation.ruleId);
  } else {
    appendBox(container, "subanta-unsupported", "unsupported", input.stem || "no stem", "No suffix was inferred for this combination.");
  }

  (generation.trace || []).forEach((node) => {
    appendBox(container, "subanta-trace", `step ${node.step}`, node.after, `${node.operation}: ${node.before}`);
  });

  (generation.reversePreview || []).forEach((node) => {
    appendBox(container, "subanta-reverse", "reverse", node.generated, `structural preview: ${node.reconstructedStem} + ${node.suffix}`);
  });

  (diagnostics.warnings || []).forEach((warning) => {
    appendBox(container, "subanta-unsupported", "warning", warning, "Generation remains read-only.");
  });
}
