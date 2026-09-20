function freeze(v) {
  return Object.freeze(v);
}

function escapeHtml(v) {
  var amp = String.fromCharCode(38) + "amp;";
  var lt = String.fromCharCode(38) + "lt;";
  var gt = String.fromCharCode(38) + "gt;";
  var quot = String.fromCharCode(38) + "quot;";
  return String(v)
    .replace(/&/g, amp)
    .replace(/</g, lt)
    .replace(/>/g, gt)
    .replace(new RegExp(String.fromCharCode(34), "g"), quot);
}

function typeClass(type) {
  var value = String(type || "").toLowerCase();
  if (value === "dhatu" || value === "sutra" || value === "stotra") {
    return "corpus-type-" + value;
  }
  return "corpus-type-unknown";
}

function renderCorpusStats(state, summary) {
  state = state || {};
  summary = summary || {};
  var recordCount = Number(state.recordCount || 0);
  var matchCount = Number(summary.count || 0);
  var status = summary.valid === false ? "Blocked" : "Ready";
  return "<article class='corpus-browser-stat'><span>Indexed records</span><strong>" + escapeHtml(recordCount) + "</strong></article><article class='corpus-browser-stat'><span>Active section</span><strong>" + escapeHtml(state.section || "Search") + "</strong></article><article class='corpus-browser-stat'><span>Matches</span><strong>" + escapeHtml(matchCount) + "</strong></article><article class='corpus-browser-stat'><span>Status</span><strong>" + escapeHtml(status) + "</strong></article>";
}

function renderCorpusNav(state) {
  state = state || {};
  var sections = Array.isArray(state.sections) ? state.sections : [];
  return sections.map(function (name) {
    var active = name === state.section ? " is-active" : "";
    var slug = String(name).toLowerCase();
    return "<button type='button' class='corpus-browser-nav-btn" + active + "' data-corpus-section='" + escapeHtml(slug) + "'>" + escapeHtml(name) + "</button>";
  }).join("");
}

function renderCorpusResultCard(item, selectedId) {
  item = item || {};
  selectedId = selectedId || "";
  var recordId = escapeHtml(item.recordId || item.id || "");
  var type = escapeHtml(item.type || "");
  var text = escapeHtml(item.text || item.normalized || "");
  var meaning = escapeHtml(item.meaning || item.notes || "");
  var selected = String(item.recordId || item.id || "") === String(selectedId) ? " is-selected" : "";
  return "<article class='corpus-browser-card" + selected + "' data-record-id='" + recordId + "' data-record-type='" + type + "'><header><span class='" + typeClass(item.type) + "'>" + type + "</span><code>" + recordId + "</code></header><p class='corpus-browser-card-text'>" + text + "</p>" + (meaning ? "<p class='corpus-browser-card-meta'>" + meaning + "</p>" : "") + "</article>";
}

function normalizeResults(summary) {
  summary = summary || {};
  if (Array.isArray(summary.results)) return summary.results;
  if (Array.isArray(summary.records)) {
    return summary.records.map(function (item) {
      return { recordId: item.id || item.recordId, type: item.type || summary.corpusType, text: item.text || item.normalized, meaning: item.notes || "" };
    });
  }
  return [];
}

function renderCorpusResults(summary, section, windowState, selectedId) {
  summary = summary || {};
  section = section || "Search";
  windowState = windowState || null;
  selectedId = selectedId || "";
  var results = normalizeResults(summary);
  if (!results.length) return "<div class='corpus-browser-empty'>No " + escapeHtml(section) + " records loaded.</div>";
  var totalCount = results.length;
  var startIndex = windowState && Number.isFinite(windowState.startIndex) ? windowState.startIndex : 0;
  var endIndex = windowState && Number.isFinite(windowState.endIndex) ? windowState.endIndex : Math.min(totalCount, 25);
  var topPadding = windowState && Number.isFinite(windowState.topPadding) ? windowState.topPadding : 0;
  var bottomPadding = windowState && Number.isFinite(windowState.bottomPadding) ? windowState.bottomPadding : Math.max(0, (totalCount - endIndex) * 48);
  var totalHeight = windowState && Number.isFinite(windowState.totalHeight) ? windowState.totalHeight : totalCount * 48;
  var cardsHtml = results.slice(startIndex, endIndex).map(function (item) { return renderCorpusResultCard(item, selectedId); }).join("");
  return "<div class='corpus-results-viewport' data-total-count='" + escapeHtml(totalCount) + "' style='height:480px;overflow:auto;position:relative;'><div class='corpus-results-spacer' style='position:relative;height:" + escapeHtml(totalHeight) + "px;'><div class='corpus-results-window' style='padding-top:" + escapeHtml(topPadding) + "px;padding-bottom:" + escapeHtml(bottomPadding) + "px;'>" + cardsHtml + "</div></div></div>";
}

function renderDerivationSteps(derivationPath) {
  return derivationPath.map(function (step, idx) {
    step = step || {};
    var operation = escapeHtml(step.operation || "unnamed_op");
    var sutra = step.sutra ? "<div>Sutra: " + escapeHtml(step.sutra) + " (" + escapeHtml(step.sutra_name || "") + ")</div>" : "";
    return "<div class='corpus-browser-trace-step'><div>Step " + (idx + 1) + ": " + operation + "</div>" + sutra + "<div>" + escapeHtml(step.input_state || "-") + " -> " + escapeHtml(step.output_state || "-") + "</div></div>";
  }).join("");
}

function renderCorpusTrace(state, summary, selected, derivationData) {
  state = state || {};
  summary = summary || {};
  selected = selected || null;
  derivationData = derivationData || null;
  var lines = ["Schema: sanskrit-corpus-browser.v1", "Section: " + (state.section || "Search"), "Query: " + (summary.query || "(none)"), "Preview only: true", "Canonical write: blocked"];
  if (!selected) {
    lines.push("", "Awaiting corpus selection...");
    return lines.map(function (line) { return "<div class='corpus-browser-trace-line'>" + escapeHtml(line) + "</div>"; }).join("");
  }
  lines.push("", "Selected:", "- id: " + (selected.recordId || selected.id || ""), "- type: " + (selected.type || ""), "- text: " + (selected.text || selected.normalized || ""));
  var header = lines.map(function (line) { return "<div class='corpus-browser-trace-line'>" + escapeHtml(line) + "</div>"; }).join("");
  var derivationPath = derivationData && derivationData.derivation_path;
  if (!derivationPath || !Array.isArray(derivationPath) || derivationPath.length === 0) {
    return header + "<div class='corpus-browser-trace-line'>derivation_path: absent</div>";
  }
  return header + renderDerivationSteps(derivationPath);
}

function renderCorpusBrowserPanel(state, summary, windowState, selected, derivationData) {
  state = state || {};
  summary = summary || {};
  var html = "<div class='corpus-browser-shell'><div>" + renderCorpusStats(state, summary) + "</div><nav>" + renderCorpusNav(state) + "</nav><section><h4>" + escapeHtml(state.section || "Search") + " results</h4><div>" + renderCorpusResults(summary, state.section, windowState, selected && selected.recordId) + "</div></section><aside><h4>Trace</h4><div>" + renderCorpusTrace(state, summary, selected, derivationData) + "</div></aside></div>";
  var results = Array.isArray(summary.results) ? summary.results : [];
  var body = ["Corpus Browser", "Section: " + (state.section || "Search"), "Record Count: " + (state.recordCount || 0), "Matches: " + (summary.count || results.length), "Results: " + results.length].join("\n");
  return freeze({ title: "Sanskrit Corpus Browser", status: summary.valid === false ? "CORPUS_BLOCKED" : "CORPUS_READY", readOnly: true, html: html, body: body });
}

module.exports = {
  renderCorpusBrowserPanel: renderCorpusBrowserPanel,
  renderCorpusStats: renderCorpusStats,
  renderCorpusNav: renderCorpusNav,
  renderCorpusResults: renderCorpusResults,
  renderCorpusTrace: renderCorpusTrace,
  renderCorpusResultCard: renderCorpusResultCard
};
