"use strict";

const { CORPUS_BROWSER_SCHEMA, CORPUS_SECTIONS } = require("./corpus-browser-map.js");

function freeze(v) {
  return Object.freeze(v);
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
      recordId: String(item.recordId || ""),
      type: String(item.type || ""),
      text: String(item.text || ""),
      normalized: String(item.normalized || "")
    }))),
    previewOnly: true,
    readOnly: true
  });
}

module.exports = {
  buildCorpusBrowserState,
  summarizeCorpusResults
};