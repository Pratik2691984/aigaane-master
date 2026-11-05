"""Group 8B - Semantic validator rejection tests (15 cases)."""

import unicodedata

import _samasa_validator as V
from tests.contract._samasa_fixtures import leaf, node


def test_valid_tree_zero_hard_violations():
    vs = V.validate_samasa_tree(node())
    hard = [v for v in vs if not v.code.startswith(('P1_', 'P4_', 'P6_'))]
    assert hard == [], hard


def test_p1_not_nfc():
    t = leaf()
    t['normalized'] = unicodedata.normalize('NFD', 'deva')
    vs = V.validate_samasa_tree(t)
    # NFD of 'deva' is same as NFC for pure ASCII - use a non-ASCII char
    t['normalized'] = unicodedata.normalize('NFD', 'devá')
    vs = V.validate_samasa_tree(t)
    assert any(v.code == 'P1_NormalizedNotNFC' for v in vs)


def test_p3_surface_not_reconstructable():
    t = node(surface='WRONG_SURFACE')
    vs = V.validate_samasa_tree(t)
    assert any(v.code == 'P3_SurfaceNotReconstructable' for v in vs)


def test_p4_sandhi_rule_format_invalid():
    t = node()
    t['internal_sandhi'] = [{'rule_id': '6-1-87', 'before': 'a', 'after': 'b'}]
    vs = V.validate_samasa_tree(t)
    assert any(v.code == 'P4_SandhiRuleFormatInvalid' for v in vs)


def test_p8_index_without_group():
    t = leaf()
    t['analysis_index'] = 3
    vs = V.validate_samasa_tree(t)
    assert any(v.code == 'P8_AnalysisIndexWithoutGroup' for v in vs)


def test_p10_depth_exceeded():
    root = leaf()
    for _ in range(10):
        root = node(children=[root, leaf(path_sig='0.99')], path_sig='0')
    vs = V.validate_samasa_tree(root)
    assert any(v.code == 'P10_MaxDepthExceeded' for v in vs)


def test_p11_node_count_exceeded():
    level = [leaf(path_sig=f'0.{i}') for i in range(8)]
    for _ in range(3):
        level = [node(children=level, path_sig=str(i)) for i in range(8)]
    root = node(children=level, path_sig='0')
    vs = V.validate_samasa_tree(root)
    assert any(v.code == 'P11_MaxNodesExceeded' for v in vs)


def test_p12_duplicate_node_id():
    dup_id = V.compute_node_id('deva', '_leaf', 0, '0.0')
    c1 = leaf('deva', 'deva', path_sig='0.0', node_id=dup_id)
    c2 = leaf('deva', 'deva', path_sig='0.1', node_id=dup_id)
    t = node(children=[c1, c2])
    vs = V.validate_samasa_tree(t)
    assert any(v.code == 'P12_NodeIdDuplicate' for v in vs)


def test_p13_node_id_mismatch():
    t = leaf()
    t['node_id'] = '00000000-0000-5000-8000-000000000000'
    vs = V.validate_samasa_tree(t)
    assert any(v.code == 'P13_NodeIdMismatch' for v in vs)


def test_p14_script_mismatch_in_tree():
    t = node(output_script='slp1')
    t['children'][0]['output_script'] = 'devanagari'
    vs = V.validate_samasa_tree(t)
    assert any(v.code == 'P14_ScriptMismatchAcrossTree' for v in vs)


def test_p15_empty_root_input():
    t = leaf()
    t['input_surface'] = ''
    vs = V.validate_samasa_tree(t)
    assert any(v.code == 'P15_RootInputMissing' for v in vs)


def test_compute_node_id_deterministic():
    a = V.compute_node_id('devaputra', 'tatpurusa', 0, '0')
    b = V.compute_node_id('devaputra', 'tatpurusa', 0, '0')
    assert a == b
    assert len(a) == 36


def test_compute_node_id_varies_with_path():
    a = V.compute_node_id('deva', '_leaf', 0, '0.0')
    b = V.compute_node_id('deva', '_leaf', 0, '0.1')
    assert a != b


def test_compute_node_id_varies_with_analysis():
    a = V.compute_node_id('deva', '_leaf', 0, '0.0')
    b = V.compute_node_id('deva', '_leaf', 1, '0.0')
    assert a != b


def test_violation_str_format():
    v = V.Violation('TEST', 'root.x', 'msg')
    assert '[TEST]' in str(v)
    assert 'root.x' in str(v)
