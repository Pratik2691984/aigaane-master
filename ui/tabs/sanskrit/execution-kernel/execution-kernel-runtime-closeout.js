"use strict";

const {
createRuntimeSummary
}=require(
"./execution-kernel-runtime-summary.js"
);

const RUNTIME_CLOSEOUT_SCHEMA_VERSION =
"sanskrit-runtime-closeout.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimeCloseout(
input={}
){

const summary=
input.summary||
createRuntimeSummary({});

return freeze({

schemaVersion:
RUNTIME_CLOSEOUT_SCHEMA_VERSION,

kind:
"CONTROLLED_RUNTIME_CLOSEOUT",

summary:
freeze({

ready:
Boolean(
summary.summary?.ready
),

deterministic:true,

immutable:true,

closed:true

}),

capabilities:
freeze({

execute:false,

rollback:false,

commit:false,

mutate:false,

produceSurfaceForms:false,

inspectOnly:true

}),

diagnostics:
freeze({

ready:true,

closeout:true,

executionBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getRuntimeCloseoutDiagnostics(
closeout={}
){

return freeze({

schemaVersion:
closeout.schemaVersion,

ready:
Boolean(
closeout.diagnostics?.ready
),

closeout:true,

executionBlocked:true,

mutationFree:true

});

}

module.exports={

RUNTIME_CLOSEOUT_SCHEMA_VERSION,

createRuntimeCloseout,

getRuntimeCloseoutDiagnostics

};