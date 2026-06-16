"use strict";

const {
  createExecutionKernelSnapshot,
} = require("./execution-kernel-engine.js");

const CERTIFICATION_BRIDGE_SCHEMA_VERSION =
"sanskrit-execution-kernel-certification-bridge.v1";

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

function normalizeExecutionCertificationReference(cert){

const obj=cert&&typeof cert==="object";
const str=typeof cert==="string";

return freeze({

id:
str
? cert
:
obj
? String(
cert.id||
cert.referenceId||
"certification.unresolved"
)
:
"certification.unresolved",

kind:
str
?
"EXECUTION_CERTIFICATION_REFERENCE"
:
obj
?
String(
cert.kind||
"EXECUTION_CERTIFICATION_REFERENCE"
)
:
"EXECUTION_CERTIFICATION_REFERENCE",

schemaVersion:
str
?
"unknown"
:
obj
?
String(
cert.schemaVersion||
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
cert.status||
"REFERENCED"
)
:
"UNRESOLVED",

certified:
Boolean(
obj&&
cert.certified===true
),

issuanceAllowed:
Boolean(
obj&&
cert.issuanceAllowed===true
),

executionAllowed:
Boolean(
obj&&
cert.executionAllowed===true
),

diagnostics:
freeze({

normalized:true,

certificationLinked:true,

sourceCertifiedObserved:
Boolean(
obj&&
cert.certified===true
),

sourceIssuanceObserved:
Boolean(
obj&&
cert.issuanceAllowed===true
),

sourceExecutionObserved:
Boolean(
obj&&
cert.executionAllowed===true
),

bridgeCertificationGranted:false,

bridgeIssuanceGranted:false,

bridgeExecutionGranted:false

})

});

}

function createExecutionKernelCertificationBridge(
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
CERTIFICATION_BRIDGE_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_CERTIFICATION_BRIDGE",

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

certification:
normalizeExecutionCertificationReference(
input.certification
),

integrity:
freeze({
id:
ref(
input.integrity,
"integrity.unresolved"
),
linked:true
}),

assurance:
freeze({
id:
ref(
input.assurance,
"assurance.unresolved"
),
linked:true
}),

compliance:
freeze({
id:
ref(
input.compliance,
"compliance.unresolved"
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

certificationLinked:true,

integrityLinked:true,

assuranceLinked:true,

complianceLinked:true,

runtimeLinked:true,

certificationInspectionOnly:true,

issuanceBlocked:true,

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

certificationOnly:true,

issuanceBlocked:true,

executionBlocked:true,

mutationFree:true,

rollbackBlocked:true,

replayBlocked:true,

surfaceFormBlocked:true,

integrityCompatible:true,

assuranceCompatible:true,

complianceCompatible:true,

runtimeCompatible:true,

stageCount:
stages.length

})

});

}

function buildExecutionKernelCertificationBridgeSnapshot(
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

return createExecutionKernelCertificationBridge({

kernelSnapshot:
kernel,

certification:
input.certification,

integrity:
input.integrity,

assurance:
input.assurance,

compliance:
input.compliance,

runtimeEnvironment:
input.runtimeEnvironment

});

}

function getExecutionKernelCertificationBridgeDiagnostics(
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

certificationLinked:
Boolean(
l.certificationLinked
),

integrityLinked:
Boolean(
l.integrityLinked
),

assuranceLinked:
Boolean(
l.assuranceLinked
),

complianceLinked:
Boolean(
l.complianceLinked
),

runtimeLinked:
Boolean(
l.runtimeLinked
),

issuanceBlocked:
Boolean(
l.issuanceBlocked
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
CERTIFICATION_BRIDGE_SCHEMA_VERSION,
normalizeExecutionCertificationReference,
createExecutionKernelCertificationBridge,
buildExecutionKernelCertificationBridgeSnapshot,
getExecutionKernelCertificationBridgeDiagnostics
};