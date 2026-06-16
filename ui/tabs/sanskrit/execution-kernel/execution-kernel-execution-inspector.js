"use strict";

const {
createRollbackRuntime
}=require(
"./execution-kernel-rollback-runtime.js"
);

const EXECUTION_INSPECTOR_SCHEMA_VERSION =
"sanskrit-execution-inspector.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeInspection(
item,
index
){

return freeze({

index,

id:
String(
item?.id||
`inspection-${index}`
),

visible:true,

executed:false,

mutated:false,

surfaceProduced:false,

diagnostics:
freeze({

inspectionOnly:true,

executionBlocked:true,

mutationBlocked:true,

surfaceBlocked:true

})

});

}

function createExecutionInspector(
input={}
){

const rollback=
input.rollbackRuntime||
createRollbackRuntime({});

const inspections=
Array.isArray(
input.inspections
)
?
input.inspections
:
[];

return freeze({

schemaVersion:
EXECUTION_INSPECTOR_SCHEMA_VERSION,

kind:
"CONTROLLED_EXECUTION_INSPECTOR",

rollback:
freeze({

schemaVersion:
rollback.schemaVersion,

stageCount:
(
rollback.stages||
[]
).length

}),

inspections:
freeze(
inspections.map(
normalizeInspection
)
),

capabilities:
freeze({

execute:false,

rollback:false,

mutate:false,

produceSurfaceForms:false,

inspectOnly:true

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

inspectionLayer:true,

executionBlocked:true,

mutationFree:true,

replaySafe:true

})

});

}

function getExecutionInspectorDiagnostics(
inspector={}
){

return freeze({

schemaVersion:
inspector.schemaVersion,

ready:
Boolean(
inspector.diagnostics?.ready
),

inspectionCount:
(
inspector.inspections||
[]
).length,

executionBlocked:true,

mutationFree:true,

replaySafe:true

});

}

module.exports={

EXECUTION_INSPECTOR_SCHEMA_VERSION,

normalizeInspection,

createExecutionInspector,

getExecutionInspectorDiagnostics

};