"""Apply Node 38G.2 controller wiring. Does not touch kernel, manifest, or 38H."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "ui" / "tabs" / "sanskrit" / "controller.js"

OLD_IMPORT = '''import { buildCorpusBrowserState, summarizeCorpusResults } from "./corpus/corpus-browser-engine.js";
'''
NEW_IMPORT = '''import { buildCorpusBrowserState, summarizeCorpusResults, computeVirtualWindow, VIRTUAL_CONFIG } from "./corpus/corpus-browser-engine.js";
'''

OLD_STATE = '''let corpusBrowserSection = "preview";
let corpusBrowserSelected = null;
'''
NEW_STATE = '''let corpusBrowserSection = "preview";
let corpusBrowserSelected = null;
let corpusBrowserSummary = { valid: true, results: [], query: "", count: 0 };
let corpusBrowserScrollTop = 0;
let corpusBrowserDerivation = null;
let corpusBrowserRaf = 0;
'''

OLD_BIND = '''function bindCorpusBrowserResultCards() {
  const resultsHost = byId("corpus-browser-results");
  if (!resultsHost) {
    return;
  }
  resultsHost.querySelectorAll(".corpus-browser-card").forEach((card) => {
    card.addEventListener("click", () => {
      corpusBrowserSelected = {
        recordId: card.dataset.recordId || "",
        type: card.dataset.recordType || "",
        text: card.querySelector(".corpus-browser-card-text")?.textContent || ""
      };
      resultsHost.querySelectorAll(".corpus-browser-card.is-selected").forEach((node) => {
        node.classList.remove("is-selected");
      });
      card.classList.add("is-selected");
      const traceHost = byId("corpus-browser-trace");
      const state = buildCorpusBrowserState({ recordCount: Number(byId("corpus-browser-stats")?.dataset.recordCount || 0) }, corpusBrowserSection);
      if (traceHost) {
        traceHost.innerHTML = renderCorpusTrace(state, { query: byId("corpus-browser-search-input")?.value || "" }, corpusBrowserSelected);
      }
    });
  });
}
'''

NEW_BIND = '''function currentCorpusWindow(resultCount) {
  return computeVirtualWindow(resultCount, corpusBrowserScrollTop, VIRTUAL_CONFIG);
}

function paintCorpusBrowserResults(state, summary) {
  const resultsHost = byId("corpus-browser-results");
  const traceHost = byId("corpus-browser-trace");
  if (!resultsHost) {
    return;
  }
  const results = Array.isArray(summary.results) ? summary.results : [];
  const windowState = currentCorpusWindow(results.length);
  const label = state.section || CORPUS_SECTION_LABELS[corpusBrowserSection] || "Preview";
  resultsHost.innerHTML = renderCorpusResults(summary, label, windowState, corpusBrowserSelected && corpusBrowserSelected.recordId);
  const viewport = resultsHost.querySelector(".corpus-results-viewport");
  if (viewport) {
    viewport.scrollTop = corpusBrowserScrollTop;
    viewport.addEventListener("scroll", handleCorpusBrowserScroll, { passive: true });
  }
  if (traceHost) {
    traceHost.innerHTML = renderCorpusTrace(state, summary, corpusBrowserSelected, corpusBrowserDerivation);
  }
  bindCorpusBrowserResultCards();
}

function handleCorpusBrowserScroll(event) {
  const viewport = event.currentTarget;
  corpusBrowserScrollTop = viewport.scrollTop || 0;
  if (corpusBrowserRaf) {
    return;
  }
  corpusBrowserRaf = requestAnimationFrame(() => {
    corpusBrowserRaf = 0;
    const statsHost = byId("corpus-browser-stats");
    const label = CORPUS_SECTION_LABELS[corpusBrowserSection] || "Preview";
    const state = buildCorpusBrowserState({ recordCount: Number(statsHost?.dataset.recordCount || 0) }, label);
    paintCorpusBrowserResults(state, corpusBrowserSummary);
  });
}

async function loadCorpusDerivation(selected) {
  corpusBrowserDerivation = null;
  if (!selected || String(selected.type || "").toLowerCase() !== "dhatu" || !selected.text) {
    return;
  }
  try {
    const response = await fetch("/api/v3/morphology/verb/conjugate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dhatu: selected.text,
        lakara: "lat",
        person: "prathama",
        number: "ekavacana"
      })
    });
    if (!response.ok) {
      return;
    }
    const payload = await response.json();
    corpusBrowserDerivation = payload && Object.prototype.hasOwnProperty.call(payload, "derivation_path")
      ? { derivation_path: payload.derivation_path }
      : { derivation_path: null };
  } catch (_error) {
    corpusBrowserDerivation = { derivation_path: null };
  }
}

function bindCorpusBrowserResultCards() {
  const resultsHost = byId("corpus-browser-results");
  if (!resultsHost) {
    return;
  }
  resultsHost.querySelectorAll(".corpus-browser-card").forEach((card) => {
    card.addEventListener("click", async () => {
      const selectedId = card.dataset.recordId || "";
      const fromMemory = (corpusBrowserSummary.results || []).find((item) => String(item.recordId) === selectedId);
      corpusBrowserSelected = fromMemory || {
        recordId: selectedId,
        type: card.dataset.recordType || "",
        text: card.querySelector(".corpus-browser-card-text")?.textContent || ""
      };
      await loadCorpusDerivation(corpusBrowserSelected);
      const statsHost = byId("corpus-browser-stats");
      const label = CORPUS_SECTION_LABELS[corpusBrowserSection] || "Preview";
      const state = buildCorpusBrowserState({ recordCount: Number(statsHost?.dataset.recordCount || 0) }, label);
      paintCorpusBrowserResults(state, corpusBrowserSummary);
    });
  });
}
'''

OLD_PAINT = '''  if (resultsTitle) {
    resultsTitle.textContent = label + " results";
  }
  resultsHost.innerHTML = renderCorpusResults(normalizedSummary, label);
  if (traceHost) {
    traceHost.innerHTML = renderCorpusTrace(state, normalizedSummary, corpusBrowserSelected);
  }
'''

NEW_PAINT = '''  if (resultsTitle) {
    resultsTitle.textContent = label + " results";
  }
  corpusBrowserSummary = normalizedSummary;
  corpusBrowserScrollTop = 0;
  paintCorpusBrowserResults(state, normalizedSummary);
'''


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if "function paintCorpusBrowserResults" in text and "computeVirtualWindow" in text:
        print("already patched")
        return 0
    missing = []
    if OLD_IMPORT not in text:
        missing.append("import")
    if OLD_STATE not in text:
        missing.append("state")
    if OLD_BIND not in text:
        missing.append("bind")
    if OLD_PAINT not in text:
        missing.append("paint")
    if missing:
        print("target blocks missing: " + ",".join(missing))
        return 1
    text = text.replace(OLD_IMPORT, NEW_IMPORT, 1)
    text = text.replace(OLD_STATE, NEW_STATE, 1)
    text = text.replace(OLD_BIND, NEW_BIND, 1)
    text = text.replace(OLD_PAINT, NEW_PAINT, 1)
    i = text.find("async function fetchCorpusBrowserPayload")
    if i >= 0:
        text = text[:i] + text[i:].replace("  const limit = 24;", "  const limit = 2000;", 1)
    TARGET.write_text(text, encoding="utf-8")
    print(f"patched {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
