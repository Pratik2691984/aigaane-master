"use strict";

const {
createRuleStateMachine
}=require(
"./execution-kernel-rule-state-machine.js"
);

const SANDHI_RUNTIME_SCHEMA_VERSION =
"sanskrit-sandhi-runtime.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeSandhiStage(
stage,
index
){

return freeze({

index,

id:
String(
stage?.id||
`sandhi-${index}`
),

mode:
"INSPECTION",

authorized:false,

executed:false,

mutated:false,

surfaceProduced:false,

diagnostics:
freeze({

sandhiBlocked:true,

executionBlocked:true,

mutationBlocked:true,

surfaceBlocked:true

})

});

}

function createSandhiRuntime(
input={}
){

const machine=
input.machine||
createRuleStateMachine({});

const stages=
Array.isArray(
input.stages
)
?
input.stages
:
[];

return freeze({

schemaVersion:
SANDHI_RUNTIME_SCHEMA_VERSION,

kind:
"CONTROLLED_SANDHI_RUNTIME",

machine:
freeze({

schemaVersion:
machine.schemaVersion,

stateCount:
(
machine.states||
[]
).length

}),

stages:
freeze(
stages.map(
normalizeSandhiStage
)
),

capabilities:
freeze({

execute:false,

mutate:false,

produceSurfaceForms:false,

rollback:true,

inspectOnly:true

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

sandhiRuntime:true,

executionBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getSandhiRuntimeDiagnostics(
runtime={}
){

return freeze({

schemaVersion:
runtime.schemaVersion,

ready:
Boolean(
runtime.diagnostics?.ready
),

stageCount:
(
runtime.stages||
[]
).length,

executionBlocked:true,

mutationFree:true,

replaySafe:true

});

}

module.exports={

SANDHI_RUNTIME_SCHEMA_VERSION,

normalizeSandhiStage,

createSandhiRuntime,

getSandhiRuntimeDiagnostics

};