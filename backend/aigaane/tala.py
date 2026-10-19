TALAS = {
    'adi': {
        'aksharas': 8,
        'vibhagas': [4, 2, 2]
    }
}

def align_to_tala(weights: list[str], tala_name: str) -> list[dict]:
    if tala_name not in TALAS:
        raise KeyError(f"Unknown tala: {tala_name}")
    tala = TALAS[tala_name]
    total_aksharas = tala['aksharas']
    vibhaga_sizes = tala['vibhagas']
    aligned = []
    
    for i, weight in enumerate(weights):
        cycle = i // total_aksharas
        akshara_idx = (i % total_aksharas) + 1
        running_sum = 0
        vibhaga_idx = 0
        for v_idx, size in enumerate(vibhaga_sizes):
            running_sum += size
            if akshara_idx <= running_sum:
                vibhaga_idx = v_idx
                break
        aligned.append({
            'cycle': cycle,
            'akshara': akshara_idx,
            'vibhaga': vibhaga_idx,
            'weight': weight
        })
    return aligned
