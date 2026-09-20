"use strict";

const {
createExecutionKernelSnapshot
}=require("./execution-kernel-engine.js");

const RUNTIME_CLOSEOUT_INDEX_SCHEMA_VERSION =
"sanskrit-execution-kernel-runtime-closeout-index.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeCloseoutEntry(
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
`closeout-${index}`
)
:
`closeout-${index}`,

kind:
obj
?
String(
entry.kind||
"CLOSEOUT_ENTRY"
)
:
"CLOSEOUT_ENTRY",

stage:
obj
?
String(
entry.stage||
"UNSPECIFIED"
)
:
"UNSPECIFIED",

closed:
false,

released:
false,

surfaceProduced:
false,

diagnostics:
freeze({

inspectionOnly:true,

closeoutBlocked:true,

releaseBlocked:true,

surfaceBlocked:true

})

});

}

function createExecutionKernelRuntimeCloseoutIndex(
input={}
){

const kernel=
input.kernelSnapshot||{};

const stages=
Array.isArray(
kernel.stages
)
?
kernel.stages
:
[];

const entries=
(
input.entries||
[]
)
.map(
normalizeCloseoutEntry
);

return freeze({

schemaVersion:
RUNTIME_CLOSEOUT_INDEX_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_RUNTIME_CLOSEOUT_INDEX",

kernel:
freeze({

schemaVersion:
String(
kernel.schemaVersion||
"unknown"
),

mode:
String(
kernel.mode||
"INSPECTION"
),

stageCount:
stages.length

}),

entries:
freeze(entries),

summary:
freeze({

entryCount:
entries.length,

closeoutExecuted:false,

releaseExecuted:false,

surfaceFormsProduced:false

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

inspectionOnly:true,

runtimeCloseoutOnly:true,

closeoutBlocked:true,

releaseBlocked:true,

executionBlocked:true,

surfaceBlocked:true,

replaySafe:true,

mutationFree:true

})

});

}

function buildExecutionKernelRuntimeCloseoutIndex(
input={}
){

const kernel=
input.kernelSnapshot||

createExecutionKernelSnapshot({

mode:
input.mode||
"INSPECTION",

guard:
input.guardReference||
"guard.unresolved",

runtimeEnvironment:
input.runtimeEnvironment||
"runtime.unresolved",

prakriyaPlan:
input.prakriyaPlan||
"prakriya.unresolved",

derivationGraph:
input.derivationGraph||
"graph.unresolved",

stages:
input.stages||
[]

});

return createExecutionKernelRuntimeCloseoutIndex({

kernelSnapshot:
kernel,

entries:
input.entries

});

}

function getExecutionKernelRuntimeCloseoutDiagnostics(
index={}
){

const d=
index.diagnostics||{};

const s=
index.summary||{};

return freeze({

schemaVersion:
index.schemaVersion,

ready:
Boolean(
d.ready
),

entryCount:
Number(
s.entryCount||0
),

closeoutBlocked:
Boolean(
d.closeoutBlocked
),

releaseBlocked:
Boolean(
d.releaseBlocked
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

RUNTIME_CLOSEOUT_INDEX_SCHEMA_VERSION,

normalizeCloseoutEntry,

createExecutionKernelRuntimeCloseoutIndex,

buildExecutionKernelRuntimeCloseoutIndex,

getExecutionKernelRuntimeCloseoutDiagnostics

};