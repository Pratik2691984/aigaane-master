function labelCount(label, value) {
  return `${label}: ${Number(value || 0)}`;
}

export function summarizeReplayDiff(diff = {}) {
  const summary = diff.summary || {};
  return [
    labelCount("added steps", summary.addedSteps),
    labelCount("removed steps", summary.removedSteps),
    labelCount("changed steps", summary.changedSteps),
    labelCount("sutra changes", (diff.sutraDiffs || []).length),
    labelCount("branch changes", (diff.branchDiffs || []).length),
    labelCount("semantic changes", (diff.semanticDiffs || []).length),
  ].join(" · ");
}

export function renderReplayComparison(container, diff = {}) {
  if (!container) return;
  container.textContent = "";
  const panel = document.createElement("div");
  panel.className = "replay-comparison";
  const title = document.createElement("strong");
  title.textContent = `${diff.baseReplayId || "base"} -> ${diff.targetReplayId || "target"}`;
  const body = document.createElement("span");
  body.textContent = summarizeReplayDiff(diff);
  panel.append(title, body);
  container.appendChild(panel);
}

export default { renderReplayComparison, summarizeReplayDiff };
