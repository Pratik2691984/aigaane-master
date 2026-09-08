/**
 * Read-only Corpus Browser. Loads seed JSON in memory. No write APIs.
 */

import { callDerivation } from '../../../shared/derivationFallback.js';

const DHATU_IDS = Array.from({ length: 37 }, (_, i) => `dhatu-${String(i + 1).padStart(3, "0")}`);
const SUTRA_IDS = ["sutra-001", "sutra-002", "sutra-003", "sutra-004", "sutra-005"];
const STOTRA_IDS = ["stotra-001", "stotra-002", "stotra-003"];

async function loadJson(path) {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(path);
  return res.json();
}

export async function loadCorpusIndex() {
  const dhatu = await Promise.all(DHATU_IDS.map((id) => loadJson(`/corpus/dhatu/${id}.json`)));
  const sutra = await Promise.all(SUTRA_IDS.map((id) => loadJson(`/corpus/sutra/${id}.json`)));
  const stotra = await Promise.all(STOTRA_IDS.map((id) => loadJson(`/corpus/stotra/${id}.json`)));
  return {
    dhatu,
    sutra,
    stotra,
    all: [...dhatu, ...sutra, ...stotra],
    counts: { dhatu: dhatu.length, sutra: sutra.length, stotra: stotra.length, total: dhatu.length + sutra.length + stotra.length },
  };
}

function label(rec) {
  return rec.root || rec.text || rec.title || rec.id;
}

function matches(rec, q) {
  if (!q) return true;
  return JSON.stringify(rec).toLowerCase().includes(q.toLowerCase());
}

function renderList(panel, items, onSelect) {
  const ul = document.createElement("ul");
  ul.className = "corpus-list";
  items.forEach((rec) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = `${rec.id} — ${label(rec)}`;
    btn.addEventListener("click", () => onSelect(rec));
    li.appendChild(btn);
    ul.appendChild(li);
  });
  panel.innerHTML = "";
  panel.appendChild(ul);
}

function enginesFor(rec) {
  if (rec?.root) return ["verbConjugate", "sandhi", "prakriya"];
  if (rec?.text) return ["sandhi", "prakriya"];
  if (rec?.meter) return ["chandas"];
  return ["sandhi"];
}

export function mountCorpusBrowser(root) {
  if (!root) return { destroy() {} };

  const panel = root.querySelector("#corpusPanel");
  const banner = root.querySelector("#corpusBanner");
  const searchWrap = root.querySelector("#corpusSearchWrap");
  const searchInput = root.querySelector("#corpusSearch");
  const tabs = [...root.querySelectorAll("[data-corpus-view]")];

  let index = { dhatu: [], sutra: [], stotra: [], all: [], counts: { dhatu: 0, sutra: 0, stotra: 0, total: 0 } };
  let view = "dhatu";
  let selected = null;
  let query = "";
  let hooks = [];

  function setView(next) {
    view = next;
    tabs.forEach((t) => t.classList.toggle("active", t.dataset.corpusView === view));
    if (searchWrap) searchWrap.hidden = view !== "search";
    draw();
  }

  async function loadHooks(rec) {
    hooks = [];
    if (!rec) return;
    const jobs = enginesFor(rec).map((engine) => callDerivation(engine, rec));
    hooks = await Promise.all(jobs);
  }

  function draw() {
    if (!panel) return;
    if (view === "preview") {
      panel.innerHTML = `<div class="corpus-preview"><dl>
        <dt>Mode</dt><dd>PREVIEW / READ ONLY</dd>
        <dt>Dhātu</dt><dd>${index.counts.dhatu} / 1400</dd>
        <dt>Sūtra</dt><dd>${index.counts.sutra} / 400</dd>
        <dt>Stotra</dt><dd>${index.counts.stotra} / 200</dd>
        <dt>Loaded</dt><dd>${index.counts.total} / 2000</dd>
        <dt>canonicalWrite</dt><dd>false</dd>
      </dl></div>`;
      return;
    }
    if (view === "trace") {
      const recordBlock = selected ? JSON.stringify(selected, null, 2) : "Select a record from Dhātu / Sūtra / Stotra.";
      const hookBlock = hooks.length ? JSON.stringify(hooks, null, 2) : "No derivation preview yet.";
      panel.innerHTML = `<pre class="corpus-trace">${recordBlock}\n\n--- derivation hooks (read-only) ---\n${hookBlock}</pre>`;
      return;
    }
    const source = view === "search" ? index.all.filter((r) => matches(r, query)) : index[view] || [];
    renderList(panel, source, async (rec) => {
      selected = rec;
      setView("trace");
      try {
        await loadHooks(rec);
      } catch (err) {
        hooks = [{ status: "mock_fallback", canonicalWrite: false, readOnly: true, error: String(err) }];
      }
      if (view === "trace") draw();
    });
  }

  tabs.forEach((t) => t.addEventListener("click", () => setView(t.dataset.corpusView)));
  searchInput?.addEventListener("input", () => {
    query = searchInput.value.trim();
    draw();
  });

  loadCorpusIndex()
    .then((loaded) => {
      index = loaded;
      if (banner) {
        banner.textContent = `[PREVIEW MODE — ${loaded.counts.total} / 2000 RECORDS LOADED — READ ONLY]`;
      }
      draw();
    })
    .catch((err) => {
      if (panel) panel.textContent = `Local fallback: corpus fetch failed (${err.message}). Write flags unchanged.`;
    });

  return {
    getIndex: () => index,
    destroy() {
      index = { dhatu: [], sutra: [], stotra: [], all: [], counts: { dhatu: 0, sutra: 0, stotra: 0, total: 0 } };
    },
  };
}
