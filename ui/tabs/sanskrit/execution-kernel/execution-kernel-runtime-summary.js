"use strict";

const {
createExecutionRenderer
}=require(
"./execution-kernel-execution-renderer.js"
);

const RUNTIME_SUMMARY_SCHEMA_VERSION =
"sanskrit-runtime-summary.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimeSummary(
input={}
){

const renderer=
input.renderer||
createExecutionRenderer({});

const panels=
renderer.panels||
[];

return freeze({

schemaVersion:
RUNTIME_SUMMARY_SCHEMA_VERSION,

kind:
"CONTROLLED_RUNTIME_SUMMARY",

summary:
freeze({

panelCount:
panels.length,

ready:
Boolean(
renderer.summary?.ready
),

deterministic:true,

immutable:true

}),

capabilities:
freeze({

execute:false,

rollback:false,

mutate:false,

commit:false,

produceSurfaceForms:false,

inspectOnly:true

}),

diagnostics:
freeze({

ready:true,

summaryOnly:true,

executionBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getRuntimeSummaryDiagnostics(
summary={}
){

return freeze({

schemaVersion:
summary.schemaVersion,

ready:
Boolean(
summary.diagnostics?.ready
),

summaryOnly:true,

executionBlocked:true,

mutationFree:true

});

}

module.exports={

RUNTIME_SUMMARY_SCHEMA_VERSION,

createRuntimeSummary,

getRuntimeSummaryDiagnostics

};