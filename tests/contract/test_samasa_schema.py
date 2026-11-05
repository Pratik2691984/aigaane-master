"""Group 8A - JSON Schema rejection tests (12 cases)."""

import json
import pathlib

from jsonschema import Draft202012Validator, FormatChecker

from tests.contract._samasa_fixtures import leaf, node


SCHEMA = json.loads(
    (pathlib.Path(__file__).parents[2] / 'schemas' / 'samasa_node_v1.json').read_text(encoding='utf-8')
)
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def reject(data):
    errors = list(VALIDATOR.iter_errors(data))
    assert errors, 'expected rejection'


def accept(data):
    errors = list(VALIDATOR.iter_errors(data))
    assert not errors, [e.message for e in errors]


def test_s1_missing_required_field():
    t = leaf()
    del t['normalized']
    reject(t)


def test_s2_invalid_enum():
    t = leaf()
    t['samasa_type'] = 'not_a_real_type'
    reject(t)


def test_s3_additional_property():
    t = leaf()
    t['foo'] = 'bar'
    reject(t)


def test_s4a_leaf_with_children():
    t = leaf()
    t['children'] = [leaf(path_sig='0.0.0')]
    reject(t)


def test_s4b_internal_with_null_children():
    t = node()
    t['children'] = None
    reject(t)


def test_s4c_internal_with_null_vigraha():
    t = node()
    t['vigraha'] = None
    reject(t)


def test_s5_children_count_too_few():
    t = node()
    t['children'] = [leaf()]
    reject(t)


def test_s6a_confidence_too_high():
    t = leaf()
    t['confidence'] = 1.5
    reject(t)


def test_s6b_confidence_negative():
    t = leaf()
    t['confidence'] = -0.1
    reject(t)


def test_s8_bad_node_id_format():
    t = leaf()
    t['node_id'] = 'not-a-uuid'
    reject(t)


def test_s9_bad_sutra_id():
    t = node()
    t['derivation_rules'] = ['not-a-sutra']
    reject(t)


def test_s11_bad_normalized_charset():
    t = leaf()
    t['normalized'] = 'with spaces and emoji'
    reject(t)


def test_valid_tree_accepts():
    accept(node())
