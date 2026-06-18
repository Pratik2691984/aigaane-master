"use strict";

const UI_INTEGRITY_SEAL_SCHEMA =
  "sanskrit-runtime-ui-integrity-seal.v1";

const UI_INTEGRITY_SEAL_STATES =
Object.freeze({
  EMPTY: "EMPTY",
  UI_INTEGRITY_SEAL_READY:
    "UI_INTEGRITY_SEAL_READY",
  BLOCKED: "BLOCKED",
  REVIEW_ONLY: "REVIEW_ONLY"
});

function freeze(v){
  return Object.freeze(v);
}

function isObject(v){
  return Boolean(v)
    && typeof v==="object"
    && !Array.isArray(v);
}

function asCount(v){
  const n=Number(v||0);

  return Number.isFinite(n)
    ? Math.max(0,Math.floor(n))
    : 0;
}

function normalizeRuntimeUiIntegritySealRecord(
  input={}
){

return freeze({

uiIntegritySealId:String(
input.uiIntegritySealId
|| "runtime-ui-integrity-seal"
),

createdAt:String(
input.createdAt
|| "static"
),

sourceRegistrySealId:String(
input.sourceRegistrySealId
|| "runtime-ui-registry-seal"
),

sourceEvidenceSealId:String(
input.sourceEvidenceSealId
|| "runtime-ui-evidence-seal"
),

sourceLedgerSealId:String(
input.sourceLedgerSealId
|| "runtime-ui-ledger-seal"
),

sourceArchiveSealId:String(
input.sourceArchiveSealId
|| "runtime-ui-archive-seal"
),

uiIntegritySealStatus:String(
input.uiIntegritySealStatus
|| "ui-integrity-seal-ready"
),

uiIntegritySealMode:String(
input.uiIntegritySealMode
|| "inspection-ui-integrity-seal"
),

integritySealAllowed:false,
registrySealAllowed:false,
evidenceSealAllowed:false,
ledgerSealAllowed:false,
archiveSealAllowed:false,

controllerAllowed:false,
executionAllowed:false,
mutationAllowed:false,
publicationAllowed:false,
rollbackAllowed:false,

canonicalWriteAllowed:false,

integritySealEntryCount:
asCount(
input.integritySealEntryCount
),

warningCount:
asCount(
input.warningCount
),

integritySealEntries:
freeze(
Array.isArray(
input.integritySealEntries
)
?
input.integritySealEntries
:
[]
),

warnings:
freeze(
Array.isArray(
input.warnings
)
?
input.warnings
:
[]
),

diagnostics:
freeze(
isObject(
input.diagnostics
)
?
input.diagnostics
:
{}
),

metadata:
freeze(
isObject(
input.metadata
)
?
input.metadata
:
{}
)

});

}

function buildRuntimeUiIntegritySealRecord(
input={}
){

const normalized=
normalizeRuntimeUiIntegritySealRecord(
input
);

return freeze({

schemaVersion:
UI_INTEGRITY_SEAL_SCHEMA,

state:
normalized.integritySealEntries.length
?
UI_INTEGRITY_SEAL_STATES
.UI_INTEGRITY_SEAL_READY
:
UI_INTEGRITY_SEAL_STATES.EMPTY,

...normalized

});

}

module.exports={
UI_INTEGRITY_SEAL_SCHEMA,
UI_INTEGRITY_SEAL_STATES,
normalizeRuntimeUiIntegritySealRecord,
buildRuntimeUiIntegritySealRecord
};