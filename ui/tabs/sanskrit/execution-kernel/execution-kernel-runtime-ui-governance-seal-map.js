"use strict";

const UI_GOVERNANCE_SEAL_SCHEMA =
"sanskrit-runtime-ui-governance-seal.v1";

const UI_GOVERNANCE_SEAL_STATES = Object.freeze({
EMPTY:"EMPTY",
UI_GOVERNANCE_SEAL_READY:"UI_GOVERNANCE_SEAL_READY",
BLOCKED:"BLOCKED",
REVIEW_ONLY:"REVIEW_ONLY"
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
:0;
}

function normalizeRuntimeUiGovernanceSealRecord(
input={}
){
return freeze({

uiGovernanceSealId:String(
input.uiGovernanceSealId
|| "runtime-ui-governance-seal"
),

createdAt:String(
input.createdAt
|| "static"
),

sourceAuditSealId:String(
input.sourceAuditSealId
|| "runtime-ui-audit-seal"
),

sourceReplaySealId:String(
input.sourceReplaySealId
|| "runtime-ui-replay-seal"
),

sourceSnapshotSealId:String(
input.sourceSnapshotSealId
|| "runtime-ui-snapshot-seal"
),

uiGovernanceSealStatus:String(
input.uiGovernanceSealStatus
|| "ui-governance-seal-ready"
),

uiGovernanceSealMode:String(
input.uiGovernanceSealMode
|| "inspection-ui-governance-seal"
),

governanceSealAllowed:false,
auditSealAllowed:false,
replaySealAllowed:false,
snapshotSealAllowed:false,
controllerAllowed:false,
executionAllowed:false,
mutationAllowed:false,
publicationAllowed:false,
rollbackAllowed:false,
canonicalWriteAllowed:false,

governanceSealEntryCount:
asCount(input.governanceSealEntryCount),

warningCount:
asCount(input.warningCount),

governanceSealEntries:
freeze(
Array.isArray(
input.governanceSealEntries
)
? input.governanceSealEntries
: []
),

warnings:
freeze(
Array.isArray(input.warnings)
? input.warnings
: []
),

diagnostics:
freeze(
isObject(input.diagnostics)
? input.diagnostics
: {}
),

metadata:
freeze(
isObject(input.metadata)
? input.metadata
: {}
)

});
}

function buildRuntimeUiGovernanceSealRecord(
input={}
){
const normalized=
normalizeRuntimeUiGovernanceSealRecord(
input
);

return freeze({

schemaVersion:
UI_GOVERNANCE_SEAL_SCHEMA,

state:
normalized.governanceSealEntries.length
? UI_GOVERNANCE_SEAL_STATES
.UI_GOVERNANCE_SEAL_READY
: UI_GOVERNANCE_SEAL_STATES.EMPTY,

...normalized

});
}

module.exports={
UI_GOVERNANCE_SEAL_SCHEMA,
UI_GOVERNANCE_SEAL_STATES,
normalizeRuntimeUiGovernanceSealRecord,
buildRuntimeUiGovernanceSealRecord
};