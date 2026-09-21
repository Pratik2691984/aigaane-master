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

STRATEGY:
  - Low temperature on first attempt (0.5) for stability.
  - Progressive lowering on retries (0.5 → 0.4 → 0.3) to force precision.
  - Few-shot exemplar of a valid Anuṣṭubh verse in the system prompt.
  - Pāda-4-first composition to combat the "short last line" bias.
  - Per-pāda surgical feedback on retries.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

from agent.quanta_ledger import QuantaExceeded, QuantaLedger
from engines.chandas.anustubh import validate_anustubh
from engines.chandas.scansion import scan
from engines.gemini_client import GeminiClient, GeminiClientError


logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────
# System prompt
# ────────────────────────────────────────────────────────────────

SYSTEM_INSTRUCTION = """You are a classical Sanskrit lyricist composing STRICTLY in Anuṣṭubh meter.

═══════════════════════════════════════════════════════════════════
CRITICAL METER REQUIREMENT — ANUṢṬUBH
═══════════════════════════════════════════════════════════════════
Anuṣṭubh has EXACTLY 32 syllables: 4 pādas × 8 syllables each.

EACH pāda MUST have EXACTLY 8 syllables. Not 7. Not 9. EXACTLY 8.

How to count syllables (akṣaras):
  - Each vowel = 1 syllable
  - Long vowels (ā, ī, ū) = 1 syllable
  - Diphthongs (ai, au, e, o) = 1 syllable
  - Anusvāra (ṃ), visarga (ḥ), and trailing consonants attach to the preceding vowel
  Example: rā-mo-'ga-ccha-ti = 5 syllables

═══════════════════════════════════════════════════════════════════
COMPOSITION ORDER — FOLLOW EXACTLY
═══════════════════════════════════════════════════════════════════
STEP 1: Compose PĀDA 4 FIRST with EXACTLY 8 syllables.
STEP 2: Then compose PĀDA 3 with EXACTLY 8 syllables.
STEP 3: Then compose PĀDA 2 with EXACTLY 8 syllables.
STEP 4: Then compose PĀDA 1 with EXACTLY 8 syllables.

WHY: Pāda 4 is the most common failure point. By composing it first,
you anchor the verse and prevent the "short last line" problem.

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
- EXACTLY one newline between pādas
- NO blank lines
- NO title, commentary, translation, or scansion notation
- IAST transliteration only (not Devanagari)
- NO punctuation (no danda, no comma, no period)

═══════════════════════════════════════════════════════════════════
EXAMPLE OF A VALID ANUṢṬUBH VERSE
═══════════════════════════════════════════════════════════════════
tapaḥsvādhyāyanirataṃ
tapasvī vāgvidāṃ varam
nāradaṃ paripapraccha
vālmīkir munisattamam

Verify: 8 + 8 + 8 + 8 = 32 syllables. ✓

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
        """Execute Anuṣṭubh validation in-process."""
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
        # If not 4 lines, report total only
        return [scan(text).length]

    @staticmethod
    def _build_surgical_feedback(
        per_pada_counts: list[int],
        total: int,
        target_per_pada: int = 8,
    ) -> str:
        """
        Build an explicit, per-pāda failure report for the model.
        Returns a short string naming which pādas need fixing.
        """
        if len(per_pada_counts) != 4:
            return (
                f"Output has {total} syllables total (need 32). "
                f"Ensure EXACTLY 4 pādas, one per line. "
                f"Each pāda must have EXACTLY 8 syllables."
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
        """
        ledger = QuantaLedger(ceiling=ledger_ceiling)

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
            system_prompt += "\nTARGET: 4 pādas, EXACTLY 8 syllables each = 32 total."

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

                # Build user prompt with surgical retry feedback
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
                        f"1. Compose PĀDA 4 first, EXACTLY 8 syllables.\n"
                        f"2. Then compose pādas 3, 2, 1 in that order.\n"
                        f"3. Every pāda must have EXACTLY 8 syllables.\n"
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

                # ── 5. Validate ──
                yield {"stage": "validating"}

                if meter.lower() in ("anuṣṭubh", "anustubh"):
                    try:
                        anu_result = await self._validate_anustubh(draft)
                    except Exception as e:
                        yield {"stage": "error", "message": f"Validate failed: {e}"}
                        return

                    if anu_result.get("is_valid"):
                        yield {
                            "stage": "complete",
                            "prompt": prompt,
                            "verse": draft,
                            "pattern": scan_result.get("pattern"),
                            "length": scan_result.get("length"),
                            "padas": anu_result.get("padas", []),
                            "quanta": ledger.snapshot(),
                            "attempts_used": attempt,
                        }
                        return

                    # Capture failure info
                    last_pattern = scan_result.get("pattern", "")
                    last_error = "; ".join(anu_result.get("errors", []))
                    last_pada_counts = self._split_pada_counts(draft)
                    last_feedback = self._build_surgical_feedback(
                        last_pada_counts, syllable_count
                    )

                    yield {
                        "stage": "regenerating",
                        "reason": last_error,
                        "per_pada_counts": last_pada_counts,
                        "total_syllables": syllable_count,
                        "feedback": last_feedback,
                    }
                else:
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