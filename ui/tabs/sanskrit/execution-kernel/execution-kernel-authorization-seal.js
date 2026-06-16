"use strict";

const {
createExecutionKernelSnapshot
}=require("./execution-kernel-engine.js");

const AUTHORIZATION_SEAL_SCHEMA_VERSION =
"sanskrit-execution-kernel-authorization-seal.v1";

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

function normalizeExecutionAuthorizationSeal(seal){
const obj=seal&&typeof seal==="object";
const str=typeof seal==="string";

return freeze({
id:
str
? seal
:
obj
? String(seal.id||seal.referenceId||"authorization-seal.unresolved")
:
"authorization-seal.unresolved",

kind:
str
? "EXECUTION_AUTHORIZATION_SEAL_REFERENCE"
:
obj
? String(seal.kind||"EXECUTION_AUTHORIZATION_SEAL_REFERENCE")
:
"EXECUTION_AUTHORIZATION_SEAL_REFERENCE",

schemaVersion:
str
? "unknown"
:
obj
? String(seal.schemaVersion||"unknown")
:
"unknown",

status:
str
? "REFERENCED"
:
obj
? String(seal.status||"REFERENCED")
:
"UNRESOLVED",

sealed:
Boolean(obj&&seal.sealed===true),

authorizationAllowed:
Boolean(obj&&seal.authorizationAllowed===true),

executionAllowed:
Boolean(obj&&seal.executionAllowed===true),

diagnostics:
freeze({
normalized:true,
authorizationSealLinked:true,

sourceSealedObserved:
Boolean(obj&&seal.sealed===true),

sourceAuthorizationObserved:
Boolean(obj&&seal.authorizationAllowed===true),

sourceExecutionObserved:
Boolean(obj&&seal.executionAllowed===true),

bridgeSealGranted:false,
bridgeAuthorizationGranted:false,
bridgeExecutionGranted:false
})
});
}

function createExecutionKernelAuthorizationSeal(input={}){
const kernel=input.kernelSnapshot||{};
const stages=Array.isArray(kernel.stages)?kernel.stages:[];

return freeze({
schemaVersion:
AUTHORIZATION_SEAL_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_AUTHORIZATION_SEAL",

kernel:
freeze({
schemaVersion:String(kernel.schemaVersion||"unknown"),
kind:String(kernel.kind||"EXECUTION_KERNEL_SNAPSHOT"),
mode:String(kernel.mode||"INSPECTION"),
stageCount:stages.length
}),

authorizationSeal:
normalizeExecutionAuthorizationSeal(input.authorizationSeal),

permission:
freeze({
id:ref(input.permission,"permission.unresolved"),
linked:true
}),

authority:
freeze({
id:ref(input.authority,"authority.unresolved"),
linked:true
}),

governance:
freeze({
id:ref(input.governance,"governance.unresolved"),
linked:true
}),

runtimeEnvironment:
freeze({
id:ref(input.runtimeEnvironment,"runtime.unresolved"),
linked:true
}),

linkage:
freeze({
kernelLinked:true,

authorizationSealLinked:true,
permissionLinked:true,
authorityLinked:true,
governanceLinked:true,
runtimeLinked:true,

sealInspectionOnly:true,

authorizationBlocked:true,
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
sealOnly:true,

authorizationBlocked:true,
executionBlocked:true,
mutationFree:true,
rollbackBlocked:true,
replayBlocked:true,
surfaceFormBlocked:true,

permissionCompatible:true,
authorityCompatible:true,
governanceCompatible:true,
runtimeCompatible:true,

stageCount:stages.length
})
});
}

function buildExecutionKernelAuthorizationSealSnapshot(input={}){
const kernel=
input.kernelSnapshot||
createExecutionKernelSnapshot({
mode:input.mode||"INSPECTION",
guard:input.guardReference||"guard.unresolved",
runtimeEnvironment:input.runtimeEnvironment||"runtime.unresolved",
prakriyaPlan:input.prakriyaPlan||"prakriya.unresolved",
derivationGraph:input.derivationGraph||"graph.unresolved",
stages:input.stages||[]
});

return createExecutionKernelAuthorizationSeal({
kernelSnapshot:kernel,
authorizationSeal:input.authorizationSeal,
permission:input.permission,
authority:input.authority,
governance:input.governance,
runtimeEnvironment:input.runtimeEnvironment
});
}

function getExecutionKernelAuthorizationSealDiagnostics(bridge={}){
const l=bridge.linkage||{};
const d=bridge.diagnostics||{};

return freeze({
schemaVersion:bridge.schemaVersion,
ready:Boolean(d.ready),

authorizationSealLinked:Boolean(l.authorizationSealLinked),
permissionLinked:Boolean(l.permissionLinked),
authorityLinked:Boolean(l.authorityLinked),
governanceLinked:Boolean(l.governanceLinked),
runtimeLinked:Boolean(l.runtimeLinked),

authorizationBlocked:Boolean(l.authorizationBlocked),
executionBlocked:Boolean(l.executionBlocked),
mutationFree:Boolean(d.mutationFree),
rollbackBlocked:Boolean(l.rollbackBlocked),
replayBlocked:Boolean(l.replayBlocked),
surfaceFormBlocked:Boolean(l.surfaceFormBlocked),

stageCount:Number(d.stageCount||0)
});
}

module.exports={
AUTHORIZATION_SEAL_SCHEMA_VERSION,
normalizeExecutionAuthorizationSeal,
createExecutionKernelAuthorizationSeal,
buildExecutionKernelAuthorizationSealSnapshot,
getExecutionKernelAuthorizationSealDiagnostics
};