"""Pillar 1: Gemini neural boundary for rāga swara phrasing.

Consumes metrical chandas weights, emits structured SwaraSequence.
Falls back deterministically if Gemini is unavailable or emits malformed tokens.
"""
import json
import logging
from typing import Optional

from google import genai
from google.genai import types

from aigaane.neural.schemas import ChandasInput, SwaraSequence, SwaraToken
from aigaane.neural.guards import validate_swara_sequence, validate_sanskrit_text
from aigaane.neural.confidence import cap_confidence

logger = logging.getLogger(__name__)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "sequence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "swara": {"type": "string"},
                    "meend_target": {"type": "string", "nullable": True},
                },
                "required": ["swara"],
            },
        },
        "confidence": {"type": "number"},
        "rationale": {"type": "string"},
    },
    "required": ["sequence", "confidence", "rationale"],
}

SYSTEM_PROMPT = """You are the swara phrasing engine for Rāga Bhairav.

RULES:
1. Return ONLY valid JSON matching the provided schema.
2. Allowed swaras for Bhairav: S, r, G, M, P, d, N, S'.
3. NEVER output frequencies, cents, ratios, MIDI values, or beat positions.
4. Confidence must be between 0.0 and 0.75.
5. Rationale must be under 280 characters.
"""


class GeminiSwaraEngine:
    def __init__(self, project_id: str = "gen-lang-client-0991678000", model: str = "gemini-2.5-flash"):
        self.project_id = project_id
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = genai.Client(vertexai=True, project=self.project_id, location="us-central1")
        return self._client

    def phrase(self, chandas: ChandasInput) -> Optional[SwaraSequence]:
        """Attempt neural phrasing with deterministic validation."""
        if not validate_sanskrit_text(chandas.verse_text):
            return None

        if not all(w in ("L", "G") for w in chandas.weights):
            return None

        prompt = (
            f"Verse: {chandas.verse_text}\n"
            f"Weights: {' '.join(chandas.weights)}\n"
            f"Length: {len(chandas.syllables)}\n"
            f"Target Rāga: {chandas.target_raga}\n"
            f"Compose a {len(chandas.syllables)}-note sequence."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    max_output_tokens=1024,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                ),
            )
            raw = json.loads(response.text)
            seq = SwaraSequence(
                sequence=[
                    SwaraToken(swara=t["swara"], meend_target=t.get("meend_target"))
                    for t in raw["sequence"]
                ],
                confidence=cap_confidence(raw["confidence"]),
                rationale=raw["rationale"],
            )
            validate_swara_sequence(seq, chandas.target_raga)
            return seq

        except Exception as e:
            logger.warning(f"Neural phrasing fallback triggered: {e}")
            return None


def deterministic_fallback(chandas: ChandasInput) -> SwaraSequence:
    """Canonical 5-limit Bhairav ārohaṇa fallback when neural layer is bypassed."""
    pattern = ["S", "r", "G", "M", "P", "d", "N", "S'"]
    n = len(chandas.syllables)
    seq = [
        SwaraToken(
            swara=pattern[i % len(pattern)],
            meend_target="G" if pattern[i % len(pattern)] == "r" else ("N" if pattern[i % len(pattern)] == "d" else None)
        )
        for i in range(n)
    ]
    return SwaraSequence(
        sequence=seq,
        confidence=0.0,
        rationale="Deterministic 5-limit Bhairav fallback (neural layer bypassed)",
    )
