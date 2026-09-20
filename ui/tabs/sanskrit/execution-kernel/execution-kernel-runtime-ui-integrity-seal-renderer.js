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

function renderRuntimeUiIntegritySealPanel(
record={}
){

const entries=
Array.isArray(
record.integritySealEntries
)
?
record.integritySealEntries
:
[];

const body=[

"Integrity Status: "
+
escapeHtml(
record.uiIntegritySealStatus
),

"Integrity Mode: "
+
escapeHtml(
record.uiIntegritySealMode
),

"Source Registry Seal ID: "
+
escapeHtml(
record.sourceRegistrySealId
),

"Source Evidence Seal ID: "
+
escapeHtml(
record.sourceEvidenceSealId
),

"",

"Entry Count: "
+
entries.length,

"",

"Execution Allowed: false",

"Mutation Allowed: false",

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
"Runtime UI Integrity Seal",

status:
entries.length
?
"UI_INTEGRITY_SEAL_READY"
:
"EMPTY",

readOnly:true,

body

});

}

module.exports={
renderRuntimeUiIntegritySealPanel
};