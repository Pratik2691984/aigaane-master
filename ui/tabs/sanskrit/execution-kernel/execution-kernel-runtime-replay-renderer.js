"use strict";

function freeze(v) {
  return Object.freeze(v);
}

function escapeHtml(v) {
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderStep(step = {}) {
  return [
    "field=" + escapeHtml(step.field || "unknown"),
    "from=" + escapeHtml(step.from),
    "to=" + escapeHtml(step.to),
    "action=" + escapeHtml(step.action || "inspect-change"),
    "execute=false",
    "mutate=false"
  ].join(" | ");
}

function renderRuntimeReplayPanel(plan = {}) {
  const steps = Array.isArray(plan.steps) ? plan.steps : [];
  const warnings = Array.isArray(plan.warnings) ? plan.warnings : [];

  const replayAllowed = plan.replayAllowed === true;

  const status =
    steps.length === 0
      ? "EMPTY"
      : replayAllowed
        ? "READY"
        : "BLOCKED";

  const body = [
    "Replay Mode: " + escapeHtml(plan.replayMode || "inspection-only"),
    "Replay Allowed: " + escapeHtml(replayAllowed),
    "Step Count: " + escapeHtml(plan.stepCount || steps.length || 0),
    "Source Hash: " + escapeHtml(plan.sourceHash || "source-pending"),
    "Target Hash: " + escapeHtml(plan.targetHash || "target-pending"),
    "Warnings:",
    ...warnings.map((w) => "- " + escapeHtml(w)),
    "Steps:",
    ...steps.map(renderStep)
  ].join("\n");

  return freeze({
    title: "Runtime Replay",
    status,
    readOnly: true,
    replayAllowed: false,
    body
  });
}

module.exports = {
  renderRuntimeReplayPanel
};