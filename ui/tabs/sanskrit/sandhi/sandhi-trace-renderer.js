import { groupSandhiRulesByCategory } from "./sandhi-rule-map.js";

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
  appendText(row, "span", label, "sandhi-badge");
  appendText(row, "strong", value || "-");
  if (detail) appendText(row, "small", detail);
  container.appendChild(row);
}

function renderDiagnostics(container, diagnostics) {
  const node = document.createElement("div");
  node.className = "sandhi-diagnostics";
  node.textContent = [
    `tokens: ${diagnostics.tokenCount || 0}`,
    `transitions: ${diagnostics.transitionCount || 0}`,
    `matched: ${diagnostics.matchedCount || 0}`,
    `unmatched: ${diagnostics.unmatchedCount || 0}`,
  ].join(" · ");
  container.appendChild(node);
}

export function renderSandhiExecution(containerOrId, execution) {
  const container = resolveContainer(containerOrId);
  if (!container) return;

  while (container.firstChild) container.removeChild(container.firstChild);
  container.classList.add("sandhi-panel");

  appendText(container, "h3", "Sandhi Execution Core");
  renderDiagnostics(container, execution?.diagnostics || {});

  const transitions = Array.isArray(execution?.transitions) ? execution.transitions : [];
  if (transitions.length === 0) {
    appendBox(container, "sandhi-unmatched", "empty", "No sandhi boundaries", "At least two tokens are required for execution preview.");
  }

  transitions
    .filter((transition) => transition.matched)
    .forEach((transition) => {
      appendBox(
        container,
        "sandhi-transition",
        transition.category,
        `${transition.originalBoundary} -> ${transition.transformedBoundary}`,
        `${transition.ruleId}; ${transition.sutraReference || "no reference"}; ${transition.confidence}`,
      );
    });

  transitions
    .filter((transition) => !transition.matched)
    .forEach((transition) => {
      appendBox(
        container,
        "sandhi-unmatched",
        "unmatched",
        transition.originalBoundary,
        "Boundary preserved visibly; no rule was inferred.",
      );
    });

  const trace = Array.isArray(execution?.trace) ? execution.trace : [];
  trace.forEach((node) => {
    appendBox(container, "sandhi-trace", `step ${node.step}`, node.after, node.explanation);
  });

  const reversePreview = Array.isArray(execution?.reversePreview) ? execution.reversePreview : [];
  reversePreview.forEach((node) => {
    appendBox(container, "sandhi-reverse", "reverse", node.transformed, `structural preview: ${node.reconstructed}`);
  });

  Object.entries(groupSandhiRulesByCategory()).forEach(([category, rules]) => {
    appendBox(container, "sandhi-rule", category, `${rules.length} deterministic rules`, rules.map((rule) => rule.id).join(", "));
  });
}
