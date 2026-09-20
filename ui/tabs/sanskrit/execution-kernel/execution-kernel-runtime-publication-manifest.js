"use strict";

const {
createRuntimePublicationStableTag
}=require(
"./execution-kernel-runtime-publication-stable-tag.js"
);

const MANIFEST_SCHEMA =
"sanskrit-runtime-publication-manifest.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimePublicationManifest(
input={}
){

const tag=
input.tag||
createRuntimePublicationStableTag({});

return freeze({

schemaVersion:
MANIFEST_SCHEMA,

kind:
"CONTROLLED_RUNTIME_PUBLICATION_MANIFEST",

manifest:
freeze({

name:
tag.tag?.name,

published:
Boolean(
tag.tag?.published
),

closed:
Boolean(
tag.tag?.closed
),

immutable:true,

deterministic:true

}),

capabilities:
freeze({

execute:false,
rollback:false,
replay:false,
mutate:false,
canonicalWrite:false,
manifestOnly:true

}),

diagnostics:
freeze({

ready:true,
manifestOnly:true,
executionBlocked:true,
rollbackBlocked:true,
replayBlocked:true,
mutationFree:true,
canonicalWriteBlocked:true

})

});

}

function getRuntimePublicationManifestDiagnostics(
manifest={}
){

return freeze({

schemaVersion:
manifest.schemaVersion,

ready:
Boolean(
manifest.diagnostics?.ready
),

manifestOnly:true,

executionBlocked:true,

canonicalWriteBlocked:true

});

}

module.exports={
MANIFEST_SCHEMA,
createRuntimePublicationManifest,
getRuntimePublicationManifestDiagnostics
};