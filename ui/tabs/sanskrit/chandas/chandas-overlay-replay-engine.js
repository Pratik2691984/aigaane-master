import { createEmptyChandasOverlayReplay } from "./chandas-overlay-replay-map.js";

function hasObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function normalizeIndex(index, totalSteps) {
  if (!Number.isFinite(index)) {
    return 0;
  }

  if (totalSteps <= 0) {
    return 0;
  }

  return Math.min(Math.max(Math.trunc(index), 0), totalSteps - 1);
}

function normalizeTimelineEntry(entry, fallbackIndex) {
  return {
    index: Number.isFinite(entry?.index) ? entry.index : fallbackIndex,
    sequence: Number.isFinite(entry?.sequence) ? entry.sequence : fallbackIndex + 1,
    digest: String(entry?.digest || ""),
    summaryCount: Number.isFinite(entry?.summaryCount) ? entry.summaryCount : 0,
    diagnosticCount: Number.isFinite(entry?.diagnosticCount) ? entry.diagnosticCount : 0,
  };
}

function buildDiagnostics(replay) {
  if (!replay.totalSteps) {
    return [
      {
        id: "overlay-replay-empty",
        level: "warning",
        message: "Overlay replay has no timeline steps.",
      },
    ];
  }

  return [
    {
      id: "overlay-replay-ready",
      level: "info",
      message: "Overlay replay cursor is available.",
    },
  ];
}

export function buildChandasOverlayReplay(history, options = {}) {
  const replay = createEmptyChandasOverlayReplay();

  const timeline = Array.isArray(history?.timeline)
    ? history.timeline.filter(hasObject)
    : [];

  const totalSteps = timeline.length;
  const cursorIndex = normalizeIndex(options.index ?? totalSteps - 1, totalSteps);
  const current = timeline[cursorIndex]
    ? normalizeTimelineEntry(timeline[cursorIndex], cursorIndex)
    : null;

  replay.totalSteps = totalSteps;
  replay.current = current;
  replay.cursor = {
    index: cursorIndex,
    sequence: current?.sequence || 0,
    digest: current?.digest || "",
  };
  replay.hasPrevious = cursorIndex > 0;
  replay.hasNext = totalSteps > 0 && cursorIndex < totalSteps - 1;
  replay.diagnostics = buildDiagnostics(replay);

  return Object.freeze(replay);
}

export function isChandasOverlayReplayReady(replay) {
  return Boolean(
    hasObject(replay) &&
      replay.deterministic &&
      replay.runtimeIsolated &&
      replay.staticPreviewCompatible &&
      replay.immutableReplaySafe &&
      replay.totalSteps >= 0
  );
}