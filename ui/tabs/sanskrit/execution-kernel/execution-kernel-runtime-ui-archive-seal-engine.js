"use strict";

const {
buildRuntimeUiArchiveSealRecord,
normalizeRuntimeUiArchiveSealRecord
}=require(
"./execution-kernel-runtime-ui-archive-seal-map.js"
);

function freeze(v){
return Object.freeze(v);
}

function deriveRuntimeUiArchiveSealEntries(
record={}
){

const entries=[

"runtime-ui-archive-surface",

"runtime-ui-import-reference",

"runtime-ui-export-reference",

"runtime-ui-certification-reference",

"runtime-archive-reference",

"archive-inspection-only",

"archive-evidence-immutable",

"archive-metadata-only",

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
"warning-reference-ui-archive"
);
}

return freeze(entries);

}

function createRuntimeUiArchiveSealRecord(
record={}
){

const entries=
deriveRuntimeUiArchiveSealEntries(
record
);

return buildRuntimeUiArchiveSealRecord({

...record,

uiArchiveSealStatus:
"ui-archive-seal-ready",

uiArchiveSealMode:
"inspection-ui-archive-seal",

archiveSealEntryCount:
entries.length,

warningCount:
Array.isArray(record.warnings)
? record.warnings.length
:0,

archiveSealEntries:
entries,

diagnostics:{

readOnly:true,

archiveSealBlocked:true,

importSealBlocked:true,

exportSealBlocked:true,

certificationSealBlocked:true,

archiveExecutionBlocked:true,

executionBlocked:true,

mutationBlocked:true,

publicationBlocked:true,

rollbackBlocked:true,

canonicalWriteBlocked:true

},

metadata:{
archiveMetadataOnly:true
}

});

}

function inspectRuntimeUiArchiveSealRecord(
record={}
){

const normalized=
normalizeRuntimeUiArchiveSealRecord(
record
);

return freeze({

readOnly:true,

entryCount:
normalized.archiveSealEntries.length,

archiveSealBlocked:true,

importSealBlocked:true,

exportSealBlocked:true,

certificationSealBlocked:true,

archiveExecutionBlocked:true,

executionBlocked:true,

mutationBlocked:true,

publicationBlocked:true,

rollbackBlocked:true,

canonicalWriteBlocked:true

});

}

function compareRuntimeUiArchiveSealRecords(
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

deriveRuntimeUiArchiveSealEntries,

createRuntimeUiArchiveSealRecord,

inspectRuntimeUiArchiveSealRecord,

compareRuntimeUiArchiveSealRecords

};