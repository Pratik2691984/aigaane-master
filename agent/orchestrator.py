"""
agent/orchestrator.py
Track A: Agentic RAG for metrically-grounded Sanskrit verse generation.

ARCHITECTURAL RULES:
  1. The LLM MUST NOT scan meter itself. Every draft is validated by
     Track B's deterministic scanners, called in-process.
  2. No HTTP self-calls — the orchestrator runs in the same container as
     the Track B engine and imports it directly.
  3. No decorator on `generate_verse` — it is an async generator and
     cannot be wrapped by `canonical_read_only`.

WEEK 1: Supports Anuṣṭubh, Triṣṭubh, and Jagatī meters.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

from agent.quanta_ledger import QuantaExceeded, QuantaLedger
from engines.chandas.anustubh import validate_anustubh
from engines.chandas.scansion import scan
from engines.chandas.trishtubh import validate_trishtubh
from engines.chandas.jagati import validate_jagati
from engines.gemini_client import GeminiClient, GeminiClientError


logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────
# Meter-specific syllable targets
# ────────────────────────────────────────────────────────────────

_METER_TARGETS = {
    "anuṣṭubh": "4 pādas of EXACTLY 8 syllables each (32 total)",
    "anustubh": "4 pādas of EXACTLY 8 syllables each (32 total)",
    "triṣṭubh": "4 pādas of EXACTLY 11 syllables each (44 total)",
    "trishtubh": "4 pādas of EXACTLY 11 syllables each (44 total)",
    "jagatī": "4 pādas of EXACTLY 12 syllables each (48 total)",
    "jagati": "4 pādas of EXACTLY 12 syllables each (48 total)",
}


# ────────────────────────────────────────────────────────────────
# System prompt
# ────────────────────────────────────────────────────────────────

SYSTEM_INSTRUCTION = """You are a classical Sanskrit lyricist composing STRICTLY in the requested meter.

═══════════════════════════════════════════════════════════════════
CRITICAL METER REQUIREMENT
═══════════════════════════════════════════════════════════════════
Every verse has EXACTLY 4 pādas. Each pāda MUST have the EXACT syllable count specified.

EACH pāda must have EXACTLY the target syllable count. Not one less. Not one more.

How to count syllables (akṣaras):
  - Each vowel = 1 syllable
  - Long vowels (ā, ī, ū) = 1 syllable
  - Diphthongs (ai, au, e, o) = 1 syllable
  - Anusvāra (ṃ), visarga (ḥ), and trailing consonants attach to the preceding vowel

═══════════════════════════════════════════════════════════════════
COMPOSITION ORDER — FOLLOW EXACTLY
═══════════════════════════════════════════════════════════════════
STEP 1: Compose PĀDA 4 FIRST with EXACTLY the target syllables.
STEP 2: Then compose PĀDA 3 with EXACTLY the target syllables.
STEP 3: Then compose PĀDA 2 with EXACTLY the target syllables.
STEP 4: Then compose PĀDA 1 with EXACTLY the target syllables.

WHY: Pāda 4 is the most common failure point. Composing it first anchors
the verse and prevents the "short last line" problem.

═══════════════════════════════════════════════════════════════════
OUTPUT FORMAT — STRICTLY ENFORCED
═══════════════════════════════════════════════════════════════════
Return ONLY the verse in this exact format:

<pāda 1 text>
<pāda 2 text>
<pāda 3 text>
<pāda 4 text>

Rules:
- ONE pāda per line
- EXACTLY 4 lines
- NO blank lines
- NO title, commentary, translation, or scansion notation
- IAST transliteration only (not Devanagari)
- NO punctuation (no danda, no comma, no period)

═══════════════════════════════════════════════════════════════════
YOU MUST NOT
═══════════════════════════════════════════════════════════════════
- Self-scan laghu/guru (a deterministic engine will validate)
- Include commentary, translations, or explanations
- Output more than 4 pādas or fewer than 4 pādas
- Use Devanagari
- Concatenate pādas onto one line

IAST diacritics: ā ī ū ṛ ṝ ḷ ḹ e ai o au ṃ ḥ ṅ ñ ṭ ḍ ṇ ś ṣ
"""


# ────────────────────────────────────────────────────────────────
# Orchestrator
# ────────────────────────────────────────────────────────────────

class Orchestrator:
    """
    Track A orchestrator: generation → scan → validate → regenerate loop.

    Supports: Anuṣṭubh, Triṣṭubh, Jagatī.
    """

    _TEMPERATURE_SCHEDULE = (0.3, 0.25, 0.2, 0.15, 0.1)

    def __init__(self, gemini: GeminiClient | None = None):
        self.gemini = gemini or GeminiClient()

    async def close(self) -> None:
        return None

    # ─────────────────────── Track B (in-process) ───────────────────────

    async def _scan_meter(self, text: str) -> dict:
        """Execute deterministic scansion in-process."""
        result = scan(text)
        return {
            "input": result.input,
            "syllables": [
                {"text": s.text, "weight": s.weight, "position": s.position}
                for s in result.syllables
            ],
            "pattern": result.pattern,
            "length": result.length,
        }

    async def _validate_anustubh(self, text: str) -> dict:
        result = validate_anustubh(text)
        return {
            "input": result.input,
            "is_valid": result.is_valid,
            "padas": [
                {
                    "index": p.index,
                    "text_pattern": p.text_pattern,
                    "variety": p.variety,
                    "is_valid": p.is_valid,
                    "reason": p.reason,
                }
                for p in result.padas
            ],
            "errors": result.errors,
        }

    # ─────────────────────── Diagnostics ───────────────────────

    @staticmethod
    def _split_pada_counts(text: str) -> list[int]:
        """Return syllable count per line (pāda)."""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            return [scan(text).length]
        if len(lines) == 4:
            return [scan(ln).length for ln in lines]
        return [scan(text).length]

    @staticmethod
    def _build_surgical_feedback(
        per_pada_counts: list[int],
        total: int,
        target_per_pada: int = 8,
    ) -> str:
        """Build per-pāda failure report."""
        if len(per_pada_counts) != 4:
            return (
                f"Output has {total} syllables total (need 4 pādas × "
                f"{target_per_pada}). Ensure EXACTLY 4 pādas, one per line."
            )

        correct = []
        broken = []
        for i, count in enumerate(per_pada_counts, start=1):
            if count == target_per_pada:
                correct.append(f"pāda {i}")
            else:
                diff = target_per_pada - count
                sign = "+" if diff > 0 else ""
                broken.append(f"pāda {i} has {count} (need {target_per_pada}, {sign}{diff})")

        parts = []
        if correct:
            parts.append(f"CORRECT: {', '.join(correct)}")
        if broken:
            parts.append(f"WRONG: {'; '.join(broken)}")
        return " | ".join(parts)

    # ─────────────────────── RAG retrieval (stub) ───────────────────────

    async def _retrieve_anchors(self, prompt: str) -> list[str]:
        """Placeholder for vector retrieval."""
        return []

    # ─────────────────────── Core loop ───────────────────────

    async def generate_verse(
        self,
        prompt: str,
        meter: str = "anuṣṭubh",
        max_attempts: int = 3,
        ledger_ceiling: int = 300,
    ) -> AsyncIterator[dict]:
        """
        Async generator yielding SSE-ready events.

        Stages:
          - retrieving
          - drafting      {attempt, temperature}
          - scanning
          - validating
          - regenerating  {reason, per_pada_counts}
          - complete      {verse, pattern, padas, quanta, prompt}
          - error         {message}
        """
        ledger = QuantaLedger(ceiling=ledger_ceiling)
        meter_key = meter.lower()

        # Determine target syllables for feedback
        if meter_key in ("anuṣṭubh", "anustubh"):
            target_per_pada = 8
            total_target = 32
        elif meter_key in ("triṣṭubh", "trishtubh"):
            target_per_pada = 11
            total_target = 44
        elif meter_key in ("jagatī", "jagati"):
            target_per_pada = 12
            total_target = 48
        else:
            target_per_pada = 8
            total_target = 32

        try:
            # ── 1. Retrieval ──
            yield {"stage": "retrieving"}
            try:
                anchors = await self._retrieve_anchors(prompt)
                ledger.debit_retrieval()
            except Exception as e:
                yield {"stage": "error", "message": f"Retrieval failed: {e}"}
                return

            # ── 2. Build system prompt ──
            system_prompt = SYSTEM_INSTRUCTION
            if anchors:
                system_prompt += "\n\nCORPUS ANCHORS:\n" + "\n".join(
                    f"- {a}" for a in anchors
                )
            system_prompt += f"\n\nREQUESTED METER: {meter}"
            target_line = _METER_TARGETS.get(
                meter_key, f"4 pādas of EXACTLY {target_per_pada} syllables each"
            )
            system_prompt += f"\nTARGET: {target_line}."

            # ── 3. Generation + validation loop ──
            last_pattern = ""
            last_error = ""
            last_pada_counts: list[int] = []
            last_feedback = ""

            for attempt in range(1, max_attempts + 1):
                idx = min(attempt - 1, len(self._TEMPERATURE_SCHEDULE) - 1)
                temperature = self._TEMPERATURE_SCHEDULE[idx]

                yield {
                    "stage": "drafting",
                    "attempt": attempt,
                    "temperature": temperature,
                }

                user_prompt = prompt
                if last_feedback:
                    user_prompt += (
                        f"\n\n═══════════════════════════════════════════\n"
                        f"PREVIOUS ATTEMPT REJECTED\n"
                        f"═══════════════════════════════════════════\n"
                        f"{last_feedback}\n\n"
                        f"Full scansion pattern: {last_pattern}\n"
                        f"Total syllables: {sum(last_pada_counts) if last_pada_counts else 'N/A'}\n\n"
                        f"INSTRUCTIONS FOR NEXT ATTEMPT:\n"
                        f"1. Compose PĀDA 4 first, EXACTLY {target_per_pada} syllables.\n"
                        f"2. Then compose pādas 3, 2, 1 in that order.\n"
                        f"3. Every pāda must have EXACTLY {target_per_pada} syllables.\n"
                        f"4. Output EXACTLY 4 lines (one pāda per line)."
                    )

                # Generate
                try:
                    draft = await self.gemini.generate(
                        system_instruction=system_prompt,
                        user_prompt=user_prompt,
                        temperature=temperature,
                    )
                except GeminiClientError as e:
                    yield {"stage": "error", "message": str(e)}
                    return

                # ── 4. Track B scan ──
                yield {"stage": "scanning"}
                try:
                    scan_result = await self._scan_meter(draft)
                except Exception as e:
                    yield {"stage": "error", "message": f"Scan failed: {e}"}
                    return

                syllable_count = scan_result.get("length", 0)
                try:
                    ledger.debit_aksaras(syllable_count)
                except QuantaExceeded as e:
                    yield {
                        "stage": "error",
                        "message": str(e),
                        "quanta": ledger.snapshot(),
                    }
                    return

                # ── 5. Validate meter ──
                yield {"stage": "validating"}

                is_valid_meter = False
                pada_results = []
                error_message = ""

                if meter_key in ("anuṣṭubh", "anustubh"):
                    try:
                        anu_result = await self._validate_anustubh(draft)
                        is_valid_meter = anu_result.get("is_valid", False)
                        pada_results = anu_result.get("padas", [])
                        if not is_valid_meter:
                            error_message = "; ".join(anu_result.get("errors", []))
                    except Exception as e:
                        yield {"stage": "error", "message": f"Validate failed: {e}"}
                        return

                elif meter_key in ("triṣṭubh", "trishtubh"):
                    try:
                        tri_result = validate_trishtubh(draft)
                        is_valid_meter = tri_result.is_valid
                        pada_results = [
                            {
                                "index": p.index,
                                "text_pattern": p.text_pattern,
                                "variety": p.variety,
                                "is_valid": p.is_valid,
                                "reason": p.reason,
                            }
                            for p in tri_result.padas
                        ]
                        if not is_valid_meter:
                            error_message = "; ".join(tri_result.errors)
                    except Exception as e:
                        yield {"stage": "error", "message": f"Validate failed: {e}"}
                        return

                elif meter_key in ("jagatī", "jagati"):
                    try:
                        jag_result = validate_jagati(draft)
                        is_valid_meter = jag_result.is_valid
                        pada_results = [
                            {
                                "index": p.index,
                                "text_pattern": p.text_pattern,
                                "variety": p.variety,
                                "is_valid": p.is_valid,
                                "reason": p.reason,
                            }
                            for p in jag_result.padas
                        ]
                        if not is_valid_meter:
                            error_message = "; ".join(jag_result.errors)
                    except Exception as e:
                        yield {"stage": "error", "message": f"Validate failed: {e}"}
                        return

                else:
                    # Unknown meter: accept after scan
                    yield {
                        "stage": "complete",
                        "prompt": prompt,
                        "verse": draft,
                        "pattern": scan_result.get("pattern"),
                        "length": scan_result.get("length"),
                        "quanta": ledger.snapshot(),
                        "attempts_used": attempt,
                    }
                    return

                if is_valid_meter:
                    yield {
                        "stage": "complete",
                        "prompt": prompt,
                        "verse": draft,
                        "pattern": scan_result.get("pattern"),
                        "length": scan_result.get("length"),
                        "padas": pada_results,
                        "quanta": ledger.snapshot(),
                        "attempts_used": attempt,
                    }
                    return

                # Failed — build feedback for next attempt
                last_pattern = scan_result.get("pattern", "")
                last_error = error_message
                last_pada_counts = self._split_pada_counts(draft)
                last_feedback = self._build_surgical_feedback(
                    last_pada_counts, syllable_count, target_per_pada=target_per_pada
                )
                yield {
                    "stage": "regenerating",
                    "reason": last_error,
                    "per_pada_counts": last_pada_counts,
                    "total_syllables": syllable_count,
                    "feedback": last_feedback,
                }

            # ── 6. Max attempts exceeded ──
            yield {
                "stage": "error",
                "message": (
                    f"Could not produce valid {meter} after "
                    f"{max_attempts} attempts"
                ),
                "last_pattern": last_pattern,
                "last_error": last_error,
                "last_per_pada_counts": last_pada_counts,
                "last_feedback": last_feedback,
                "quanta": ledger.snapshot(),
            }

        except Exception as e:
            logger.exception("orchestrator.generate_verse crashed")
            yield {"stage": "error", "message": str(e)}