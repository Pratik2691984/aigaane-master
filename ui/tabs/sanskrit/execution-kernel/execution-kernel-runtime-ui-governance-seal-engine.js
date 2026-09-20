"use strict";

const {
buildRuntimeUiGovernanceSealRecord,
normalizeRuntimeUiGovernanceSealRecord
}=require(
"./execution-kernel-runtime-ui-governance-seal-map.js"
);

function freeze(v){
return Object.freeze(v);
}

function deriveRuntimeUiGovernanceSealEntries(
record={}
){

const entries=[

"runtime-ui-governance-surface",
"runtime-ui-audit-reference",
"runtime-ui-replay-reference",
"runtime-ui-snapshot-reference",
"runtime-governance-reference",
"runtime-controller-reference",

"governance-inspection-only",

"execution-denied",
"mutation-denied",
"publication-denied",
"rollback-denied",
"canonical-write-denied"

];

if(
Array.isArray(record.warnings)
&& record.warnings.length
){
entries.push(
"warning-reference-ui-governance"
);
}

return freeze(entries);
}

function createRuntimeUiGovernanceSealRecord(
record={}
){

const entries=
deriveRuntimeUiGovernanceSealEntries(
record
);

return buildRuntimeUiGovernanceSealRecord({

...record,

uiGovernanceSealStatus:
"ui-governance-seal-ready",

uiGovernanceSealMode:
"inspection-ui-governance-seal",

governanceSealEntryCount:
entries.length,

warningCount:
Array.isArray(record.warnings)
? record.warnings.length
:0,

governanceSealEntries:
entries,

diagnostics:{

readOnly:true,

governanceSealBlocked:true,
auditSealBlocked:true,
replaySealBlocked:true,
snapshotSealBlocked:true,

executionBlocked:true,
mutationBlocked:true,
publicationBlocked:true,
rollbackBlocked:true,

canonicalWriteBlocked:true

},

metadata:{
governanceMetadataOnly:true
}

});

}

function inspectRuntimeUiGovernanceSealRecord(
record={}
){

const normalized=
normalizeRuntimeUiGovernanceSealRecord(
record
);

return freeze({

readOnly:true,

entryCount:
normalized.governanceSealEntries.length,

governanceSealBlocked:true,
auditSealBlocked:true,
replaySealBlocked:true,
snapshotSealBlocked:true,

executionBlocked:true,
mutationBlocked:true,
publicationBlocked:true,
rollbackBlocked:true,

canonicalWriteBlocked:true

});

}

function compareRuntimeUiGovernanceSealRecords(
a={},
b={}
){
return freeze({
stable:
JSON.stringify(a)
===
JSON.stringify(b)
});
}

module.exports={
deriveRuntimeUiGovernanceSealEntries,
createRuntimeUiGovernanceSealRecord,
inspectRuntimeUiGovernanceSealRecord,
compareRuntimeUiGovernanceSealRecords
};