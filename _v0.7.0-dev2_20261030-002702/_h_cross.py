"""
Aigaane v0.2.0 — Category H Cross-Domain Mapping Engine
"""

from typing import Optional, Dict

_CROSS_DOMAIN: Dict[str, dict] = {
    "gaṇita": {
        "mapping": "mathematics",
        "domain": "shastra",
        "canon_name": "Gaṇitasārasaṅgraha",
        "reference_locator": "mathematics 1.1",
    },
    "bījagaṇita": {
        "mapping": "algebra",
        "domain": "shastra",
        "canon_name": "Bījagaṇita",
        "reference_locator": "algebra 1.1",
    },
    "jyotiṣa": {
        "mapping": "astronomy/astrology",
        "domain": "jyotisha",
        "canon_name": "Sūryasiddhānta",
        "reference_locator": "astronomy/astrology 1.1",
    },
    "āyurveda": {
        "mapping": "medicine",
        "domain": "ayurveda",
        "canon_name": "Carakasaṃhitā",
        "reference_locator": "medicine 1.1",
    },
    "rasaśāstra": {
        "mapping": "chemistry/metallurgy",
        "domain": "shastra",
        "canon_name": "Rasaratnasamuccaya",
        "reference_locator": "chemistry/metallurgy 1.1",
    },
    "yantra": {
        "mapping": "mechanics/engineering",
        "domain": "shastra",
        "canon_name": "Samarāṅgaṇasūtradhāra",
        "reference_locator": "mechanics/engineering 1.1",
    },
    "vyākaraṇa": {
        "mapping": "formal grammar",
        "domain": "vyakarana",
        "canon_name": "Aṣṭādhyāyī",
        "reference_locator": "formal grammar 1.1",
    },
    "nyāya": {
        "mapping": "formal logic",
        "domain": "nyaya",
        "canon_name": "Nyāyasūtra",
        "reference_locator": "formal logic 1.1",
    },
    "tarka": {
        "mapping": "argumentation theory",
        "domain": "nyaya",
        "canon_name": "Tarkasaṅgraha",
        "reference_locator": "argumentation theory 1.1",
    },
    "mīmāṃsā": {
        "mapping": "hermeneutics",
        "domain": "shastra",
        "canon_name": "Mīmāṃsāsūtra",
        "reference_locator": "hermeneutics 1.1",
    },
}

def lookup(surface: str) -> Optional[dict]:
    return _CROSS_DOMAIN.get(surface)
