"use strict";

const {
createExecutionKernelSnapshot
}=require("./execution-kernel-engine.js");

const CLOSEOUT_SEAL_SCHEMA_VERSION =
"sanskrit-execution-kernel-closeout-seal.v1";

function freeze(v){
return Object.freeze(v);
}

function ref(v,f){
if(typeof v==="string") return v;

if(v&&typeof v==="object"){
return String(
v.id||
v.referenceId||
f
);
}

return f;
}

function normalizeExecutionCloseoutSeal(
seal
){

const obj=
seal&&
typeof seal==="object";

const str=
typeof seal==="string";

return freeze({

id:
str
? seal
:
obj
?
String(
seal.id||
seal.referenceId||
"closeout-seal.unresolved"
)
:
"closeout-seal.unresolved",

kind:
str
?
"EXECUTION_CLOSEOUT_SEAL_REFERENCE"
:
obj
?
String(
seal.kind||
"EXECUTION_CLOSEOUT_SEAL_REFERENCE"
)
:
"EXECUTION_CLOSEOUT_SEAL_REFERENCE",

schemaVersion:
str
?
"unknown"
:
obj
?
String(
seal.schemaVersion||
"unknown"
)
:
"unknown",

status:
str
?
"REFERENCED"
:
obj
?
String(
seal.status||
"REFERENCED"
)
:
"UNRESOLVED",

closed:
Boolean(
obj&&
seal.closed===true
),

closeoutAllowed:
Boolean(
obj&&
seal.closeoutAllowed===true
),

releaseAllowed:
Boolean(
obj&&
seal.releaseAllowed===true
),

diagnostics:
freeze({

normalized:true,

closeoutSealLinked:true,

sourceClosedObserved:
Boolean(
obj&&
seal.closed===true
),

sourceCloseoutObserved:
Boolean(
obj&&
seal.closeoutAllowed===true
),

sourceReleaseObserved:
Boolean(
obj&&
seal.releaseAllowed===true
),

bridgeCloseoutGranted:false,

bridgeReleaseGranted:false

})

});

}

function createExecutionKernelCloseoutSeal(
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

return freeze({

schemaVersion:
CLOSEOUT_SEAL_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_CLOSEOUT_SEAL",

kernel:
freeze({

schemaVersion:
String(
kernel.schemaVersion||
"unknown"
),

kind:
String(
kernel.kind||
"EXECUTION_KERNEL_SNAPSHOT"
),

mode:
String(
kernel.mode||
"INSPECTION"
),

stageCount:
stages.length

}),

closeoutSeal:
normalizeExecutionCloseoutSeal(
input.closeoutSeal
),

finalizationSeal:
freeze({
id:
ref(
input.finalizationSeal,
"finalization-seal.unresolved"
),
linked:true
}),

authorizationSeal:
freeze({
id:
ref(
input.authorizationSeal,
"authorization-seal.unresolved"
),
linked:true
}),

runtimeEnvironment:
freeze({
id:
ref(
input.runtimeEnvironment,
"runtime.unresolved"
),
linked:true
}),

linkage:
freeze({

kernelLinked:true,

closeoutSealLinked:true,

finalizationSealLinked:true,

authorizationSealLinked:true,

runtimeLinked:true,

closeoutInspectionOnly:true,

closeoutBlocked:true,

releaseBlocked:true,

executionBlocked:true,

mutationBlocked:true,

rollbackBlocked:true,

replayBlocked:true,

surfaceFormBlocked:true

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

inspectionOnly:true,

closeoutOnly:true,

closeoutBlocked:true,

releaseBlocked:true,

executionBlocked:true,

mutationFree:true,

rollbackBlocked:true,

replayBlocked:true,

surfaceFormBlocked:true,

finalizationCompatible:true,

authorizationCompatible:true,

runtimeCompatible:true,

stageCount:
stages.length

})

});

}

function buildExecutionKernelCloseoutSealSnapshot(
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

return createExecutionKernelCloseoutSeal({

kernelSnapshot:
kernel,

closeoutSeal:
input.closeoutSeal,

finalizationSeal:
input.finalizationSeal,

authorizationSeal:
input.authorizationSeal,

runtimeEnvironment:
input.runtimeEnvironment

});

}

function getExecutionKernelCloseoutSealDiagnostics(
bridge={}
){

const l=
bridge.linkage||{};

const d=
bridge.diagnostics||{};

return freeze({

schemaVersion:
bridge.schemaVersion,

ready:
Boolean(
d.ready
),

closeoutSealLinked:
Boolean(
l.closeoutSealLinked
),

finalizationSealLinked:
Boolean(
l.finalizationSealLinked
),

authorizationSealLinked:
Boolean(
l.authorizationSealLinked
),

runtimeLinked:
Boolean(
l.runtimeLinked
),

closeoutBlocked:
Boolean(
l.closeoutBlocked
),

releaseBlocked:
Boolean(
l.releaseBlocked
),

executionBlocked:
Boolean(
l.executionBlocked
),

mutationFree:
Boolean(
d.mutationFree
),

rollbackBlocked:
Boolean(
l.rollbackBlocked
),

replayBlocked:
Boolean(
l.replayBlocked
),

surfaceFormBlocked:
Boolean(
l.surfaceFormBlocked
),

stageCount:
Number(
d.stageCount||0
)

});

}

module.exports={
CLOSEOUT_SEAL_SCHEMA_VERSION,
normalizeExecutionCloseoutSeal,
createExecutionKernelCloseoutSeal,
buildExecutionKernelCloseoutSealSnapshot,
getExecutionKernelCloseoutSealDiagnostics
};