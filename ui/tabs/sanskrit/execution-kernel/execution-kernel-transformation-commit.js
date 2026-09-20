"use strict";

const {
createPrakriyaRuntime
}=require(
"./execution-kernel-prakriya-runtime.js"
);

const TRANSFORMATION_COMMIT_SCHEMA_VERSION =
"sanskrit-transformation-commit.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeCommitStage(
stage,
index
){

return freeze({

index,

id:
String(
stage?.id||
`commit-${index}`
),

planned:true,

committed:false,

executed:false,

mutated:false,

surfaceProduced:false,

diagnostics:
freeze({

commitBlocked:true,

executionBlocked:true,

mutationBlocked:true,

surfaceBlocked:true

})

});

}

function createTransformationCommit(
input={}
){

const runtime=
input.runtime||
createPrakriyaRuntime({});

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
TRANSFORMATION_COMMIT_SCHEMA_VERSION,

kind:
"CONTROLLED_TRANSFORMATION_COMMIT",

runtime:
freeze({

schemaVersion:
runtime.schemaVersion,

stageCount:
(
runtime.stages||
[]
).length

}),

stages:
freeze(
stages.map(
normalizeCommitStage
)
),

capabilities:
freeze({

commit:false,

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

commitLayer:true,

executionBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getTransformationCommitDiagnostics(
layer={}
){

return freeze({

schemaVersion:
layer.schemaVersion,

ready:
Boolean(
layer.diagnostics?.ready
),

stageCount:
(
layer.stages||
[]
).length,

executionBlocked:true,

mutationFree:true,

replaySafe:true

});

}

module.exports={

TRANSFORMATION_COMMIT_SCHEMA_VERSION,

normalizeCommitStage,

createTransformationCommit,

getTransformationCommitDiagnostics

};