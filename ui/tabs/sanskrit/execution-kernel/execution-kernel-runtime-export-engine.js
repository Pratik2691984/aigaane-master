"use strict";

const {
buildRuntimeExportRecord,
normalizeRuntimeExportRecord
}=require(
"./execution-kernel-runtime-export-map.js"
);

function freeze(v){
return Object.freeze(v);
}

function stableArray(v){
return Array.isArray(v)
? v
: [];
}

function deriveRuntimeExportAttestations(
record={}
){

const warnings=
stableArray(
record.warnings
);

const attestations=[

"inspection-export-certified",

"runtime-readonly-certified",

"execution-denied-certified",

"mutation-denied-certified",

"publication-denied-certified",

"rollback-denied-certified",

"canonical-write-denied-certified"

];

if(
warnings.length
){
attestations.push(
"warning-carry-forward-certified"
);
}

return freeze(
attestations
);

}

function createRuntimeExportRecord(
record={}
){

const warnings=
stableArray(
record.warnings
);

return buildRuntimeExportRecord({

certificationId:
record.certificationId,

certificationStatus:
record.certificationStatus,

certificate:
record.certificate,

controlCount:
record.controlCount,

findingCount:
record.findingCount,

warningCount:
warnings.length,

warnings,

attestations:
deriveRuntimeExportAttestations(
record
),

diagnostics:{
readOnly:true,
executionBlocked:true,
mutationBlocked:true,
publicationBlocked:true,
rollbackBlocked:true,
canonicalWriteBlocked:true
}

});

}

function inspectRuntimeExportRecord(
record={}
){

const normalized=
normalizeRuntimeExportRecord(
record
);

return freeze({

ready:true,

readOnly:true,

attestationCount:
normalized.attestations.length,

executionBlocked:true,

mutationBlocked:true,

publicationBlocked:true,

rollbackBlocked:true,

canonicalWriteBlocked:true

});

}

function compareRuntimeExportRecords(
a={},
b={}
){

return freeze({

stable:
JSON.stringify(
normalizeRuntimeExportRecord(a)
)
===
JSON.stringify(
normalizeRuntimeExportRecord(b)
),

readOnly:true

});

}

module.exports={

deriveRuntimeExportAttestations,

createRuntimeExportRecord,

inspectRuntimeExportRecord,

compareRuntimeExportRecords

};