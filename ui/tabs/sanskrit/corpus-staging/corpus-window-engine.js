"use strict";

const {
  buildCorpusWindowRecord,
  DEFAULT_CORPUS_WINDOW_SIZE
} = require("./corpus-window-map.js");

const {
  summarizeCorpusReservation
} = require("./corpus-reservation-engine.js");

function freeze(v) {
  return Object.freeze(v);
}

function buildCorpusWindows(totalReserved = 0, windowSize = DEFAULT_CORPUS_WINDOW_SIZE) {
  const safeTotal = Math.max(0, Number(totalReserved || 0));
  const safeWindowSize = Math.max(1, Number(windowSize || DEFAULT_CORPUS_WINDOW_SIZE));
  const windows = [];

  for (let start = 0; start < safeTotal; start += safeWindowSize) {
    const end = Math.min(start + safeWindowSize, safeTotal);

    windows.push({
      windowId: "window-" + String(windows.length + 1).padStart(3, "0"),
      windowOrder: windows.length + 1,
      startIndex: start,
      endIndex: end,
      recordCount: end - start,
      previewOnly: true
    });
  }

  return freeze(windows);
}

function planCorpusWindows(input = {}, windowSize = DEFAULT_CORPUS_WINDOW_SIZE) {
  const reservation = summarizeCorpusReservation(input);
  const totalReserved = Number(reservation.totalReserved || 0);
  const windows = buildCorpusWindows(totalReserved, windowSize);

  return buildCorpusWindowRecord({
    windowSize,
    windowCount: windows.length,
    totalReserved,
    windows,
    reservation
  });
}

function summarizeCorpusWindows(input = {}, windowSize = DEFAULT_CORPUS_WINDOW_SIZE) {
  const plan = planCorpusWindows(input, windowSize);

  return freeze({
    state: plan.state,
    valid: plan.state !== "WINDOW_BLOCKED",
    windowSize: plan.windowSize,
    windowCount: plan.windowCount,
    totalReserved: plan.totalReserved,
    previewOnly: true,
    readOnly: true,
    windowExecutionAllowed: false,
    executionAllowed: false,
    canonicalWriteAllowed: false,
    promotionAllowed: false,
    importAllowed: false
  });
}

module.exports = {
  buildCorpusWindows,
  planCorpusWindows,
  summarizeCorpusWindows
};