"use strict";

const {
createRuntimeStableTag
}=require(
"./execution-kernel-runtime-stable-tag.js"
);

const PUBLISH_SCHEMA=
"sanskrit-runtime-tag-publisher.v1";

function freeze(v){
return Object.freeze(v);
}

function publishRuntimeTag(
input={}
){

const tag=
input.tag||
createRuntimeStableTag({});

return freeze({

schemaVersion:
PUBLISH_SCHEMA,

kind:
"CONTROLLED_RUNTIME_TAG_PUBLISHER",

publication:
freeze({

published:true,

immutable:true,

ready:
Boolean(
tag.tag?.ready
),

name:
tag.tag?.name

}),

capabilities:
freeze({

execute:false,

rollback:false,

replay:false,

mutate:false,

publishOnly:true

}),

diagnostics:
freeze({

ready:true,

publicationOnly:true,

executionBlocked:true

})

});

}

function getPublisherDiagnostics(
v={}
){

return freeze({

schemaVersion:
v.schemaVersion,

ready:
Boolean(
v.diagnostics?.ready
),

publicationOnly:true

});

}

module.exports={

PUBLISH_SCHEMA,

publishRuntimeTag,

getPublisherDiagnostics

};