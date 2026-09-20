"use strict";

const {
createMorphologyRuntime
}=require(
"./execution-kernel-morphology-runtime.js"
);

const PRAKRIYA_RUNTIME_SCHEMA_VERSION =
"sanskrit-prakriya-runtime.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizePrakriyaStage(
stage,
index
){

return freeze({

index,

id:
String(
stage?.id||
`prakriya-${index}`
),

phase:
String(
stage?.phase||
"PLANNED"
),

authorized:false,

executed:false,

mutated:false,

surfaceProduced:false,

diagnostics:
freeze({

prakriyaBlocked:true,

executionBlocked:true,

mutationBlocked:true,

surfaceBlocked:true

})

});

}

function createPrakriyaRuntime(
input={}
){

const morphology=
input.morphologyRuntime||
createMorphologyRuntime({});

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
PRAKRIYA_RUNTIME_SCHEMA_VERSION,

kind:
"CONTROLLED_PRAKRIYA_RUNTIME",

morphology:
freeze({

schemaVersion:
morphology.schemaVersion,

stageCount:
(
morphology.stages||
[]
).length

}),

stages:
freeze(
stages.map(
normalizePrakriyaStage
)
),

capabilities:
freeze({

execute:false,

mutate:false,

applySandhi:false,

applyMorphology:false,

runSutras:false,

produceSurfaceForms:false,

inspectOnly:true

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

prakriyaRuntime:true,

executionBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getPrakriyaRuntimeDiagnostics(
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

PRAKRIYA_RUNTIME_SCHEMA_VERSION,

normalizePrakriyaStage,

createPrakriyaRuntime,

getPrakriyaRuntimeDiagnostics

};