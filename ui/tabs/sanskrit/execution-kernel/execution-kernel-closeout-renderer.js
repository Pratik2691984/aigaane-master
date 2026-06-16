"use strict";

const {
createExecutionKernelCloseoutSummary
}=require(
"./execution-kernel-closeout-summary.js"
);

const CLOSEOUT_RENDERER_SCHEMA_VERSION =
"sanskrit-execution-kernel-closeout-renderer.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeRenderEntry(
entry,
index
){

const obj=
entry&&
typeof entry==="object";

return freeze({

index,

id:
obj
?
String(
entry.id||
`render-${index}`
)
:
`render-${index}`,

kind:
obj
?
String(
entry.kind||
"CLOSEOUT_RENDER_ENTRY"
)
:
"CLOSEOUT_RENDER_ENTRY",

visible:true,

executed:false,

surfaceProduced:false,

diagnostics:
freeze({

inspectionOnly:true,

rendererOnly:true,

executionBlocked:true,

surfaceBlocked:true

})

});

}

function createExecutionKernelCloseoutRenderer(
input={}
){

const summary=
input.summary||

createExecutionKernelCloseoutSummary(
{}
);

const entries=
(
input.entries||
[]
)
.map(
normalizeRenderEntry
);

return freeze({

schemaVersion:
CLOSEOUT_RENDERER_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_CLOSEOUT_RENDERER",

summary:
freeze({

schemaVersion:
summary.schemaVersion,

summaryCount:
Number(
summary.summary?.summaryCount||
0
)

}),

entries:
freeze(entries),

render:
freeze({

renderCount:
entries.length,

renderExecuted:false,

surfaceFormsProduced:false

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

inspectionOnly:true,

rendererOnly:true,

executionBlocked:true,

surfaceBlocked:true,

replaySafe:true,

mutationFree:true

})

});

}

function buildExecutionKernelCloseoutRenderer(
input={}
){

return createExecutionKernelCloseoutRenderer({

summary:
input.summary,

entries:
input.entries

});

}

function getExecutionKernelCloseoutRendererDiagnostics(
renderer={}
){

const d=
renderer.diagnostics||{};

const r=
renderer.render||{};

return freeze({

schemaVersion:
renderer.schemaVersion,

ready:
Boolean(
d.ready
),

renderCount:
Number(
r.renderCount||
0
),

executionBlocked:
Boolean(
d.executionBlocked
),

surfaceBlocked:
Boolean(
d.surfaceBlocked
),

replaySafe:
Boolean(
d.replaySafe
),

mutationFree:
Boolean(
d.mutationFree
)

});

}

module.exports={

CLOSEOUT_RENDERER_SCHEMA_VERSION,

normalizeRenderEntry,

createExecutionKernelCloseoutRenderer,

buildExecutionKernelCloseoutRenderer,

getExecutionKernelCloseoutRendererDiagnostics

};