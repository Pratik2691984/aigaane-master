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
    `rhythm: ${diagnostics.padaRhythmCandidateCount || 0}`,
    `caesura: ${diagnostics.caesuraCandidateCount || 0}`,
    `struct nodes: ${diagnostics.structuralGraphNodeCount || 0}`,
    `struct edges: ${diagnostics.structuralGraphEdgeCount || 0}`,
    `flow: ${diagnostics.recitationFlowCandidateCount || 0}`,
    `breath: ${diagnostics.breathWindowCandidateCount || 0}`,
    `timing: ${diagnostics.recitationTimingCandidateCount || 0}`,
    `pāda timing: ${diagnostics.padaTimingSummaryCount || 0}`,
    `timing mātrā: ${diagnostics.timingMatraTotal || 0}`,
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

    const rhythms = Array.isArray(overlay?.padaRhythmCandidates) ? overlay.padaRhythmCandidates : [];
  rhythms.forEach((rhythm) => {
    appendBox(
      container,
      "chandas-rhythm-candidate",
      "pāda rhythm",
      rhythm.rhythm,
      `${rhythm.matraPattern} mātrā pattern`,
    );
  });

  const caesuras = Array.isArray(overlay?.caesuraCandidates) ? overlay.caesuraCandidates : [];
  caesuras.forEach((caesura) => {
    appendBox(
      container,
      "chandas-caesura-candidate",
      "caesura",
      `after syllable ${caesura.afterSyllableIndex}`,
      "Candidate midpoint pause only; no poetic intent is inferred.",
    );
  });

  const structuralNodes = Array.isArray(overlay?.structuralGraphNodes) ? overlay.structuralGraphNodes : [];
  const structuralEdges = Array.isArray(overlay?.structuralGraphEdges) ? overlay.structuralGraphEdges : [];

  if (structuralNodes.length > 0 || structuralEdges.length > 0) {
    appendBox(
      container,
      "chandas-structural-graph",
      "structural graph",
      `${structuralNodes.length} nodes · ${structuralEdges.length} edges`,
      "Deterministic projection from explicit chandas overlay components.",
    );
  }

    const flows = Array.isArray(overlay?.recitationFlowCandidates) ? overlay.recitationFlowCandidates : [];
  flows.forEach((flow) => {
    appendBox(
      container,
      "chandas-recitation-flow",
      "recitation flow",
      `${flow.fromPadaId} → ${flow.toPadaId}`,
      "Candidate sequencing only; no recitation quality is inferred.",
    );
  });

  const breathWindows = Array.isArray(overlay?.breathWindowCandidates) ? overlay.breathWindowCandidates : [];
  breathWindows.forEach((window) => {
    appendBox(
      container,
      "chandas-breath-window",
      "breath window",
      `after syllable ${window.afterSyllableIndex}`,
      "Candidate pause window only; no chanting instruction is inferred.",
    );
  });

    const timingCandidates = Array.isArray(overlay?.recitationTimingCandidates) ? overlay.recitationTimingCandidates : [];
  const padaTimings = Array.isArray(overlay?.padaTimingSummaries) ? overlay.padaTimingSummaries : [];

  if (timingCandidates.length > 0) {
    appendBox(
      container,
      "chandas-recitation-timing",
      "timing projection",
      `${timingCandidates.length} syllables`,
      "Mātrā projection only; no audio tempo or chanting-speed inference is claimed.",
    );
  }

  padaTimings.forEach((timing) => {
    appendBox(
      container,
      "chandas-pada-timing",
      "pāda timing",
      `${timing.durationMatra} mātrā`,
      `syllables ${timing.startIndex}-${timing.endIndex}`,
    );
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
