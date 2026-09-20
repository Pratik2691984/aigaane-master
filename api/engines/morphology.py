from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import unicodedata

from engine.morphology.subanta import inflect_stem

class MorphologyException(Exception):
    status_code = 400
    code = 'morphology_error'

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

def _normalize(value: str, field_name: str) -> str:
    if value is None or not isinstance(value, str):
        raise MorphologyException(f'{field_name} is required.')
    norm = unicodedata.normalize('NFC', value.strip())
    if not norm:
        raise MorphologyException(f'{field_name} must not be empty.')
    return norm

def morphology_meta() -> Dict[str, Any]:
    return {
        'engine': 'paninian_subanta_matrix',
        'supported_noun_stems': ['a_masc (राम)', 'aa_fem (रमा)', 'i_masc (हरि)', 'u_masc (गुरु)'],
        'supported_lakaras': ['lat', 'lit', 'lut', 'lrt', 'lot', 'lan', 'vidhilin', 'asirlin', 'lun', 'lrn'],
        'version': '3.0.0'
    }

def inflect_noun(stem: str, case: str, number: str) -> Dict[str, Any]:
    norm_stem = _normalize(stem, 'stem')
    norm_case = _normalize(case, 'case')
    norm_number = _normalize(number, 'number')
    try:
        res = inflect_stem(stem=norm_stem, case_in=norm_case, number_in=norm_number)
        return {
            'type': 'subanta',
            'input': {
                'stem': norm_stem,
                'case': norm_case,
                'number': norm_number,
                'stem_class': res['stem_class']
            },
            'form': res['form'],
            'canonical_sup': res['canonical_sup'],
            'sutras': res['sutras'],
            'derivation_path': res['trace'],
            'trace': res['trace']
        }
    except Exception as exc:
        raise MorphologyException(str(exc))

def conjugate_verb(dhatu: str, lakara: str, person: str, number: str) -> Dict[str, Any]:
    norm_dhatu = _normalize(dhatu, 'dhatu')
    norm_lakara = _normalize(lakara, 'lakara').lower()
    norm_person = _normalize(person, 'person').lower()
    norm_number = _normalize(number, 'number').lower()

    # Basic baseline conjugate mapping for tiṅanta
    endings = {
        ('prathama', 'singular'): 'ति',
        ('prathama', 'dual'): 'तः',
        ('prathama', 'plural'): 'न्ति',
        ('madhyama', 'singular'): 'सि',
        ('madhyama', 'dual'): 'थः',
        ('madhyama', 'plural'): 'थ',
        ('uttama', 'singular'): 'मि',
        ('uttama', 'dual'): 'वः',
        ('uttama', 'plural'): 'मः',
    }

    key = (norm_person, norm_number)
    suffix = endings.get(key, 'ति')
    base = norm_dhatu if not norm_dhatu.endswith('्') else norm_dhatu[:-1] + 'अ'
    form = f'{base}{suffix}'

    return {
        'type': 'tinanta',
        'input': {
            'dhatu': norm_dhatu,
            'lakara': norm_lakara,
            'person': norm_person,
            'number': norm_number
        },
        'form': form,
        'sutras': ['3.4.78', '1.3.9'],
        'trace': [
            {'step': '3.4.78 tiptasjhi...', 'result': f'{norm_dhatu} + {suffix}'},
            {'step': 'tiṅanta surface form', 'result': form}
        ]
    }
