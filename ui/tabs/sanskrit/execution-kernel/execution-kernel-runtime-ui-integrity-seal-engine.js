"use strict";

const {
buildRuntimeUiIntegritySealRecord,
normalizeRuntimeUiIntegritySealRecord
}=require(
"./execution-kernel-runtime-ui-integrity-seal-map.js"
);

function freeze(v){
return Object.freeze(v);
}

function deriveRuntimeUiIntegritySealEntries(
record={}
){

const entries=[

"runtime-ui-integrity-surface",

"runtime-ui-registry-reference",

"runtime-ui-evidence-reference",

"runtime-ui-ledger-reference",

"runtime-ui-archive-reference",

"runtime-integrity-reference",

"integrity-inspection-only",

"integrity-evidence-immutable",

"integrity-metadata-only",

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
"warning-reference-ui-integrity"
);
}

return freeze(entries);

}

function createRuntimeUiIntegritySealRecord(
record={}
){

const entries=
deriveRuntimeUiIntegritySealEntries(
record
);

return buildRuntimeUiIntegritySealRecord({

...record,

uiIntegritySealStatus:
"ui-integrity-seal-ready",

uiIntegritySealMode:
"inspection-ui-integrity-seal",

integritySealEntryCount:
entries.length,

warningCount:
Array.isArray(record.warnings)
?
record.warnings.length
:
0,

integritySealEntries:
entries,

diagnostics:{

readOnly:true,

integritySealBlocked:true,

registrySealBlocked:true,

evidenceSealBlocked:true,

ledgerSealBlocked:true,

archiveSealBlocked:true,

integrityExecutionBlocked:true,

executionBlocked:true,

mutationBlocked:true,

publicationBlocked:true,

rollbackBlocked:true,

canonicalWriteBlocked:true

},

metadata:{

integrityMetadataOnly:true

}

});

}

function inspectRuntimeUiIntegritySealRecord(
record={}
){

const normalized=
normalizeRuntimeUiIntegritySealRecord(
record
);

return freeze({

readOnly:true,

entryCount:
normalized.integritySealEntries
.length,

integritySealBlocked:true,

registrySealBlocked:true,

evidenceSealBlocked:true,

ledgerSealBlocked:true,

archiveSealBlocked:true,

integrityExecutionBlocked:true,

executionBlocked:true,

mutationBlocked:true,

publicationBlocked:true,

rollbackBlocked:true,

canonicalWriteBlocked:true

});

}

function compareRuntimeUiIntegritySealRecords(
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

deriveRuntimeUiIntegritySealEntries,

createRuntimeUiIntegritySealRecord,

inspectRuntimeUiIntegritySealRecord,

compareRuntimeUiIntegritySealRecords

};