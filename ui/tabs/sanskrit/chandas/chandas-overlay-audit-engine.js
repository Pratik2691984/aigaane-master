import { createEmptyChandasOverlayAudit } from "./chandas-overlay-audit-map.js";

function hasObject(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function buildCheckpoint(id, passed, message) {
  return {
    id,
    passed: Boolean(passed),
    message,
  };
}

function buildDiagnostics(audit) {
  if (audit.verified) {
    return [
      {
        id: "overlay-audit-verified",
        level: "info",
        message: "Overlay replay audit verification passed.",
      },
    ];
  }

  return [
    {
      id: "overlay-audit-partial",
      level: "warning",
      message: "Overlay replay audit verification is partial.",
    },
  ];
}

export function auditChandasOverlayReplay(replay) {
  const audit = createEmptyChandasOverlayAudit();

  const replayAvailable = hasObject(replay);
  const cursorAvailable = hasObject(replay?.cursor);
  const digestAvailable = Boolean(replay?.cursor?.digest);
  const traversalBounded = Boolean(
    Number.isFinite(replay?.cursor?.index) &&
      Number.isFinite(replay?.totalSteps) &&
      replay.cursor.index >= 0 &&
      replay.cursor.index < Math.max(replay.totalSteps, 1)
  );

  audit.integrity = {
    replayAvailable,
    cursorAvailable,
    digestAvailable,
    traversalBounded,
  };

  audit.checkpoints = [
    buildCheckpoint(
      "replay-available",
      replayAvailable,
      replayAvailable
        ? "Replay payload is available."
        : "Replay payload is missing."
    ),
    buildCheckpoint(
      "cursor-available",
      cursorAvailable,
      cursorAvailable
        ? "Replay cursor is available."
        : "Replay cursor is missing."
    ),
    buildCheckpoint(
      "digest-available",
      digestAvailable,
      digestAvailable
        ? "Replay cursor digest is available."
        : "Replay cursor digest is missing."
    ),
    buildCheckpoint(
      "traversal-bounded",
      traversalBounded,
      traversalBounded
        ? "Replay cursor is bounded within timeline."
        : "Replay cursor is outside timeline bounds."
    ),
  ];

  audit.checkpointCount = audit.checkpoints.length;
  audit.verified = audit.checkpoints.every((checkpoint) => checkpoint.passed);
  audit.diagnostics = buildDiagnostics(audit);

  return Object.freeze(audit);
}

export function isChandasOverlayAuditReady(audit) {
  return Boolean(
    hasObject(audit) &&
      audit.deterministic &&
      audit.runtimeIsolated &&
      audit.staticPreviewCompatible &&
      audit.immutableAuditSafe &&
      Array.isArray(audit.checkpoints)
  );
}