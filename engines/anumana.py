from typing import Dict, List, Tuple


ACTION_DOSHA_RESONANCE: Dict[Tuple[str, str], float] = {
    ("mental", "vata"): 1.0,
    ("mental", "pitta"): 0.55,
    ("mental", "kapha"): 0.45,
    ("physical", "pitta"): 1.0,
    ("physical", "kapha"): 0.55,
    ("physical", "vata"): 0.30,
    ("rest", "kapha"): 1.0,
    ("rest", "vata"): 0.70,
    ("rest", "pitta"): 0.40,
    ("eat", "kapha"): 0.85,
    ("eat", "pitta"): 0.70,
    ("eat", "vata"): 0.35,
}

DOSHA_REMEDIES = {
    "vata": {
        "raga": "Bhairav",
        "matrika": "LAM",
        "tag": "grounding",
        "recommendation": "Atmosphere is cold/dry. Prioritize hydration and creative ideation over heavy digestion.",
    },
    "pitta": {
        "raga": "Yaman",
        "matrika": "SHAM",
        "tag": "cooling",
        "recommendation": "Heat is active. Choose precise effort, measured speech, and cooling pauses.",
    },
    "kapha": {
        "raga": "Bhairavi",
        "matrika": "RAM",
        "tag": "activation",
        "recommendation": "Density is active. Favor light movement, warm stimulation, and simple momentum.",
    },
}


def normalize_action(action: str) -> str:
    value = (action or "").strip().lower().replace("_", "-")
    aliases = {
        "mental-work": "mental",
        "study": "mental",
        "planning": "mental",
        "physical-work": "physical",
        "exercise": "physical",
        "meal": "eat",
        "eating": "eat",
        "sleep": "rest",
    }
    return aliases.get(value, value)


def normalize_dosha(dosha: str) -> str:
    value = (dosha or "").strip().lower()
    return value if value in {"vata", "pitta", "kapha"} else "kapha"


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def calculate_friction(
    user_action: str,
    current_dosha: str,
    agni_factor: float,
    solar_time: float,
    lunar_velocity: float = 1.0,
    cosmic_angle: float = 0.0,
) -> Dict[str, object]:
    action = normalize_action(user_action)
    dosha = normalize_dosha(current_dosha)
    agni = clamp(float(agni_factor or 0.0))
    lunar = clamp(float(lunar_velocity or 1.0), 0.5, 1.5)

    resonance = ACTION_DOSHA_RESONANCE.get((action, dosha), 0.45)
    metabolic_low = agni < 0.20
    flags: List[str] = []

    if metabolic_low:
        flags.append("metabolic_low")
    if metabolic_low and action == "eat":
        resonance *= 0.25
        flags.append("heavy_digestion_penalty")

    resonance = clamp(resonance * lunar, 0.0, 1.0)
    final_conflict = round(100 - (resonance * agni * 100), 2)
    remedy = DOSHA_REMEDIES[dosha]

    if final_conflict < 20:
        label = "Aligned"
    elif final_conflict < 60:
        label = "Mixed"
    else:
        label = "High Friction"

    return {
        "user_action": action,
        "current_dosha": dosha,
        "solar_time": solar_time,
        "lunar_velocity": lunar,
        "cosmic_angle": cosmic_angle,
        "agni_factor": agni,
        "resonance_score": round(resonance, 4),
        "conflict": final_conflict,
        "label": label,
        "flags": flags,
        "dosha_resonance": remedy["tag"],
        "raga_suggestion": remedy["raga"] if final_conflict > 50 else None,
        "matrika_suggestion": remedy["matrika"] if final_conflict > 50 else None,
        "recommendation": remedy["recommendation"],
    }
