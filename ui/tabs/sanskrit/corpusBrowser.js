/**
 * Read-only Corpus Browser. Loads seed JSON in memory. No write APIs.
 */

const DHATU_IDS = Array.from({ length: 37 }, (_, i) => `dhatu-${String(i + 1).padStart(3, "0")}`);
const SUTRA_IDS = ["sutra-001", "sutra-002", "sutra-003", "sutra-004", "sutra-005"];
const STOTRA_IDS = ["stotra-001", "stotra-002", "stotra-003"];

const FORBIDDEN = /import|save canonical|promote|edit|delete/i;

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
  const blob = JSON.stringify(rec).toLowerCase();
  return blob.includes(q.toLowerCase());
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

  function setView(next) {
    view = next;
    tabs.forEach((t) => t.classList.toggle("active", t.dataset.corpusView === view));
    if (searchWrap) searchWrap.hidden = view !== "search";
    draw();
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
      panel.innerHTML = `<pre class="corpus-trace">${selected ? JSON.stringify(selected, null, 2) : "Select a record from Dhātu / Sūtra / Stotra."}</pre>`;
      return;
    }
    const source = view === "search" ? index.all.filter((r) => matches(r, query)) : index[view] || [];
    renderList(panel, source, (rec) => {
      selected = rec;
      setView("trace");
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

  const html = root.innerHTML;
  if (FORBIDDEN.test(html)) {
    console.warn("[corpus] forbidden mutation control text detected");
  }

  return {
    getIndex: () => index,
    destroy() {
      index = { dhatu: [], sutra: [], stotra: [], all: [], counts: { dhatu: 0, sutra: 0, stotra: 0, total: 0 } };
    },
  };
}
