"use strict";

const { CORPUS_BROWSER_SCHEMA, CORPUS_SECTIONS } = require("./corpus-browser-map.js");

const VIRTUAL_CONFIG = {
  rowHeight: 48,
  viewportHeight: 480,
  overscan: 5
};

function freeze(v) {
  return Object.freeze(v);
}

function computeVirtualWindow(totalCount, scrollTop, config = VIRTUAL_CONFIG) {
  const count = Math.max(0, Number(totalCount) || 0);
  const top = Math.max(0, Number(scrollTop) || 0);
  const rowHeight = config.rowHeight || 48;
  const viewportHeight = config.viewportHeight || 480;
  const overscan = config.overscan !== undefined ? config.overscan : 5;

  const visibleCount = Math.ceil(viewportHeight / rowHeight);
  const rawStart = Math.floor(top / rowHeight);
  const startIndex = Math.max(0, rawStart - overscan);
  const endIndex = Math.min(count, rawStart + visibleCount + overscan);

  return freeze({
    startIndex,
    endIndex,
    topPadding: startIndex * rowHeight,
    bottomPadding: Math.max(0, (count - endIndex) * rowHeight),
    totalHeight: count * rowHeight
  });
}

function buildCorpusBrowserState(indexPayload = {}, section = "Search") {
  const recordCount = Number(indexPayload.recordCount || 0);
  return freeze({
    schemaVersion: CORPUS_BROWSER_SCHEMA,
    section: CORPUS_SECTIONS.includes(section) ? section : "Search",
    recordCount,
    sections: CORPUS_SECTIONS,
    previewOnly: true,
    readOnly: true,
    canonicalWriteAllowed: false
  });
}

function summarizeCorpusResults(payload = {}) {
  const results = Array.isArray(payload.results) ? payload.results : [];
  return freeze({
    valid: payload.valid !== false,
    query: String(payload.query || ""),
    count: Number(payload.count || results.length),
    results: freeze(results.map((item) => freeze({
      recordId: String(item.recordId || item.id || ""),
      type: String(item.type || ""),
      text: String(item.text || ""),
      normalized: String(item.normalized || ""),
      meaning: String(item.meaning || item.notes || item.metadata?.meaning || "")
    }))),
    previewOnly: true,
    readOnly: true
  });
}

module.exports = {
  VIRTUAL_CONFIG,
  computeVirtualWindow,
  buildCorpusBrowserState,
  summarizeCorpusResults
};
