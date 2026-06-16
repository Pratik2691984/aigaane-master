"use strict";

const {
createSandhiRuntime
}=require(
"./execution-kernel-sandhi-runtime.js"
);

const MORPHOLOGY_RUNTIME_SCHEMA_VERSION =
"sanskrit-morphology-runtime.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeMorphologyStage(
stage,
index
){

return freeze({

index,

id:
String(
stage?.id||
`morphology-${index}`
),

category:
String(
stage?.category||
"MORPHOLOGY_STAGE"
),

authorized:false,

executed:false,

mutated:false,

surfaceProduced:false,

diagnostics:
freeze({

morphologyBlocked:true,

executionBlocked:true,

mutationBlocked:true,

surfaceBlocked:true

})

});

}

function createMorphologyRuntime(
input={}
){

const sandhi=
input.sandhiRuntime||
createSandhiRuntime({});

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
MORPHOLOGY_RUNTIME_SCHEMA_VERSION,

kind:
"CONTROLLED_MORPHOLOGY_RUNTIME",

sandhi:
freeze({

schemaVersion:
sandhi.schemaVersion,

stageCount:
(
sandhi.stages||
[]
).length

}),

stages:
freeze(
stages.map(
normalizeMorphologyStage
)
),

capabilities:
freeze({

execute:false,

mutate:false,

generateSubanta:false,

generateTinanta:false,

produceSurfaceForms:false,

inspectOnly:true

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

morphologyRuntime:true,

executionBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getMorphologyRuntimeDiagnostics(
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

MORPHOLOGY_RUNTIME_SCHEMA_VERSION,

normalizeMorphologyStage,

createMorphologyRuntime,

getMorphologyRuntimeDiagnostics

};