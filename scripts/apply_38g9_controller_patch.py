"""Apply Node 38G.9 Chandas envelope sync. No API/manifest/38H changes."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"

OLD_START = """function renderChandasProsodyPanel(inputText = "") {
  const container = byId("chandas-prosody-panel");
  if (!container) return;

  const morphologyTransitions = inspectMorphologyTransitions(inputText);
"""

NEW_START = """function isFragmentStanzaMeter(meter) {
  const value = String(meter || "");
  if (!value || value === "-") return true;
  return value.indexOf("Fragment") >= 0
    || value.indexOf("not determined") >= 0
    || value.indexOf("not authoritatively") >= 0;
}

function renderAuthoritativeChandasHeader(container) {
  if (!container) return;
  const existing = container.querySelector("[data-chandas-envelope]");
  if (existing) existing.remove();

  const wrap = document.createElement("div");
  wrap.setAttribute("data-chandas-envelope", "true");
  wrap.className = "chandas-envelope-header";

  const env = latestAnalyzeEnvelope;
  const padas = Array.isArray(env?.padas) ? env.padas : [];
  const meter = env?.overall_stanza_meter;
  const live = Boolean(env && padas.length > 0 && meter && !isFragmentStanzaMeter(meter));

  const status = document.createElement("p");
  if (live) {
    status.textContent = "chandas: live";
  } else if (!env || padas.length === 0) {
    status.textContent = "chandas: absent";
  } else {
    status.textContent = String(meter);
  }
  wrap.appendChild(status);

  const meterRow = document.createElement("p");
  meterRow.textContent = "overall_stanza_meter: " + (typeof meter === "string" && meter ? meter : "chandas: absent");
  wrap.appendChild(meterRow);

  const matraRow = document.createElement("p");
  matraRow.textContent = "total_matra_count: " + String(Number(env?.total_matra_count) || 0);
  wrap.appendChild(matraRow);

  const preview = document.createElement("p");
  preview.textContent = "static-preview";
  wrap.appendChild(preview);

  container.insertBefore(wrap, container.firstChild);
}

function renderChandasProsodyPanel(inputText = "") {
  const container = byId("chandas-prosody-panel");
  if (!container) return;

  const trimmedInput = String(inputText || "").trim();
  const envelopePadas = Array.isArray(latestAnalyzeEnvelope?.padas) ? latestAnalyzeEnvelope.padas : [];
  if (!trimmedInput && envelopePadas.length === 0) {
    clearChildren(container);
    const emptyBadge = document.createElement("p");
    emptyBadge.textContent = "chandas: absent";
    container.appendChild(emptyBadge);
    return;
  }

  const morphologyTransitions = inspectMorphologyTransitions(inputText);
"""

OLD_END = """  container.appendChild(governanceHost);
}
"""

NEW_END = """  container.appendChild(governanceHost);
  renderAuthoritativeChandasHeader(container);
}
"""


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if "function renderAuthoritativeChandasHeader" in text and "chandas: absent" in text:
        print("already patched")
        return 0
    missing = []
    if OLD_START not in text:
        missing.append("start")
    if OLD_END not in text:
        missing.append("end")
    if missing:
        print("target blocks missing: " + ",".join(missing))
        return 1
    text = text.replace(OLD_START, NEW_START, 1)
    text = text.replace(OLD_END, NEW_END, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("patched " + str(TARGET))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())