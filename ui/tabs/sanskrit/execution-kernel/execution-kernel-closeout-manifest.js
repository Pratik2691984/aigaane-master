"use strict";

const {
createExecutionKernelRuntimeCloseoutIndex
}=require(
"./execution-kernel-runtime-closeout-index.js"
);

const CLOSEOUT_MANIFEST_SCHEMA_VERSION =
"sanskrit-execution-kernel-closeout-manifest.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeManifestEntry(
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
`manifest-${index}`
)
:
`manifest-${index}`,

kind:
obj
?
String(
entry.kind||
"CLOSEOUT_MANIFEST_ENTRY"
)
:
"CLOSEOUT_MANIFEST_ENTRY",

included:true,

executed:false,

released:false,

surfaceProduced:false,

diagnostics:
freeze({

inspectionOnly:true,

manifestOnly:true,

executionBlocked:true,

releaseBlocked:true,

surfaceBlocked:true

})

});

}

function createExecutionKernelCloseoutManifest(
input={}
){

const runtimeIndex=
input.runtimeIndex||

createExecutionKernelRuntimeCloseoutIndex(
{}
);

const entries=
(
input.entries||
[]
)
.map(
normalizeManifestEntry
);

return freeze({

schemaVersion:
CLOSEOUT_MANIFEST_SCHEMA_VERSION,

kind:
"EXECUTION_KERNEL_CLOSEOUT_MANIFEST",

runtimeIndex:
freeze({

schemaVersion:
runtimeIndex.schemaVersion,

entryCount:
Number(
runtimeIndex.summary?.entryCount||
0
)

}),

entries:
freeze(entries),

summary:
freeze({

manifestCount:
entries.length,

closeoutComplete:false,

releaseComplete:false,

surfaceFormsProduced:false

}),

diagnostics:
freeze({

ready:true,

deterministic:true,

immutable:true,

inspectionOnly:true,

manifestOnly:true,

executionBlocked:true,

releaseBlocked:true,

surfaceBlocked:true,

replaySafe:true,

mutationFree:true

})

});

}

function buildExecutionKernelCloseoutManifest(
input={}
){

return createExecutionKernelCloseoutManifest({

runtimeIndex:
input.runtimeIndex,

entries:
input.entries

});

}

function getExecutionKernelCloseoutManifestDiagnostics(
manifest={}
){

const d=
manifest.diagnostics||{};

const s=
manifest.summary||{};

return freeze({

schemaVersion:
manifest.schemaVersion,

ready:
Boolean(
d.ready
),

manifestCount:
Number(
s.manifestCount||
0
),

executionBlocked:
Boolean(
d.executionBlocked
),

releaseBlocked:
Boolean(
d.releaseBlocked
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

CLOSEOUT_MANIFEST_SCHEMA_VERSION,

normalizeManifestEntry,

createExecutionKernelCloseoutManifest,

buildExecutionKernelCloseoutManifest,

getExecutionKernelCloseoutManifestDiagnostics

};