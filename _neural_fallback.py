"""
Pillar 1 Neural-Symbolic Fallback Scaffolding for Aigaane.
Invokes Google GenAI SDK with structured schema enforcement when Pāṇinian rule engines return None.
"""
import os
import re
import json
import uuid
from typing import Optional, Dict, Any

try:
    from google import genai
    from google.genai import types
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False


def is_valid_sanskrit_surface(text: str) -> bool:
    """Rejects strings containing digits, underscores, or non-linguistic noise."""
    if not text:
        return False
    if any(ch.isdigit() or ch in "_$#@*&^%+=~`<>{}" for ch in text):
        return False
    cleaned = re.sub(r"[\s\.,।॥\-']+", "", text)
    return len(cleaned) > 0


FALLBACK_SYSTEM_PROMPT = """You are the Pāṇinian Sanskrit morphological fallback engine for Aigaane.
When deterministic rule tables and finite-state transducers do not match an input, analyze the Sanskrit word or sentence
and return a strictly structured JSON document following schema version 0.2.0.

JSON requirements:
{
  "schema_version": "0.2.0",
  "tokens": [
    {
      "token_id": "T0",
      "pada": "<surface word>",
      "stem": "<uninflected pratipadika or dhatu>",
      "pos": "subhanta" | "tinanta" | "avyaya",
      "vibhakti": "prathama" | "dvitiya" | "na",
      "vacana": "ekavacana" | "dvivacana" | "bahuvacana",
      "linga": "pullinga" | "strilinga" | "napumsakalinga" | "na",
      "dhatu": "<optional root if tinanta>",
      "purusa": "<optional person if tinanta>",
      "lakara": "<optional tense/mood if tinanta>",
      "confidence": 0.75
    }
  ],
  "confidence": 0.75,
  "provenance": ["engine=hybrid-neural-fallback", "model=gemini-2.5-flash"]
}
Only output raw JSON. Do not wrap in markdown fences or backticks.
"""


def is_llm_available() -> bool:
    """Checks if API key and SDK are available."""
    return bool(_GENAI_AVAILABLE and os.getenv("GEMINI_API_KEY"))


def fallback_parse(surface: str, raw_surface: str, deva: str, script_original: str) -> Optional[Dict[str, Any]]:
    """
    Executes an LLM fallback call when deterministic parsing yields None.
    If the surface contains non-Sanskrit noise (digits, underscores), returns None
    so the API layer can return 422 Unprocessable Entity.
    """
    if not is_valid_sanskrit_surface(raw_surface) or not is_valid_sanskrit_surface(surface):
        return None

    trace_id = str(uuid.uuid4())

    if not is_llm_available():
        return {
            "schema_version": "0.2.0",
            "trace_id": trace_id,
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": [
                {
                    "token_id": "T0",
                    "pada": raw_surface,
                    "stem": surface,
                    "pos": "subhanta",
                    "vibhakti": "prathama",
                    "vacana": "ekavacana",
                    "linga": "pullinga",
                    "confidence": 0.50,
                }
            ],
            "sandhi_splits": [],
            "ambiguous_parses": [],
            "canon_refs": [],
            "confidence": 0.50,
            "confidence_aggregate": {"min": 0.50, "mean": 0.50},
            "provenance": ["engine=heuristic-unknown-fallback"],
        }

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Analyze Sanskrit surface: {raw_surface} (IAST: {surface})",
            config=types.GenerateContentConfig(
                system_instruction=FALLBACK_SYSTEM_PROMPT,
                temperature=0.0,
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        data["trace_id"] = trace_id
        data["surface"] = raw_surface
        data["normalized"] = deva
        data["script_original"] = script_original
        data["transliteration"] = {"devanagari": deva, "iast": surface}
        data["sandhi_splits"] = data.get("sandhi_splits", [])
        data["ambiguous_parses"] = data.get("ambiguous_parses", [])
        data["canon_refs"] = data.get("canon_refs", [])
        data["confidence"] = min(data.get("confidence", 0.75), 0.75)
        confs = [t.get("confidence", 0.75) for t in data.get("tokens", [])] or [0.75]
        data["confidence_aggregate"] = {"min": min(confs), "mean": sum(confs) / len(confs)}
        return data
    except Exception:
        return {
            "schema_version": "0.2.0",
            "trace_id": trace_id,
            "script_original": script_original,
            "surface": raw_surface,
            "normalized": deva,
            "transliteration": {"devanagari": deva, "iast": surface},
            "parse_rank": 1,
            "tokens": [
                {
                    "token_id": "T0",
                    "pada": raw_surface,
                    "stem": surface,
                    "pos": "subhanta",
                    "vibhakti": "prathama",
                    "vacana": "ekavacana",
                    "linga": "pullinga",
                    "confidence": 0.50,
                }
            ],
            "sandhi_splits": [],
            "ambiguous_parses": [],
            "canon_refs": [],
            "confidence": 0.50,
            "confidence_aggregate": {"min": 0.50, "mean": 0.50},
            "provenance": ["engine=heuristic-degraded-fallback"],
        }
