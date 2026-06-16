"use strict";

const {
createRuntimePublicationCloseoutTagPush
}=require("./execution-kernel-runtime-publication-closeout-tag-push.js");

const FINAL_TAG_INDEX_SCHEMA =
"sanskrit-runtime-publication-final-tag-index.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeTag(tag,index){

const obj=tag&&typeof tag==="object";

return freeze({
index,
id:obj?String(tag.id||`tag-${index}`):`tag-${index}`,
name:obj?String(
tag.name||
"sanskrit-runtime-publication-final-stable"
):"sanskrit-runtime-publication-final-stable",
sealed:true,
published:false,
immutable:true
});

}

function createRuntimePublicationFinalTagIndex(input={}){

const closeout=
input.closeout||
createRuntimePublicationCloseoutTagPush({});

const tags=
Array.isArray(input.tags)
?input.tags
:[{id:"stable"}];

return freeze({
schemaVersion:FINAL_TAG_INDEX_SCHEMA,

closeout:freeze({
schemaVersion:closeout.schemaVersion
}),

tags:freeze(
tags.map(normalizeTag)
),

capabilities:freeze({
execute:false,
publish:false,
rollback:false,
mutate:false,
canonicalWrite:false
}),

diagnostics:freeze({
indexed:true,
sealed:true,
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
})
});

}

function inspectRuntimePublicationFinalTagIndex(
index={}
){

return freeze({
indexed:Boolean(
index.diagnostics?.indexed
),
tagCount:(index.tags||[]).length,
executionBlocked:true,
canonicalWriteBlocked:true
});

}

module.exports={
FINAL_TAG_INDEX_SCHEMA,
normalizeTag,
createRuntimePublicationFinalTagIndex,
inspectRuntimePublicationFinalTagIndex
};