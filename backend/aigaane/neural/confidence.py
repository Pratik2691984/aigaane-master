"""Confidence capping - neural confidence never exceeds 0.75."""
MAX_CONFIDENCE = 0.75


def cap_confidence(raw: float) -> float:
    """Hard ceiling regardless of what the neural model claims."""
    return min(float(raw), MAX_CONFIDENCE)
