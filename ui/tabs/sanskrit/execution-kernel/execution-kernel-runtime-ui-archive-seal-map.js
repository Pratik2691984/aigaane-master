"use strict";

const UI_ARCHIVE_SEAL_SCHEMA =
"sanskrit-runtime-ui-archive-seal.v1";

const UI_ARCHIVE_SEAL_STATES =
Object.freeze({
EMPTY:"EMPTY",
UI_ARCHIVE_SEAL_READY:
"UI_ARCHIVE_SEAL_READY",
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

function normalizeRuntimeUiArchiveSealRecord(
input={}
){

return freeze({

uiArchiveSealId:String(
input.uiArchiveSealId
|| "runtime-ui-archive-seal"
),

createdAt:String(
input.createdAt
|| "static"
),

sourceImportSealId:String(
input.sourceImportSealId
|| "runtime-ui-import-seal"
),

sourceExportSealId:String(
input.sourceExportSealId
|| "runtime-ui-export-seal"
),

sourceCertificationSealId:String(
input.sourceCertificationSealId
|| "runtime-ui-certification-seal"
),

uiArchiveSealStatus:String(
input.uiArchiveSealStatus
|| "ui-archive-seal-ready"
),

uiArchiveSealMode:String(
input.uiArchiveSealMode
|| "inspection-ui-archive-seal"
),

archiveSealAllowed:false,
importSealAllowed:false,
exportSealAllowed:false,
certificationSealAllowed:false,

controllerAllowed:false,
executionAllowed:false,
mutationAllowed:false,
publicationAllowed:false,
rollbackAllowed:false,

canonicalWriteAllowed:false,

archiveSealEntryCount:
asCount(
input.archiveSealEntryCount
),

warningCount:
asCount(
input.warningCount
),

archiveSealEntries:
freeze(
Array.isArray(
input.archiveSealEntries
)
? input.archiveSealEntries
:[]
),

warnings:
freeze(
Array.isArray(
input.warnings
)
? input.warnings
:[]
),

diagnostics:
freeze(
isObject(
input.diagnostics
)
? input.diagnostics
:{}
),

metadata:
freeze(
isObject(
input.metadata
)
? input.metadata
:{}
)

});

}

function buildRuntimeUiArchiveSealRecord(
input={}
){

const normalized=
normalizeRuntimeUiArchiveSealRecord(
input
);

return freeze({

schemaVersion:
UI_ARCHIVE_SEAL_SCHEMA,

state:
normalized.archiveSealEntries.length
?
UI_ARCHIVE_SEAL_STATES
.UI_ARCHIVE_SEAL_READY
:
UI_ARCHIVE_SEAL_STATES.EMPTY,

...normalized

});

}

module.exports={
UI_ARCHIVE_SEAL_SCHEMA,
UI_ARCHIVE_SEAL_STATES,
normalizeRuntimeUiArchiveSealRecord,
buildRuntimeUiArchiveSealRecord
};