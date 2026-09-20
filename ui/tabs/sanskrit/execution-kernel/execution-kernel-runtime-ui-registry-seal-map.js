"use strict";

const UI_REGISTRY_SEAL_SCHEMA =
  "sanskrit-runtime-ui-registry-seal.v1";

const UI_REGISTRY_SEAL_STATES = Object.freeze({
  EMPTY: "EMPTY",
  UI_REGISTRY_SEAL_READY: "UI_REGISTRY_SEAL_READY",
  BLOCKED: "BLOCKED",
  REVIEW_ONLY: "REVIEW_ONLY"
});

function freeze(v) {
  return Object.freeze(v);
}

function isObject(v) {
  return Boolean(v) &&
    typeof v === "object" &&
    !Array.isArray(v);
}

function asCount(v) {
  const n = Number(v || 0);

  return Number.isFinite(n)
    ? Math.max(0, Math.floor(n))
    : 0;
}

function normalizeRuntimeUiRegistrySealRecord(
  input = {}
) {

  return freeze({

    uiRegistrySealId: String(
      input.uiRegistrySealId ||
      "runtime-ui-registry-seal"
    ),

    createdAt: String(
      input.createdAt || "static"
    ),

    sourceEvidenceSealId: String(
      input.sourceEvidenceSealId ||
      "runtime-ui-evidence-seal"
    ),

    sourceLedgerSealId: String(
      input.sourceLedgerSealId ||
      "runtime-ui-ledger-seal"
    ),

    sourceArchiveSealId: String(
      input.sourceArchiveSealId ||
      "runtime-ui-archive-seal"
    ),

    sourceImportSealId: String(
      input.sourceImportSealId ||
      "runtime-ui-import-seal"
    ),

    uiRegistrySealStatus: String(
      input.uiRegistrySealStatus ||
      "ui-registry-seal-ready"
    ),

    uiRegistrySealMode: String(
      input.uiRegistrySealMode ||
      "inspection-ui-registry-seal"
    ),

    registrySealAllowed: false,
    evidenceSealAllowed: false,
    ledgerSealAllowed: false,
    archiveSealAllowed: false,
    importSealAllowed: false,

    controllerAllowed: false,
    executionAllowed: false,
    mutationAllowed: false,
    publicationAllowed: false,
    rollbackAllowed: false,

    canonicalWriteAllowed: false,

    registrySealEntryCount:
      asCount(
        input.registrySealEntryCount
      ),

    warningCount:
      asCount(
        input.warningCount
      ),

    registrySealEntries:
      freeze(
        Array.isArray(
          input.registrySealEntries
        )
          ? input.registrySealEntries
          : []
      ),

    warnings:
      freeze(
        Array.isArray(
          input.warnings
        )
          ? input.warnings
          : []
      ),

    diagnostics:
      freeze(
        isObject(
          input.diagnostics
        )
          ? input.diagnostics
          : {}
      ),

    metadata:
      freeze(
        isObject(
          input.metadata
        )
          ? input.metadata
          : {}
      )

  });

}

function buildRuntimeUiRegistrySealRecord(
  input = {}
) {

  const normalized =
    normalizeRuntimeUiRegistrySealRecord(
      input
    );

  return freeze({

    schemaVersion:
      UI_REGISTRY_SEAL_SCHEMA,

    state:
      normalized.registrySealEntries.length
        ? UI_REGISTRY_SEAL_STATES
            .UI_REGISTRY_SEAL_READY
        : UI_REGISTRY_SEAL_STATES
            .EMPTY,

    ...normalized

  });

}

module.exports = {
  UI_REGISTRY_SEAL_SCHEMA,
  UI_REGISTRY_SEAL_STATES,
  normalizeRuntimeUiRegistrySealRecord,
  buildRuntimeUiRegistrySealRecord
};