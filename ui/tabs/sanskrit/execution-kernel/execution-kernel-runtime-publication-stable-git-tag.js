"use strict";

const {
createRuntimePublicationFinalCloseout
}=require("./execution-kernel-runtime-publication-final-closeout.js");

const STABLE_TAG_SCHEMA =
"sanskrit-runtime-publication-stable-git-tag.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimePublicationStableGitTag(
input={}
){

const closeout =
input.closeout ||
createRuntimePublicationFinalCloseout({});

return freeze({

schemaVersion:
STABLE_TAG_SCHEMA,

tag:freeze({
name:
"sanskrit-runtime-publication-stable",
ready:true,
created:false,
pushed:false,
sealed:true
}),

source:freeze({
schemaVersion:
closeout.schemaVersion
}),

capabilities:freeze({
execute:false,
publish:false,
push:false,
rollback:false,
mutate:false,
canonicalWrite:false
}),

diagnostics:freeze({
stableTagReady:true,
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
})
});

}

function inspectRuntimePublicationStableGitTag(
tag={}
){

return freeze({
ready:
Boolean(
tag.diagnostics?.stableTagReady
),

executionBlocked:true,

publicationBlocked:true,

canonicalWriteBlocked:true
});

}

module.exports={
STABLE_TAG_SCHEMA,
createRuntimePublicationStableGitTag,
inspectRuntimePublicationStableGitTag
};