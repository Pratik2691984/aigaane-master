"""
aigaane/samcara.py
Saṃcāra Grammar — classical melodic phrase generation.
"""

# Define the exact allowed movements (pakad) for each rāga.
# 'next' specifies the legal subsequent notes from any given note.
SAMCARA_RULES = {
    "mayamalavagowla": {
        "S":  ["R1", "G3"], "R1": ["G3", "S"], "G3": ["M1", "R1"],
        "M1": ["P", "G3"], "P":  ["D1", "M1"], "D1": ["N3", "P"],
        "N3": ["S", "D1"]
    },
    "todi": {
        # Tōḍī is vakra (crooked): G2 is reached via R1, but R1 is not reached via G2
        "S":  ["R1", "G2"], "R1": ["G2", "S"], "G2": ["M1", "R1"],
        "M1": ["P", "G2"], "P":  ["D1", "M1"], "D1": ["N2", "P"],
        "N2": ["S", "D1", "P"] # N2 -> P is a characteristic vakra jump
    },
    "kalyani": {
        # Kalyāṇi emphasizes M2 (the prati madhyama) heavily
        "S":  ["R2", "G3", "M2"], "R2": ["G3", "S"], "G3": ["M2", "R2"],
        "M2": ["P", "G3", "D2"], "P":  ["D2", "M2"], "D2": ["N3", "P"],
        "N3": ["S", "D2"]
    },
    "bhairavi": {
        # Bhairavī is deeply devotional; oscillates between G2 and M1
        "S":  ["R2", "G2"], "R2": ["G2", "S"], "G2": ["M1", "R2"],
        "M1": ["P", "G2"], "P":  ["D1", "M1"], "D1": ["N2", "P"],
        "N2": ["S", "D1"]
    }
}

# Default starting pakad (phrases) that capture the rāga's identity
PAKAD = {
    "mayamalavagowla": ["S", "R1", "G3", "R1", "S", "G3", "M1", "G3", "R1", "S"],
    "todi":            ["S", "R1", "G2", "R1", "S", "G2", "M1", "G2", "R1", "S"],
    "kalyani":         ["S", "R2", "G3", "M2", "G3", "R2", "S", "M2", "P", "M2", "G3", "R2", "S"],
    "bhairavi":        ["S", "G2", "R2", "S", "G2", "M1", "G2", "R2", "S"]
}


def generate_samcara(aligned: list[dict], raga_name: str) -> list[dict]:
    """
    Replaces linear svara assignment with a grammar-aware melodic phrase.
    Ensures every note is a legal legal transition within the rāga.
    """
    if raga_name not in SAMCARA_RULES:
        # Fallback if unknown raga: use mayamalavagowla rules
        raga_name = "mayamalavagowla"
        
    rules = SAMCARA_RULES[raga_name]
    pakad = PAKAD[raga_name]
    pakad_len = len(pakad)
    
    result = []
    last_svara = None
    
    for i, cell in enumerate(aligned):
        # Cycle through the pakad phrase for this rāga
        svara = pakad[i % pakad_len]
        
        # If we have a previous svara, enforce the transition rule
        if last_svara and last_svara in rules:
            allowed_next = rules[last_svara]
            if svara not in allowed_next:
                # If the pakad jumps to an illegal note, fall back to the first allowed
                svara = allowed_next[0]
                
        result.append({**cell, "svara": svara})
        last_svara = svara
        
    return result
