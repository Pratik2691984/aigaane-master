"use strict";

const {
createExecutionKernelSnapshot
}=require("./execution-kernel-engine.js");

const PERMISSION_BRIDGE_SCHEMA_VERSION =
"sanskrit-execution-kernel-permission-bridge.v1";

function freeze(v){
return Object.freeze(v);
}

function ref(v,f){
if(typeof v==="string") return v;

if(v&&typeof v==="object"){
return String(v.id||v.referenceId||f);
}

return f;
}

function normalizeExecutionPermissionReference(
permission
){

const obj=
permission&&
typeof permission==="object";

const str=
typeof permission==="string";

return freeze({

id:
str
? permission
:
obj
? String(
permission.id||
permission.referenceId||
"permission.unresolved"
)
:
"permission.unresolved",

kind:
str
?
"EXECUTION_PERMISSION_REFERENCE"
:
obj
?
String(
permission.kind||
"EXECUTION_PERMISSION_REFERENCE"
)
:
"EXECUTION_PERMISSION_REFERENCE",

schemaVersion:
str
?
"unknown"
:
obj
?
String(
permission.schemaVersion||
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
permission.status||
"REFERENCED"
)
:
"UNRESOLVED",

permitted:
Boolean(
obj&&
permission.permitted===true
),

grantAllowed:
Boolean(
obj&&
permission.grantAllowed===true
),

executionAllowed:
Boolean(
obj&&
permission.executionAllowed===true
),

diagnostics:
freeze({

normalized:true,

permissionLinked:true,

sourcePermissionObserved:
Boolean(
obj&&
permission.permitted===true
),

sourceGrantObserved:
Boolean(
obj&&
permission.grantAllowed===true
),

sourceExecutionObserved:
Boolean(
obj&&
permission.executionAllowed===true
),

bridgePermissionGranted:false,

bridgeGrantGranted:false,

bridgeExecutionGranted:false

})

});

}

function createExecutionKernelPermissionBridge(
input={}
){

const kernel=
input.kernelSnapshot||{};

const stages=
Array.isArray(kernel.stages)
? kernel.stages
: [];

return freeze({

schemaVersion:
PERMISSION_BRIDGE_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_PERMISSION_BRIDGE",

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

permission:
normalizeExecutionPermissionReference(
input.permission
),

authority:
freeze({
id:
ref(
input.authority,
"authority.unresolved"
),
linked:true
}),

governance:
freeze({
id:
ref(
input.governance,
"governance.unresolved"
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

permissionLinked:true,

authorityLinked:true,

governanceLinked:true,

runtimeLinked:true,

permissionInspectionOnly:true,

grantBlocked:true,

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

permissionOnly:true,

grantBlocked:true,

executionBlocked:true,

mutationFree:true,

rollbackBlocked:true,

replayBlocked:true,

surfaceFormBlocked:true,

authorityCompatible:true,

governanceCompatible:true,

runtimeCompatible:true,

stageCount:
stages.length

})

});

}

function buildExecutionKernelPermissionBridgeSnapshot(
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

return createExecutionKernelPermissionBridge({

kernelSnapshot:
kernel,

permission:
input.permission,

authority:
input.authority,

governance:
input.governance,

runtimeEnvironment:
input.runtimeEnvironment

});

}

function getExecutionKernelPermissionBridgeDiagnostics(
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
Boolean(d.ready),

permissionLinked:
Boolean(
l.permissionLinked
),

authorityLinked:
Boolean(
l.authorityLinked
),

governanceLinked:
Boolean(
l.governanceLinked
),

runtimeLinked:
Boolean(
l.runtimeLinked
),

grantBlocked:
Boolean(
l.grantBlocked
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
PERMISSION_BRIDGE_SCHEMA_VERSION,
normalizeExecutionPermissionReference,
createExecutionKernelPermissionBridge,
buildExecutionKernelPermissionBridgeSnapshot,
getExecutionKernelPermissionBridgeDiagnostics
};