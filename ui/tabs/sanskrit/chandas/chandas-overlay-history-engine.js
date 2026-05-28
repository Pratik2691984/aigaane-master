import { createEmptyChandasOverlayHistory } from "./chandas-overlay-history-map.js";

function hasObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function normalizeTimelineEntry(snapshot, index) {
  return {
    index,
    sequence: Number.isFinite(snapshot?.sequence) ? snapshot.sequence : index + 1,
    digest: String(snapshot?.digest || ""),
    summaryCount: Number.isFinite(snapshot?.summaryCount) ? snapshot.summaryCount : 0,
    diagnosticCount: Number.isFinite(snapshot?.diagnosticCount) ? snapshot.diagnosticCount : 0,
  };
}

function normalizeDiffEntry(diff, index) {
  return {
    index,
    baselineDigest: String(diff?.baselineDigest || ""),
    candidateDigest: String(diff?.candidateDigest || ""),
    changed: Boolean(diff?.changed),
    changeCount: Number.isFinite(diff?.changeCount) ? diff.changeCount : 0,
  };
}

function buildDiagnostics(history) {
  if (!history.timeline.length) {
    return [
      {
        id: "overlay-history-empty",
        level: "warning",
        message: "Overlay history has no snapshots.",
      },
    ];
  }

  if (!history.diffChain.length) {
    return [
      {
        id: "overlay-history-single-snapshot",
        level: "info",
        message: "Overlay history contains snapshot state without diff traversal.",
      },
    ];
  }

  return [
    {
      id: "overlay-history-ready",
      level: "info",
      message: "Overlay history timeline and diff chain are available.",
    },
  ];
}

export function buildChandasOverlayHistory(snapshots = [], diffs = []) {
  const history = createEmptyChandasOverlayHistory();

  const safeSnapshots = Array.isArray(snapshots) ? snapshots.filter(hasObject) : [];
  const safeDiffs = Array.isArray(diffs) ? diffs.filter(hasObject) : [];

  history.timeline = safeSnapshots.map(normalizeTimelineEntry);
  history.diffChain = safeDiffs.map(normalizeDiffEntry);
  history.summary = {
    snapshotCount: history.timeline.length,
    diffCount: history.diffChain.length,
    changedDiffCount: history.diffChain.filter((diff) => diff.changed).length,
  };
  history.diagnostics = buildDiagnostics(history);

  return Object.freeze(history);
}

export function isChandasOverlayHistoryReady(history) {
  return Boolean(
    hasObject(history) &&
      history.deterministic &&
      history.runtimeIsolated &&
      history.staticPreviewCompatible &&
      history.immutableTimelineSafe &&
      Array.isArray(history.timeline)
  );
}