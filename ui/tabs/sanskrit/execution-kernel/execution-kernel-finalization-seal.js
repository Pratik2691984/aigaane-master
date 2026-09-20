"use strict";

const {
createExecutionKernelSnapshot
}=require("./execution-kernel-engine.js");

const FINALIZATION_SEAL_SCHEMA_VERSION =
"sanskrit-execution-kernel-finalization-seal.v1";

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

function normalizeExecutionFinalizationSeal(seal){
const obj=seal&&typeof seal==="object";
const str=typeof seal==="string";

return freeze({
id:
str
? seal
:
obj
? String(seal.id||seal.referenceId||"finalization-seal.unresolved")
:
"finalization-seal.unresolved",

kind:
str
? "EXECUTION_FINALIZATION_SEAL_REFERENCE"
:
obj
? String(seal.kind||"EXECUTION_FINALIZATION_SEAL_REFERENCE")
:
"EXECUTION_FINALIZATION_SEAL_REFERENCE",

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

finalizationAllowed:
Boolean(obj&&seal.finalizationAllowed===true),

surfaceFormsAllowed:
Boolean(obj&&seal.surfaceFormsAllowed===true),

diagnostics:
freeze({
normalized:true,
finalizationSealLinked:true,

sourceSealedObserved:
Boolean(obj&&seal.sealed===true),

sourceFinalizationObserved:
Boolean(obj&&seal.finalizationAllowed===true),

sourceSurfaceFormsObserved:
Boolean(obj&&seal.surfaceFormsAllowed===true),

bridgeSealGranted:false,
bridgeFinalizationGranted:false,
bridgeSurfaceFormsGranted:false
})
});
}

function createExecutionKernelFinalizationSeal(input={}){
const kernel=input.kernelSnapshot||{};
const stages=Array.isArray(kernel.stages)?kernel.stages:[];

return freeze({
schemaVersion:
FINALIZATION_SEAL_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_FINALIZATION_SEAL",

kernel:
freeze({
schemaVersion:String(kernel.schemaVersion||"unknown"),
kind:String(kernel.kind||"EXECUTION_KERNEL_SNAPSHOT"),
mode:String(kernel.mode||"INSPECTION"),
stageCount:stages.length
}),

finalizationSeal:
normalizeExecutionFinalizationSeal(input.finalizationSeal),

authorizationSeal:
freeze({
id:ref(input.authorizationSeal,"authorization-seal.unresolved"),
linked:true
}),

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

runtimeEnvironment:
freeze({
id:ref(input.runtimeEnvironment,"runtime.unresolved"),
linked:true
}),

linkage:
freeze({
kernelLinked:true,

finalizationSealLinked:true,
authorizationSealLinked:true,
permissionLinked:true,
authorityLinked:true,
runtimeLinked:true,

finalizationInspectionOnly:true,

finalizationBlocked:true,
surfaceFormBlocked:true,
authorizationBlocked:true,
executionBlocked:true,
mutationBlocked:true,
rollbackBlocked:true,
replayBlocked:true
}),

diagnostics:
freeze({
ready:true,

deterministic:true,
immutable:true,

inspectionOnly:true,
finalizationSealOnly:true,

finalizationBlocked:true,
surfaceFormBlocked:true,
authorizationBlocked:true,
executionBlocked:true,
mutationFree:true,
rollbackBlocked:true,
replayBlocked:true,

authorizationSealCompatible:true,
permissionCompatible:true,
authorityCompatible:true,
runtimeCompatible:true,

stageCount:stages.length
})
});
}

function buildExecutionKernelFinalizationSealSnapshot(input={}){
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

return createExecutionKernelFinalizationSeal({
kernelSnapshot:kernel,
finalizationSeal:input.finalizationSeal,
authorizationSeal:input.authorizationSeal,
permission:input.permission,
authority:input.authority,
runtimeEnvironment:input.runtimeEnvironment
});
}

function getExecutionKernelFinalizationSealDiagnostics(bridge={}){
const l=bridge.linkage||{};
const d=bridge.diagnostics||{};

return freeze({
schemaVersion:bridge.schemaVersion,
ready:Boolean(d.ready),

finalizationSealLinked:Boolean(l.finalizationSealLinked),
authorizationSealLinked:Boolean(l.authorizationSealLinked),
permissionLinked:Boolean(l.permissionLinked),
authorityLinked:Boolean(l.authorityLinked),
runtimeLinked:Boolean(l.runtimeLinked),

finalizationBlocked:Boolean(l.finalizationBlocked),
surfaceFormBlocked:Boolean(l.surfaceFormBlocked),
authorizationBlocked:Boolean(l.authorizationBlocked),
executionBlocked:Boolean(l.executionBlocked),
mutationFree:Boolean(d.mutationFree),
rollbackBlocked:Boolean(l.rollbackBlocked),
replayBlocked:Boolean(l.replayBlocked),

stageCount:Number(d.stageCount||0)
});
}

module.exports={
FINALIZATION_SEAL_SCHEMA_VERSION,
normalizeExecutionFinalizationSeal,
createExecutionKernelFinalizationSeal,
buildExecutionKernelFinalizationSealSnapshot,
getExecutionKernelFinalizationSealDiagnostics
};