"use strict";

require("./execution-kernel-engine.js");

function freezeCopy(value) {
  return Object.freeze({ ...(value && typeof value === "object" ? value : {}) });
}

function normalizeStageForRender(stage, index) {
  return Object.freeze({
    index,
    id: String(stage.id || `execution-kernel-stage-${index}`),
    type: String(stage.type || ""),
    order: Number.isFinite(Number(stage.order)) ? Number(stage.order) : index,
    referenceId: String(stage.referenceId || ""),
    planned: Boolean(stage.planned),
    authorized: Boolean(stage.authorized),
    executed: Boolean(stage.executed),
    diagnostics: Object.freeze(
      Array.isArray(stage.diagnostics) ? stage.diagnostics.map(String) : []
    )
  });
}

function getStageStatusLabel(stage) {
  if (stage.executed) return "EXECUTED_UNEXPECTED";
  if (stage.authorized) return "AUTHORIZED_UNEXPECTED";
  if (stage.planned) return "PLANNED_ONLY";
  return "UNPLANNED";
}

function normalizeExecutionKernelSnapshotForRender(snapshot) {
  const safeSnapshot = snapshot && typeof snapshot === "object" ? snapshot : {};
  const stages = Array.isArray(safeSnapshot.stages) ? safeSnapshot.stages : [];

  return Object.freeze({
    schemaVersion: safeSnapshot.schemaVersion,
    kind: safeSnapshot.kind,
    mode: String(safeSnapshot.mode || "INSPECTION"),
    references: freezeCopy(safeSnapshot.references),
    stageCount: stages.length,
    stages: Object.freeze(stages.map(normalizeStageForRender)),
    capabilities: freezeCopy(safeSnapshot.capabilities),
    trace: freezeCopy(safeSnapshot.trace),
    renderState: Object.freeze({
      ready: true,
      inspectionOnly: true,
      executionBlocked: true,
      mutationFree: true,
      surfaceFormBlocked: true,
      rollbackAuthorizationOnly: true
    })
  });
}

function buildExecutionKernelInspectionViewModel(snapshot) {
  const normalized = normalizeExecutionKernelSnapshotForRender(snapshot);
  const stages = normalized.stages.map((stage) =>
    Object.freeze({
      index: stage.index,
      id: stage.id,
      type: stage.type,
      order: stage.order,
      referenceId: stage.referenceId,
      planned: stage.planned,
      authorized: stage.authorized,
      executed: stage.executed,
      statusLabel: getStageStatusLabel(stage),
      diagnostics: stage.diagnostics
    })
  );

  const executedStageCount = stages.filter((stage) => stage.executed).length;
  const authorizedStageCount = stages.filter((stage) => stage.authorized).length;

  return Object.freeze({
    title: "Controlled Sanskrit Execution Kernel",
    subtitle: "Inspection-only execution envelope",
    schemaVersion: normalized.schemaVersion,
    mode: normalized.mode,
    status: Object.freeze({
      ready: true,
      inspectionOnly: true,
      executionAuthorized: false,
      executionPerformed: false,
      mutationPerformed: false,
      surfaceFormsProduced: false
    }),
    references: normalized.references,
    capabilities: normalized.capabilities,
    stages: Object.freeze(stages),
    diagnostics: Object.freeze({
      stageCount: stages.length,
      blockedStageCount: stages.filter(
        (stage) => !stage.authorized && !stage.executed
      ).length,
      plannedStageCount: stages.filter((stage) => stage.planned).length,
      executedStageCount,
      authorizedStageCount,
      replaySafe: Boolean(normalized.trace.replaySafe),
      mutationFree: true,
      executionBlocked: true,
      surfaceFormBlocked: true,
      rendererPure: true,
      staticPreviewCompatible: true
    })
  });
}

function renderExecutionKernelInspectionText(snapshot) {
  const viewModel = buildExecutionKernelInspectionViewModel(snapshot);
  const lines = [
    viewModel.title,
    `Schema: ${viewModel.schemaVersion}`,
    `Mode: ${viewModel.mode}`,
    `Stages: ${viewModel.diagnostics.stageCount}`,
    "Execution: BLOCKED",
    "Surface Forms: BLOCKED",
    "Mutation: BLOCKED"
  ];

  viewModel.stages.forEach((stage) => {
    lines.push(
      `[${stage.index}] ${stage.id} :: ${stage.type} :: ${stage.statusLabel}`
    );
  });

  return lines.join("\n");
}

function getExecutionKernelRendererDiagnostics(snapshot) {
  const normalized = normalizeExecutionKernelSnapshotForRender(snapshot);

  return {
    ready: true,
    rendererPure: true,
    inspectionOnly: true,
    executionBlocked: true,
    mutationFree: true,
    surfaceFormBlocked: true,
    stageCount: normalized.stageCount
  };
}

if (typeof module !== "undefined") {
  module.exports = {
    normalizeExecutionKernelSnapshotForRender,
    buildExecutionKernelInspectionViewModel,
    renderExecutionKernelInspectionText,
    getExecutionKernelRendererDiagnostics
  };
}
