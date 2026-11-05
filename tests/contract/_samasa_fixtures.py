"""Synthetic SamasaNode builders for P1-A tests."""

from __future__ import annotations

from _samasa_validator import compute_node_id


def leaf(
    surface: str = 'dev',
    normalized: str = 'dev',
    *,
    output_script: str = 'slp1',
    path_sig: str = '0.0',
    analysis_index: int = 0,
    node_id: str | None = None,
) -> dict:
    return {
        'node_id': node_id or compute_node_id(normalized, '_leaf', analysis_index, path_sig),
        'input_surface': surface,
        'normalized': normalized,
        'surface': surface,
        'output_script': output_script,
        'samasa_type': '_leaf',
        'children': None,
        'vigraha': None,
        'internal_sandhi': [],
        'derivation_rules': [],
        'source_provenance': {'lexical_entry': f'lex_{normalized}'},
        'confidence': 1.0,
        'ambiguity_group': None,
        'analysis_index': 0,
    }


def node(
    samasa_type: str = 'tatpurusa',
    children: list | None = None,
    *,
    surface: str = 'devaputra',
    normalized: str = 'devaputra',
    vigraha: str = 'devasya putraH',
    output_script: str = 'slp1',
    path_sig: str = '0',
    analysis_index: int = 0,
    node_id: str | None = None,
) -> dict:
    if children is None:
        children = [
            leaf('deva', 'deva', path_sig=path_sig + '.0'),
            leaf('putra', 'putra', path_sig=path_sig + '.1'),
        ]
    return {
        'node_id': node_id or compute_node_id(normalized, samasa_type, analysis_index, path_sig),
        'input_surface': surface,
        'normalized': normalized,
        'surface': surface,
        'output_script': output_script,
        'samasa_type': samasa_type,
        'children': children,
        'vigraha': vigraha,
        'internal_sandhi': [],
        'derivation_rules': ['2.1.1'],
        'source_provenance': {'authority': 'Astadhyayi', 'citation': '2.1.1'},
        'confidence': 0.9,
        'ambiguity_group': None,
        'analysis_index': 0,
    }
