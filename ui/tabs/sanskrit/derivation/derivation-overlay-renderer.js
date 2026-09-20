function appendOverlayRow(container, label, value, detail) {
  const row = document.createElement("div");
  row.className = "inspection-row";

  const title = document.createElement("strong");
  title.textContent = label;

  const body = document.createElement("span");
  body.textContent = String(value ?? "-");

  row.append(title, document.createTextNode(": "), body);

  if (detail) {
    const small = document.createElement("small");
    small.textContent = detail;
    row.appendChild(small);
  }

  container.appendChild(row);
}

function joinOrFallback(items, fallback = "-") {
  return Array.isArray(items) && items.length ? items.join(" ") : fallback;
}

export function renderDerivationOverlayList(container, analysis) {
  if (!container || !analysis) return;

  const overlays = analysis.overlays || {};
  appendOverlayRow(container, "Overlay Summary", "Active", "Deterministic read-only overlay rendering only.");
  appendOverlayRow(
    container,
    "Active Symbolic Classes",
    joinOrFallback(overlays.activeSymbolicClasses),
    "Expanded symbolic classes available to the graph overlay.",
  );
  appendOverlayRow(
    container,
    "Active Topology Nodes",
    joinOrFallback(overlays.activeTopologyNodes),
    "Input-highlighted articulation topology nodes.",
  );

  const sandhiTransitions = overlays.activeSandhiTransitions || [];
  if (sandhiTransitions.length === 0) {
    appendOverlayRow(
      container,
      "Active Sandhi Transitions",
      "-",
      "No deterministic sandhi transition matched the current input boundaries.",
    );
    return;
  }

  sandhiTransitions.forEach((transition, index) => {
    appendOverlayRow(
      container,
      `Sandhi Overlay ${index + 1}`,
      `${transition.boundary} -> ${transition.result}`,
      transition.ruleId || "matched deterministic transition",
    );
  });
}
