"use strict";

const {
publishRuntimeTag
}=require(
"./execution-kernel-runtime-tag-publisher.js"
);

const TAG_INDEX_SCHEMA =
"sanskrit-runtime-tag-index.v1";

function freeze(v){
return Object.freeze(v);
}

function normalizeTagIndexEntry(entry,index){

const obj=
entry&&
typeof entry==="object";

return freeze({

index,

id:
obj
?
String(entry.id||`runtime-tag-${index}`)
:
`runtime-tag-${index}`,

name:
obj
?
String(entry.name||"sanskrit-runtime-stable")
:
"sanskrit-runtime-stable",

published:
Boolean(obj ? entry.published !== false : true),

executionEnabled:false,

mutationEnabled:false,

canonicalWriteEnabled:false,

diagnostics:
freeze({
indexEntry:true,
executionBlocked:true,
mutationBlocked:true,
canonicalWriteBlocked:true
})

});

}

function createRuntimeTagIndex(input={}){

const publication=
input.publication||
publishRuntimeTag({});

const entries=
Array.isArray(input.entries)
?
input.entries
:
[];

return freeze({

schemaVersion:
TAG_INDEX_SCHEMA,

kind:
"CONTROLLED_RUNTIME_TAG_INDEX",

publication:
freeze({
schemaVersion:publication.schemaVersion,
published:Boolean(publication.publication?.published),
name:String(publication.publication?.name||"sanskrit-runtime-stable")
}),

entries:
freeze(entries.map(normalizeTagIndexEntry)),

capabilities:
freeze({
execute:false,
rollback:false,
replay:false,
mutate:false,
canonicalWrite:false,
indexOnly:true
}),

diagnostics:
freeze({
ready:true,
indexOnly:true,
executionBlocked:true,
mutationFree:true,
canonicalWriteBlocked:true
})

});

}

function getRuntimeTagIndexDiagnostics(index={}){

return freeze({
schemaVersion:index.schemaVersion,
ready:Boolean(index.diagnostics?.ready),
entryCount:(index.entries||[]).length,
indexOnly:true,
executionBlocked:true,
mutationFree:true,
canonicalWriteBlocked:true
});

}

module.exports={
TAG_INDEX_SCHEMA,
normalizeTagIndexEntry,
createRuntimeTagIndex,
getRuntimeTagIndexDiagnostics
};