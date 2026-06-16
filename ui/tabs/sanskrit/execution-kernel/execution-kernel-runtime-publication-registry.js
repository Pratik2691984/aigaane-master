"use strict";

const {
createRuntimePublicationManifest
}=require("./execution-kernel-runtime-publication-manifest.js");

const REGISTRY_SCHEMA =
"sanskrit-runtime-publication-registry.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeRegistryEntry(entry,index){

const obj=entry&&typeof entry==="object";

return freeze({
index,
id:obj?String(entry.id||`runtime-publication-${index}`):`runtime-publication-${index}`,
name:obj?String(entry.name||"sanskrit-runtime-stable"):"sanskrit-runtime-stable",
registered:true,
published:Boolean(obj?entry.published!==false:true),
executionEnabled:false,
mutationEnabled:false,
canonicalWriteEnabled:false,
diagnostics:freeze({
registryEntry:true,
executionBlocked:true,
mutationBlocked:true,
canonicalWriteBlocked:true
})
});

}

function createRuntimePublicationRegistry(input={}){

const manifest=input.manifest||createRuntimePublicationManifest({});
const entries=Array.isArray(input.entries)?input.entries:[];

return freeze({
schemaVersion:REGISTRY_SCHEMA,
kind:"CONTROLLED_RUNTIME_PUBLICATION_REGISTRY",

manifest:freeze({
schemaVersion:manifest.schemaVersion,
name:String(manifest.manifest?.name||"sanskrit-runtime-stable"),
published:Boolean(manifest.manifest?.published),
closed:Boolean(manifest.manifest?.closed)
}),

entries:freeze(entries.map(normalizeRegistryEntry)),

capabilities:freeze({
execute:false,
rollback:false,
replay:false,
mutate:false,
canonicalWrite:false,
registryOnly:true
}),

diagnostics:freeze({
ready:true,
registryOnly:true,
executionBlocked:true,
rollbackBlocked:true,
replayBlocked:true,
mutationFree:true,
canonicalWriteBlocked:true
})
});
}

function getRuntimePublicationRegistryDiagnostics(registry={}){

return freeze({
schemaVersion:registry.schemaVersion,
ready:Boolean(registry.diagnostics?.ready),
entryCount:(registry.entries||[]).length,
registryOnly:true,
executionBlocked:true,
canonicalWriteBlocked:true
});

}

module.exports={
REGISTRY_SCHEMA,
normalizeRegistryEntry,
createRuntimePublicationRegistry,
getRuntimePublicationRegistryDiagnostics
};