"use strict";

function freeze(v){
return Object.freeze(v);
}

function escapeHtml(v){

return String(v)
.replace(/&/g,"&amp;")
.replace(/</g,"&lt;")
.replace(/>/g,"&gt;");

}

function renderRuntimeUiArchiveSealPanel(
record={}
){

const entries=
Array.isArray(
record.archiveSealEntries
)
?
record.archiveSealEntries
:
[];

const body=[

"Archive Status: "
+
escapeHtml(
record.uiArchiveSealStatus
),

"Archive Mode: "
+
escapeHtml(
record.uiArchiveSealMode
),

"Source Import Seal ID: "
+
escapeHtml(
record.sourceImportSealId
),

"Entry Count: "
+
entries.length,

"Execution Allowed: false",

"Publication Allowed: false",

"Canonical Write Allowed: false",

"",

"Entries:",

...entries.map(
v=>" - "+escapeHtml(v)
)

].join("\n");

return freeze({

title:
"Runtime UI Archive Seal",

status:
entries.length
?
"UI_ARCHIVE_SEAL_READY"
:
"EMPTY",

readOnly:true,

body

});

}

module.exports={
renderRuntimeUiArchiveSealPanel
};