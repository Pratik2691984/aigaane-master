from pathlib import Path
from typing import Any, Dict, List
import json
import unicodedata

from engines.trace_graph import DerivationStep, DerivationTraceGraph


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "data" / "morphology"


class MorphologyException(Exception):
    code = "morphology_error"

    def __init__(self, message: str, status_code: int = 404):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize(value: str, field_name: str) -> str:
    if value is None or not isinstance(value, str):
        raise MorphologyException(f"{field_name} is required.", status_code=400)
    normalized = unicodedata.normalize("NFC", value.strip())
    if not normalized:
        raise MorphologyException(f"{field_name} must not be empty.", status_code=400)
    return normalized


def _noun_registry() -> Dict[str, Any]:
    return _load_json(DATA_ROOT / "subanta_nominal_stems.json")


def _dhatu_registry() -> Dict[str, Any]:
    return _load_json(DATA_ROOT / "dhatu_registry.json")


def _declension(name: str) -> Dict[str, Any]:
    return _load_json(DATA_ROOT / "declensions" / f"declension_{name}.json")


def _morphology_path(steps: List[DerivationStep]) -> List[Dict[str, str]]:
    return DerivationTraceGraph(steps=steps).to_list()


def morphology_meta() -> Dict[str, Any]:
    noun_data = _noun_registry()
    dhatu_data = _dhatu_registry()
    return {
        "engine": "Node 3 Morphology Engine",
        "phase": "phase1",
        "scope": {
            "subanta": ["masculine_a"],
            "tinganta": ["lat_prathama_ekavacana"],
        },
        "nouns": list(noun_data.get("stems", {}).values()),
        "dhatus": list(dhatu_data.get("dhatus", {}).values()),
    }


def inflect_noun(stem: str, case: str, number: str) -> Dict[str, Any]:
    normalized_stem = _normalize(stem, "stem")
    normalized_case = _normalize(case, "case").lower()
    normalized_number = _normalize(number, "number").lower()

    noun_data = _noun_registry()
    entry = noun_data.get("stems", {}).get(normalized_stem)
    if entry is None:
        raise MorphologyException(f"Unsupported nominal stem: {normalized_stem}")

    declension = _declension(entry["declension"])
    form_template = (
        declension.get("forms", {})
        .get(normalized_case, {})
        .get(normalized_number)
    )
    if form_template is None:
        raise MorphologyException(
            f"Unsupported noun inflection: {normalized_case} {normalized_number} for {normalized_stem}"
        )

    form = form_template.format(stem=normalized_stem)
    return {
        "type": "subanta",
        "input": {
            "stem": normalized_stem,
            "case": normalized_case,
            "number": normalized_number,
        },
        "form": form,
        "metadata": entry,
        "rule": {
            "engine": "table_driven_masculine_a_declension",
            "declension": entry["declension"],
        },
        "derivation_path": _morphology_path(
            [
                DerivationStep(
                    sutra="phase1_registry",
                    sutra_name="Phase 1 nominal registry lookup",
                    operation="registry_lookup",
                    input_state=normalized_stem,
                    output_state=entry["declension"],
                    engine_node="Node 3 Morphology",
                ),
                DerivationStep(
                    sutra="phase1_declension_table",
                    sutra_name="Phase 1 masculine a-stem selection",
                    operation="stem_selection",
                    input_state=entry["declension"],
                    output_state=normalized_stem,
                    engine_node="Node 3 Morphology",
                ),
                DerivationStep(
                    sutra="phase1_declension_table",
                    sutra_name="Phase 1 table-driven nominal ending assignment",
                    operation="table_driven_suffix_assignment",
                    input_state=f"{normalized_stem} + {normalized_case}/{normalized_number}",
                    output_state=form,
                    engine_node="Node 3 Morphology",
                ),
                DerivationStep(
                    sutra="phase1_output",
                    sutra_name="Phase 1 morphology output",
                    operation="phase1_morphology_output",
                    input_state=f"{normalized_stem} + {normalized_case}/{normalized_number}",
                    output_state=form,
                    engine_node="Node 3 Morphology",
                ),
            ]
        ),
    }


def conjugate_verb(dhatu: str, lakara: str, person: str, number: str) -> Dict[str, Any]:
    normalized_dhatu = _normalize(dhatu, "dhatu")
    normalized_lakara = _normalize(lakara, "lakara").lower()
    normalized_person = _normalize(person, "person").lower()
    normalized_number = _normalize(number, "number").lower()

    dhatu_data = _dhatu_registry()
    entry = dhatu_data.get("dhatus", {}).get(normalized_dhatu)
    if entry is None:
        raise MorphologyException(f"Unsupported dhatu: {normalized_dhatu}")

    form = (
        entry.get(normalized_lakara, {})
        .get(normalized_person, {})
        .get(normalized_number)
    )
    if form is None:
        raise MorphologyException(
            f"Unsupported verb conjugation: {normalized_lakara} {normalized_person} {normalized_number} for {normalized_dhatu}"
        )

    return {
        "type": "tinganta",
        "input": {
            "dhatu": normalized_dhatu,
            "lakara": normalized_lakara,
            "person": normalized_person,
            "number": normalized_number,
        },
        "form": form,
        "metadata": entry,
        "rule": {
            "engine": "table_driven_lat_conjugation",
            "lakara": normalized_lakara,
        },
        "derivation_path": _morphology_path(
            [
                DerivationStep(
                    sutra="phase1_registry",
                    sutra_name="Phase 1 dhatu registry lookup",
                    operation="registry_lookup",
                    input_state=normalized_dhatu,
                    output_state=entry["dhatu"],
                    engine_node="Node 3 Morphology",
                ),
                DerivationStep(
                    sutra="phase1_dhatu_table",
                    sutra_name="Phase 1 verbal stem selection",
                    operation="stem_selection",
                    input_state=f"{normalized_dhatu} + {normalized_lakara}",
                    output_state=entry["dhatu"],
                    engine_node="Node 3 Morphology",
                ),
                DerivationStep(
                    sutra="phase1_tin_table",
                    sutra_name="Phase 1 table-driven tin suffix assignment",
                    operation="table_driven_suffix_assignment",
                    input_state=f"{normalized_dhatu} + {normalized_lakara} + {normalized_person}/{normalized_number}",
                    output_state=form,
                    engine_node="Node 3 Morphology",
                ),
                DerivationStep(
                    sutra="phase1_output",
                    sutra_name="Phase 1 morphology output",
                    operation="phase1_morphology_output",
                    input_state=f"{normalized_dhatu} + {normalized_lakara} + {normalized_person}/{normalized_number}",
                    output_state=form,
                    engine_node="Node 3 Morphology",
                ),
            ]
        ),
    }
