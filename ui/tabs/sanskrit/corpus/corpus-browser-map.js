"use strict";

const CORPUS_BROWSER_SCHEMA = "sanskrit-corpus-browser.v1";

const CORPUS_SECTIONS = Object.freeze([
  "Dhatu",
  "Sutra",
  "Stotra",
  "Search",
  "Trace",
  "Preview"
]);

function freeze(v) {
  return Object.freeze(v);
}

module.exports = {
  CORPUS_BROWSER_SCHEMA,
  CORPUS_SECTIONS
};