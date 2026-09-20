"use strict";

const {
createTransformationCommit
}=require(
"./execution-kernel-transformation-commit.js"
);

const ROLLBACK_RUNTIME_SCHEMA_VERSION =
"sanskrit-rollback-runtime.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeRollbackStage(
stage,
index
){

return freeze({

index,

id:
String(
stage?.id||
`rollback-${index}`
),

planned:true,

rollbackAuthorized:false,

rollbackExecuted:false,

mutated:false,

surfaceProduced:false,

diagnostics:
freeze({

rollbackBlocked:true,

executionBlocked:true,

mutationBlocked:true,

surfaceBlocked:true

})

});

}

function createRollbackRuntime(
input={}
){

const commit=
input.commitLayer||
createTransformationCommit({});

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
ROLLBACK_RUNTIME_SCHEMA_VERSION,

kind:
"CONTROLLED_ROLLBACK_RUNTIME",

commit:
freeze({

schemaVersion:
commit.schemaVersion,

stageCount:
(
commit.stages||
[]
).length

}),

stages:
freeze(
stages.map(
normalizeRollbackStage
)
),

capabilities:
freeze({

rollback:false,

execute:false,

mutate:false,

restore:false,

produceSurfaceForms:false,

inspectOnly:true

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

rollbackRuntime:true,

executionBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getRollbackRuntimeDiagnostics(
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

ROLLBACK_RUNTIME_SCHEMA_VERSION,

normalizeRollbackStage,

createRollbackRuntime,

getRollbackRuntimeDiagnostics

};