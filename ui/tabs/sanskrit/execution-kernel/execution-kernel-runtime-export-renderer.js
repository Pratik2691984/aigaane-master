"use strict";

function freeze(v){
return Object.freeze(v);
}

function escapeHtml(
v
){

return String(v)
.replace(
/&/g,
"&amp;"
)
.replace(
/</g,
"&lt;"
)
.replace(
/>/g,
"&gt;"
);

}

function renderRuntimeExportPanel(
record={}
){

const attestations=
Array.isArray(
record.attestations
)
? record.attestations
: [];

const warnings=
Array.isArray(
record.warnings
)
? record.warnings
: [];

return freeze({

title:
"Runtime Export",

status:
attestations.length
? "EXPORT_READY"
: "EMPTY",

readOnly:true,

body:[

escapeHtml(
record.exportStatus
),

escapeHtml(
record.exportMode
),

escapeHtml(
record.certificate
),

...attestations.map(
escapeHtml
),

...warnings.map(
escapeHtml
)

].join(
"\n"
)

});

}

module.exports={
renderRuntimeExportPanel
};