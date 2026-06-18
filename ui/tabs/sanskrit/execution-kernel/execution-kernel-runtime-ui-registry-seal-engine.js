"use strict";

const {
  buildRuntimeUiRegistrySealRecord,
  normalizeRuntimeUiRegistrySealRecord
} = require(
  "./execution-kernel-runtime-ui-registry-seal-map.js"
);

function freeze(v) {
  return Object.freeze(v);
}

function deriveRuntimeUiRegistrySealEntries(
  record = {}
) {

  const entries = [

    "runtime-ui-registry-surface",

    "runtime-ui-evidence-reference",
    "runtime-ui-ledger-reference",
    "runtime-ui-archive-reference",
    "runtime-ui-import-reference",

    "runtime-registry-reference",

    "registry-inspection-only",

    "registry-evidence-immutable",

    "registry-metadata-only",

    "execution-denied",

    "mutation-denied",

    "publication-denied",

    "rollback-denied",

    "canonical-write-denied"

  ];

  if (
    Array.isArray(record.warnings) &&
    record.warnings.length
  ) {
    entries.push(
      "warning-reference-ui-registry"
    );
  }

  return freeze(entries);

}

function createRuntimeUiRegistrySealRecord(
  record = {}
) {

  const entries =
    deriveRuntimeUiRegistrySealEntries(
      record
    );

  return buildRuntimeUiRegistrySealRecord({

    ...record,

    uiRegistrySealStatus:
      "ui-registry-seal-ready",

    uiRegistrySealMode:
      "inspection-ui-registry-seal",

    registrySealEntryCount:
      entries.length,

    warningCount:
      Array.isArray(record.warnings)
        ? record.warnings.length
        : 0,

    registrySealEntries:
      entries,

    diagnostics: {

      readOnly: true,

      registrySealBlocked: true,

      evidenceSealBlocked: true,

      ledgerSealBlocked: true,

      archiveSealBlocked: true,

      importSealBlocked: true,

      registryExecutionBlocked: true,

      executionBlocked: true,

      mutationBlocked: true,

      publicationBlocked: true,

      rollbackBlocked: true,

      canonicalWriteBlocked: true

    },

    metadata: {

      registryMetadataOnly: true

    }

  });

}

function inspectRuntimeUiRegistrySealRecord(
  record = {}
) {

  const normalized =
    normalizeRuntimeUiRegistrySealRecord(
      record
    );

  return freeze({

    readOnly: true,

    entryCount:
      normalized.registrySealEntries
        .length,

    registrySealBlocked: true,

    evidenceSealBlocked: true,

    ledgerSealBlocked: true,

    archiveSealBlocked: true,

    importSealBlocked: true,

    registryExecutionBlocked: true,

    executionBlocked: true,

    mutationBlocked: true,

    publicationBlocked: true,

    rollbackBlocked: true,

    canonicalWriteBlocked: true

  });

}

function compareRuntimeUiRegistrySealRecords(
  a = {},
  b = {}
) {

  return freeze({

    stable:
      JSON.stringify(a) ===
      JSON.stringify(b)

  });

}

module.exports = {

  deriveRuntimeUiRegistrySealEntries,

  createRuntimeUiRegistrySealRecord,

  inspectRuntimeUiRegistrySealRecord,

  compareRuntimeUiRegistrySealRecords

};