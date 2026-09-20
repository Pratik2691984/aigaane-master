"use strict";

var DEVANAGARI_RE = /[\u0900-\u097F\u1CD0-\u1CFF\uA8E0-\uA8FF]/;
var IAST_DIACRITIC_RE = /[\u0101\u012B\u016B\u1E5B\u1E5D\u1E37\u1E39\u0113\u014D\u1E43\u1E25\u00F1\u1E45\u1E47\u1E6D\u1E0D\u015B\u1E63\u0100\u012A\u016A\u1E5A\u1E5C\u1E36\u1E38\u0112\u014C\u1E42\u1E24\u00D1\u1E44\u1E46\u1E6C\u1E0C\u015A\u1E62]/;
var LATIN_RE = /[A-Za-z]/;

function freeze(v) {
  return Object.freeze(v);
}

function inspectSanskritInput(raw) {
  var source = raw == null ? "" : String(raw);
  var trimmed = source.trim().replace(/\s+/g, " ");
  var nfc = trimmed.normalize("NFC");
  var errors = [];
  var script = "empty";

  if (!nfc) {
    errors.push("empty");
    return freeze({
      raw: source,
      trimmed: "",
      nfc: "",
      script: "empty",
      ok: false,
      errors: freeze(errors)
    });
  }

  var hasDevanagari = DEVANAGARI_RE.test(nfc);
  var hasLatin = LATIN_RE.test(nfc) || IAST_DIACRITIC_RE.test(nfc);
  var remainder = nfc
    .replace(/[\u0900-\u097F\u1CD0-\u1CFF\uA8E0-\uA8FF]/g, "")
    .replace(/[A-Za-z]/g, "")
    .replace(IAST_DIACRITIC_RE, "")
    .replace(/[\s\u0964\u0965\u0970.,;:!?()\[\]{}\-]/g, "");

  if (hasDevanagari && hasLatin) {
    script = "mixed";
    errors.push("mixed-script");
  } else if (hasDevanagari && remainder.length === 0) {
    script = "devanagari";
  } else if (hasLatin && !hasDevanagari && remainder.length === 0) {
    script = "iast";
  } else {
    script = "unknown";
    errors.push("unknown-script");
  }

  return freeze({
    raw: source,
    trimmed: trimmed,
    nfc: nfc,
    script: script,
    ok: errors.length === 0 && (script === "devanagari" || script === "iast"),
    errors: freeze(errors)
  });
}

function toAnalyzePayload(inspected) {
  var view = inspected && typeof inspected === "object" ? inspected : inspectSanskritInput(inspected);
  return freeze({
    input_text: view.nfc || view.trimmed || ""
  });
}

function toDevanagariOnlyPayload(inspected, fieldName) {
  var view = inspected && typeof inspected === "object" && inspected.script
    ? inspected
    : inspectSanskritInput(inspected);
  var name = fieldName || "input";
  if (view.script === "devanagari" && view.nfc) {
    return freeze({
      ok: true,
      value: view.nfc,
      field: name,
      error: null
    });
  }
  return freeze({
    ok: false,
    value: "",
    field: name,
    error: "Devanagari input required for Sandhi and Morphology execution."
  });
}

module.exports = {
  inspectSanskritInput: inspectSanskritInput,
  toAnalyzePayload: toAnalyzePayload,
  toDevanagariOnlyPayload: toDevanagariOnlyPayload
};
