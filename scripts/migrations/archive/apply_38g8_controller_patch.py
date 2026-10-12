"""Apply Node 38G.8 absent badges for derivation panes. No API/manifest/38H changes."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"

OLD_TIMELINE = """function renderDerivationTimeline(path) {
  const container = byId("derivation-timeline-output");
  clearChildren(container);
  if (!container) return;

  const steps = Array.isArray(path) ? path : [];
  if (steps.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "No derivation path";
    container.appendChild(empty);
    return;
  }

  steps.forEach((step) => {
    const item = document.createElement("li");
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(step?.operation);
    body.textContent = ` ${text(step?.input_state)} -> ${text(step?.output_state)}`;
    meta.textContent = `${text(step?.sutra)} · ${text(step?.sutra_name)} · ${text(step?.engine_node)}`;
    item.append(title, body, meta);
    container.appendChild(item);
  });
}
"""

NEW_TIMELINE = """function renderDerivationTimeline(path) {
  const container = byId("derivation-timeline-output");
  clearChildren(container);
  if (!container) return;

  const steps = Array.isArray(path) ? path : [];
  if (steps.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "derivation_path: absent";
    container.appendChild(empty);
    return;
  }

  steps.forEach((step) => {
    const item = document.createElement("li");
    const title = document.createElement("strong");
    const body = document.createElement("span");
    const meta = document.createElement("small");
    title.textContent = text(step?.operation);
    body.textContent = " " + text(step?.input_state) + " -> " + text(step?.output_state);
    const sutraLabel = step?.sutra ? String(step.sutra) : "sutra: absent";
    const sutraName = step?.sutra ? text(step?.sutra_name) : "";
    meta.textContent = sutraName
      ? sutraLabel + " · " + sutraName + " · " + text(step?.engine_node)
      : sutraLabel + " · " + text(step?.engine_node);
    item.append(title, body, meta);
    container.appendChild(item);
  });
}
"""

OLD_HIST = (
    'appendListItems(byId("derivation-history-output"), payload?.derivation_history, '
    '(step) => `${text(step?.stage)}: ${text(step?.input)} -> ${text(step?.output)} (${text(step?.rule)})`);\n'
)

NEW_HIST = """  const historyContainer = byId("derivation-history-output");
  const history = Array.isArray(payload?.derivation_history) ? payload.derivation_history : [];
  if (historyContainer && history.length === 0) {
    clearChildren(historyContainer);
    const emptyHistory = document.createElement("li");
    emptyHistory.textContent = "derivation_history: absent";
    historyContainer.appendChild(emptyHistory);
  } else {
    appendListItems(historyContainer, history, (step) => `${text(step?.stage)}: ${text(step?.input)} -> ${text(step?.output)} (${text(step?.rule)})`);
  }
"""


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if 'empty.textContent = "derivation_path: absent"' in text and "derivation_history: absent" in text:
        print("already patched")
        return 0
    missing = []
    if OLD_TIMELINE not in text:
        missing.append("timeline")
    if OLD_HIST not in text:
        missing.append("history")
    if missing:
        print("target blocks missing: " + ",".join(missing))
        return 1
    text = text.replace(OLD_TIMELINE, NEW_TIMELINE, 1)
    text = text.replace(OLD_HIST, NEW_HIST, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("patched " + str(TARGET))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())