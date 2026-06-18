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

function renderRuntimeUiGovernanceSealPanel(
record={}
){

const entries=
Array.isArray(
record.governanceSealEntries
)
? record.governanceSealEntries
:[];

const body=[

"Governance Status: "
+ escapeHtml(
record.uiGovernanceSealStatus
),

"Governance Mode: "
+ escapeHtml(
record.uiGovernanceSealMode
),

"Entry Count: "
+ entries.length,

"Execution Allowed: false",
"Mutation Allowed: false",
"Canonical Write Allowed: false",

"",
"Entries:",

...entries.map(
v=>" - "+escapeHtml(v)
)

].join("\n");

return freeze({

title:
"Runtime UI Governance Seal",

status:
entries.length
? "UI_GOVERNANCE_SEAL_READY"
: "EMPTY",

readOnly:true,

body

});

}

module.exports={
renderRuntimeUiGovernanceSealPanel
};