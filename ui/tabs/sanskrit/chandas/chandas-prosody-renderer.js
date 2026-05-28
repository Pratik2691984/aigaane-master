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
  appendText(row, "span", label, "chandas-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

export function renderChandasProsodyOverlay(containerOrId, overlay) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("chandas-panel");

  appendText(container, "h3", "Chandas Prosody Inspection");

  const diagnostics = overlay?.diagnostics || {};
  const diagnosticsNode = document.createElement("div");
  diagnosticsNode.className = "chandas-diagnostics";
  diagnosticsNode.textContent = [
    `syllables: ${diagnostics.syllableCount || 0}`,
    `laghu: ${diagnostics.laghuCount || 0}`,
    `guru: ${diagnostics.guruCount || 0}`,
    `mātrā: ${diagnostics.matraTotal || 0}`,
    `gaṇa: ${diagnostics.ganaCount || 0}`,
    `pāda: ${diagnostics.padaCandidateCount || 0}`,
    `metre: ${diagnostics.metreCandidateCount || 0}`,
    `unresolved: ${diagnostics.unresolvedCount || 0}`,
  ].join(" · ");
  container.appendChild(diagnosticsNode);

  const syllables = Array.isArray(overlay?.syllables) ? overlay.syllables : [];
  syllables.forEach((syllable) => {
    appendBox(container, "chandas-syllable", syllable.weight, syllable.text, `${syllable.reason}; ${syllable.matra} mātrā`);
  });

  const ganas = Array.isArray(overlay?.ganas) ? overlay.ganas : [];
  ganas.forEach((gana) => {
    appendBox(container, "chandas-gana", gana.gana, gana.pattern, gana.syllableIds.join(" "));
  });

  const padas = Array.isArray(overlay?.padaCandidates) ? overlay.padaCandidates : [];
  padas.forEach((pada) => {
    appendBox(container, "chandas-pada", "pāda", `${pada.startIndex}-${pada.endIndex}`, `${pada.matraCount} mātrā`);
  });

  const metres = Array.isArray(overlay?.metreCandidates) ? overlay.metreCandidates : [];

if (metres.length > 0) {
  appendBox(
    container,
    "chandas-metre-warning",
    "candidate only",
    `${diagnostics.syllableCount || 0} syllables`,
    "Metre candidates are deterministic syllable-count matches only; no authoritative scansion is claimed.",
  );
}

metres.forEach((metre) => {
  appendBox(
    container,
    "chandas-metre-candidate",
    metre.label,
    `${metre.totalSyllables} syllables`,
    `${metre.padaCount} pāda${metre.padaCount === 1 ? "" : "s"} · ${metre.syllablesPerPada || "variable"} syllables/pāda`,
  );
});

if (metres.length === 0 && syllables.length > 0) {
  appendBox(
    container,
    "chandas-metre-warning",
    "metre",
    "No exact candidate",
    "No registered metre matched the explicit syllable count.",
  );
}

  if ((diagnostics.unresolvedCount || 0) > 0) {
    appendBox(container, "chandas-unresolved", "unresolved", `${diagnostics.unresolvedCount} trailing syllables`, "No canonical metre is guessed.");
  }

  if (syllables.length === 0) {
    appendBox(container, "chandas-unresolved", "empty", "No syllables available", "No unrestricted metre inference was attempted.");
  }
}
