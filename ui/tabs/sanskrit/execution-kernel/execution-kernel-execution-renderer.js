"use strict";

const {
createExecutionInspector
}=require(
"./execution-kernel-execution-inspector.js"
);

const EXECUTION_RENDERER_SCHEMA_VERSION =
"sanskrit-execution-renderer.v1";

function freeze(v){
return Object.freeze(v);
}

function createExecutionRenderer(
input={}
){

const inspector=
input.inspector||
createExecutionInspector({});

const inspections=
inspector.inspections||[];

return freeze({

schemaVersion:
EXECUTION_RENDERER_SCHEMA_VERSION,

kind:
"CONTROLLED_EXECUTION_RENDERER",

summary:
freeze({

inspectionCount:
inspections.length,

ready:
Boolean(
inspector.diagnostics?.ready
),

deterministic:true,

renderOnly:true

}),

renderState:
freeze({

executionBlocked:true,

rollbackBlocked:true,

mutationBlocked:true,

surfaceBlocked:true,

interactive:false

}),

panels:
freeze(
inspections.map(
(item,index)=>freeze({

id:
item.id||
`panel-${index}`,

visible:true,

editable:false,

executed:false

})
)
)

});

}

function getExecutionRendererDiagnostics(
renderer={}
){

return freeze({

schemaVersion:
renderer.schemaVersion,

ready:
Boolean(
renderer.summary?.ready
),

panelCount:
(
renderer.panels||
[]
).length,

renderOnly:true,

mutationFree:true

});

}

module.exports={

EXECUTION_RENDERER_SCHEMA_VERSION,

createExecutionRenderer,

getExecutionRendererDiagnostics

};