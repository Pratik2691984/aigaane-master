"use strict";

const {
createRuntimePublicationFinalStableTag
}=require("./execution-kernel-runtime-publication-final-stable-tag.js");

const CLOSEOUT_SCHEMA =
"sanskrit-runtime-publication-closeout-tag-push.v1";

function freeze(v){
return Object.freeze(v);
}

function createRuntimePublicationCloseoutTagPush(input={}){

const stable=
input.stableTag||
createRuntimePublicationFinalStableTag({});

return freeze({
schemaVersion:CLOSEOUT_SCHEMA,

closeout:freeze({
tag:String(
stable.tag?.name||
"sanskrit-runtime-publication-final-stable"
),
prepared:true,
pushed:false,
published:false
}),

source:freeze({
schemaVersion:stable.schemaVersion
}),

capabilities:freeze({
execute:false,
publish:false,
push:false,
rollback:false,
canonicalWrite:false
}),

diagnostics:freeze({
closeoutReady:true,
dryRunOnly:true,
executionBlocked:true,
publicationBlocked:true,
canonicalWriteBlocked:true
})
});

}

function inspectRuntimePublicationCloseoutTagPush(data={}){

return freeze({
ready:Boolean(
data.diagnostics?.closeoutReady
),
dryRunOnly:true,
executionBlocked:true,
publicationBlocked:true
});

}

module.exports={
CLOSEOUT_SCHEMA,
createRuntimePublicationCloseoutTagPush,
inspectRuntimePublicationCloseoutTagPush
};