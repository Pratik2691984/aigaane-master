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
  appendText(row, "span", label, "tinanta-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

export function renderTinanta(containerOrId, generation) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("tinanta-panel");

  appendText(container, "h3", "Tiṅanta Morphology Generator");

  const diagnostics = generation?.diagnostics || {};
  const diagnosticsNode = document.createElement("div");
  diagnosticsNode.className = "tinanta-diagnostics";
  diagnosticsNode.textContent = diagnostics.supported
    ? "supported deterministic generation"
    : `unsupported deterministic generation; ${(diagnostics.warnings || []).length} warnings`;
  container.appendChild(diagnosticsNode);

  if (!generation) {
    appendBox(container, "tinanta-unsupported", "empty", "No generation available", "Run analysis to render deterministic tiṅanta metadata.");
    return;
  }

  const input = generation.input || {};
  if (generation.matched) {
    appendBox(container, "tinanta-form", "form", generation.generatedForm, `${input.lakara}; ${input.pada}; ${input.purusha}; ${input.vacana}`);
    appendBox(container, "tinanta-root", "dhatu", input.dhatu, generation.ruleId);
    appendBox(container, "tinanta-stem", "stem", generation.presentStem, "Direct deterministic present-stem metadata.");
    appendBox(container, "tinanta-affix", "affix", generation.affix, "Direct deterministic parasmaipada ending metadata.");
  } else {
    appendBox(container, "tinanta-unsupported", "unsupported", input.dhatu || "no dhatu", "No tiṅanta form was inferred.");
  }

  (generation.trace || []).forEach((node) => {
    appendBox(container, "tinanta-trace", `step ${node.step}`, node.after, `${node.operation}: ${node.before}`);
  });

  (generation.reversePreview || []).forEach((node) => {
    const reconstructed = node.reconstructed || {};
    appendBox(
      container,
      "tinanta-reverse",
      "reverse",
      node.generated,
      `${reconstructed.dhatu || "-"}; ${reconstructed.lakara || "-"}; ${reconstructed.pada || "-"}; ${reconstructed.purusha || "-"}; ${reconstructed.vacana || "-"}`,
    );
  });

  (diagnostics.warnings || []).forEach((warning) => {
    appendBox(container, "tinanta-unsupported", "warning", warning, "Generation remains read-only.");
  });
}

export function renderTinantaParadigm(containerOrId, paradigm) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("tinanta-panel");
  appendText(container, "h3", "Tiṅanta Paradigm");

  const forms = Array.isArray(paradigm?.forms) ? paradigm.forms : [];
  if (forms.length === 0) {
    appendBox(container, "tinanta-unsupported", "empty", "No paradigm forms", "Only bhū, gam, and nī laṭ/parasmaipada are currently supported.");
    return;
  }

  const table = document.createElement("div");
  table.className = "tinanta-paradigm";
  forms.forEach((item) => {
    const input = item.input || {};
    appendBox(table, "tinanta-form", `${input.purusha} ${input.vacana}`, item.generatedForm, `${item.presentStem}+${item.affix}`);
  });
  container.appendChild(table);

  const diagnostics = paradigm.diagnostics || {};
  const diagnosticsNode = document.createElement("div");
  diagnosticsNode.className = "tinanta-diagnostics";
  diagnosticsNode.textContent = `forms: ${diagnostics.formCount || forms.length}`;
  container.appendChild(diagnosticsNode);
}
