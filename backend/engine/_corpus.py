import json
from pathlib import Path
from typing import List, Dict, Any, Optional

MANIFEST_PATH = Path("corpus/golden_corpus_manifest.json")

# Fallback in-memory classical corpus if manifest is absent or minimal
CLASSICAL_CANON = [
    {
        "source": "Bhagavad Gītā",
        "canto": "1.1",
        "verse": "dharmakṣetre kurukṣetre samavetā yuyutsavaḥ | māmakāḥ pāṇḍavāścaiva kimakurvata sañjaya ||",
        "meter": "anuṣṭubh",
        "meaning": "O Sanjaya, assembled on the sacred plain of Kurukshetra and desiring to fight, what did my sons and the sons of Pandu do?",
        "keywords": ["dharma", "kurukṣetra", "sañjaya", "yuyutsavaḥ"]
    },
    {
        "source": "Bhagavad Gītā",
        "canto": "2.47",
        "verse": "karmaṇyevādhikāraste mā phaleṣu kadācana | mā karmaphalaheturbhūrmā te saṅgo'stvakarmaṇi ||",
        "meter": "anuṣṭubh",
        "meaning": "Thy right is to work only, but never to its fruits; let not the fruits of action be thy motive, nor let thy attachment be to inaction.",
        "keywords": ["karma", "phala", "adhikāra", "akarmaṇi"]
    },
    {
        "source": "Vālmīki Rāmāyaṇa",
        "canto": "1.1.1",
        "verse": "tapaḥsvādhyāyanirataṃ tapasvī vāgvidāṃ varam | nāradaṃ paripapraccha vālmīkirmunipuṅgavam ||",
        "meter": "anuṣṭubh",
        "meaning": "Sage Valmiki inquired of Narada, the foremost of eloquent speakers, who was constantly absorbed in asceticism and self-study.",
        "keywords": ["vālmīki", "nārada", "tapaḥ", "svādhyāya"]
    },
    {
        "source": "Īśāvāsya Upaniṣad",
        "canto": "1.1",
        "verse": "īśāvāsyamidaṃ sarvaṃ yatkiñca jagatyāṃ jagat | tena tyaktena bhuñjīthā mā gṛdhaḥ kasyasviddhanam ||",
        "meter": "anuṣṭubh",
        "meaning": "All this, whatsoever exists in this transient world, is enveloped by the Lord. By renouncing that, protect; do not covet anyone's wealth.",
        "keywords": ["īśāvāsya", "tyaktena", "bhuñjīthā", "jagatyām"]
    }
]

def load_corpus() -> List[Dict[str, Any]]:
    """Loads corpus items from JSON manifest or defaults to core classical canon."""
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
                elif isinstance(data, dict) and "verses" in data:
                    return data["verses"]
        except Exception:
            pass
    return CLASSICAL_CANON

def search_corpus(query: str, source: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Searches the Sanskrit canon using keyword, substring, or source matching.
    """
    corpus = load_corpus()
    q = query.lower().strip()
    results = []

    for item in corpus:
        if source and source.lower() not in item.get("source", "").lower():
            continue
        v_text = item.get("verse", "").lower()
        meaning = item.get("meaning", "").lower()
        canto = item.get("canto", "").lower()
        kws = [k.lower() for k in item.get("keywords", [])]

        if (not q or q in v_text or q in meaning or q in canto or any(q in kw for kw in kws)):
            results.append(item)
            if len(results) >= limit:
                break

    return results
