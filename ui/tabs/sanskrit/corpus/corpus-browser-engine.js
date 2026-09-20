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

function nfcCorpusText(value) {
  return String(value || "").normalize("NFC");
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

function matchesCorpusQuery(record, rawQuery) {
  const cleanQuery = nfcCorpusText(rawQuery).trim();
  if (!cleanQuery) {
    return true;
  }
  const targetText = nfcCorpusText(record && record.text);
  const targetNorm = nfcCorpusText(record && record.normalized);
  const targetId = String((record && (record.recordId || record.id)) || "");
  return targetText.indexOf(cleanQuery) !== -1
    || targetNorm.indexOf(cleanQuery) !== -1
    || targetId.indexOf(cleanQuery) !== -1;
}

function sortCorpusResults(results) {
  const list = Array.isArray(results) ? results.slice() : [];
  return list.sort(function (a, b) {
    const idA = String((a && (a.recordId || a.id)) || "");
    const idB = String((b && (b.recordId || b.id)) || "");
    if (idA < idB) return -1;
    if (idA > idB) return 1;
    const typeA = String((a && a.type) || "");
    const typeB = String((b && b.type) || "");
    if (typeA < typeB) return -1;
    if (typeA > typeB) return 1;
    return 0;
  });
}

function summarizeCorpusResults(payload = {}) {
  const query = nfcCorpusText(payload.query || "").trim();
  const incoming = Array.isArray(payload.results) ? payload.results : [];
  const mapped = incoming.map(function (item) {
    return freeze({
      recordId: String(item.recordId || item.id || ""),
      type: String(item.type || ""),
      text: nfcCorpusText(item.text || ""),
      normalized: nfcCorpusText(item.normalized || ""),
      meaning: String(item.meaning || item.notes || (item.metadata && item.metadata.meaning) || "")
    });
  });
  const filtered = mapped.filter(function (item) {
    return matchesCorpusQuery(item, query);
  });
  const sorted = sortCorpusResults(filtered);
  return freeze({
    valid: payload.valid !== false,
    query: query,
    count: Number(sorted.length),
    results: freeze(sorted),
    previewOnly: true,
    readOnly: true
  });
}

module.exports = {
  VIRTUAL_CONFIG,
  computeVirtualWindow,
  buildCorpusBrowserState,
  summarizeCorpusResults,
  nfcCorpusText,
  matchesCorpusQuery,
  sortCorpusResults
};