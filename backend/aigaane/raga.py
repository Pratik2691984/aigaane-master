RAGAS = {
    'mayamalavagowla': {
        'arohana':   ['S', 'R1', 'G3', 'M1', 'P', 'D1', 'N3'],
        'avarohana': ['N3', 'D1', 'P', 'M1', 'G3', 'R1', 'S'],
        'ratios': {
            'S':  (1, 1), 'R1': (16, 15), 'G3': (5, 4), 'M1': (4, 3),
            'P':  (3, 2), 'D1': (8, 5), 'N3': (15, 8)
        },
        'default_phrase': ['S', 'R1', 'G3', 'M1', 'P', 'D1', 'N3', 'S']
    }
}

def assign_svaras(aligned: list[dict], raga_name: str) -> list[dict]:
    if raga_name not in RAGAS:
        raise KeyError(f"Unknown raga: {raga_name}")
    phrase = RAGAS[raga_name]['default_phrase']
    phrase_len = len(phrase)
    return [{**cell, 'svara': phrase[i % phrase_len]} for i, cell in enumerate(aligned)]

def svara_ratio(raga_name: str, svara: str) -> float:
    if raga_name not in RAGAS:
        raise KeyError(f"Unknown raga: {raga_name}")
    ratios = RAGAS[raga_name]['ratios']
    if svara not in ratios:
        raise KeyError(f"Unknown svara {svara} for raga {raga_name}")
    num, den = ratios[svara]
    return num / den
