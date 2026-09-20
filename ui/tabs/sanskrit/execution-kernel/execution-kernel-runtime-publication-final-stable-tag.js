"use strict";

const {
createRuntimePublicationRegistry
}=require("./execution-kernel-runtime-publication-registry.js");

const FINAL_STABLE_TAG_SCHEMA =
"sanskrit-runtime-publication-final-stable-tag.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimePublicationFinalStableTag(input={}){

const registry=
input.registry||
createRuntimePublicationRegistry({});

const tagName=
String(
input.tag||
"sanskrit-runtime-publication-final-stable"
);

return freeze({
schemaVersion:FINAL_STABLE_TAG_SCHEMA,

tag:freeze({
name:tagName,
published:true,
immutable:true,
sealed:true
}),

registry:freeze({
schemaVersion:registry.schemaVersion,
entryCount:(registry.entries||[]).length
}),

capabilities:freeze({
execute:false,
rollback:false,
mutate:false,
canonicalWrite:false,
publish:false
}),

diagnostics:freeze({
stable:true,
sealed:true,
immutable:true,
executionBlocked:true,
canonicalWriteBlocked:true
})
});

}

function inspectRuntimePublicationFinalStableTag(tag={}){

return freeze({
stable:Boolean(tag.diagnostics?.stable),
sealed:Boolean(tag.diagnostics?.sealed),
immutable:Boolean(tag.diagnostics?.immutable),
executionBlocked:true,
canonicalWriteBlocked:true
});

}

module.exports={
FINAL_STABLE_TAG_SCHEMA,
createRuntimePublicationFinalStableTag,
inspectRuntimePublicationFinalStableTag
};