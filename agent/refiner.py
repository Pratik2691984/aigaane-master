"""
agent/refiner.py
Multi-turn verse refinement.

Given a previous verse and a refinement instruction, produce a new verse
that incorporates the requested change while preserving meter.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

from agent.quanta_ledger import QuantaExceeded, QuantaLedger
from engines.chandas.anustubh import validate_anustubh
from engines.chandas.scansion import scan
from engines.gemini_client import GeminiClient, GeminiClientError


logger = logging.getLogger(__name__)


REFINER_SYSTEM_INSTRUCTION = """You are a classical Sanskrit lyricist revising an existing verse.

You will receive:
1. A previous verse (4 pādas, one per line, in IAST)
2. A refinement instruction (in English)

Your task: rewrite the verse to incorporate the refinement while maintaining:
- The same meter (Anuṣṭubh: 4 pādas × 8 syllables = 32 total)
- EXACTLY 4 lines, one pāda per line
- EXACTLY 8 syllables per pāda

Output ONLY the revised verse. No commentary, no explanation.
If the refinement is unclear, make a reasonable interpretation.

Do NOT count syllables yourself — the caller will validate.
"""


class Refiner:
    """Multi-turn verse refinement engine."""

    _TEMPERATURE_SCHEDULE = (0.4, 0.3, 0.2, 0.2, 0.15)

    def __init__(self, gemini: GeminiClient | None = None):
        self.gemini = gemini or GeminiClient()

    async def close(self) -> None:
        return None

    async def refine(
        self,
        previous_verse: str,
        refinement: str,
        meter: str = "anuṣṭubh",
        max_attempts: int = 3,
        ledger_ceiling: int = 300,
    ) -> AsyncIterator[dict]:
        """
        Async generator yielding refinement events.

        Stages:
          - starting
          - drafting      {attempt}
          - scanning
          - validating
          - regenerating  {reason}
          - complete      {verse, pattern, padas, quanta, attempts_used}
          - error         {message}
        """
        ledger = QuantaLedger(ceiling=ledger_ceiling)

        try:
            yield {
                "stage": "starting",
                "previous_verse": previous_verse,
                "refinement": refinement,
                "meter": meter,
            }
            ledger.debit_retrieval()

            base_prompt = (
                f"PREVIOUS VERSE:\n{previous_verse}\n\n"
                f"REFINEMENT INSTRUCTION:\n{refinement}\n\n"
                f"METER: {meter}\n"
                f"Rewrite the verse with the requested change."
            )

            last_error = ""
            last_pattern = ""
            last_pada_counts: list[int] = []

            for attempt in range(1, max_attempts + 1):
                idx = min(attempt - 1, len(self._TEMPERATURE_SCHEDULE) - 1)
                temperature = self._TEMPERATURE_SCHEDULE[idx]

                yield {
                    "stage": "drafting",
                    "attempt": attempt,
                    "temperature": temperature,
                }

                user_prompt = base_prompt
                if last_error:
                    user_prompt += (
                        f"\n\nPREVIOUS REVISION FAILED:\n{last_error}\n"
                        f"Try again with EXACTLY 8 syllables per pāda."
                    )

                try:
                    draft = await self.gemini.generate(
                        system_instruction=REFINER_SYSTEM_INSTRUCTION,
                        user_prompt=user_prompt,
                        temperature=temperature,
                    )
                except GeminiClientError as e:
                    yield {"stage": "error", "message": str(e)}
                    return

                yield {"stage": "scanning"}
                try:
                    scan_result = scan(draft)
                except Exception as e:
                    yield {"stage": "error", "message": f"Scan failed: {e}"}
                    return

                syllable_count = scan_result.length
                try:
                    ledger.debit_aksaras(syllable_count)
                except QuantaExceeded as e:
                    yield {
                        "stage": "error",
                        "message": str(e),
                        "quanta": ledger.snapshot(),
                    }
                    return

                yield {"stage": "validating"}

                if meter.lower() in ("anuṣṭubh", "anustubh"):
                    try:
                        anu_result = validate_anustubh(draft)
                    except Exception as e:
                        yield {"stage": "error", "message": f"Validate failed: {e}"}
                        return

                    if anu_result.is_valid:
                        yield {
                            "stage": "complete",
                            "previous_verse": previous_verse,
                            "refinement": refinement,
                            "verse": draft,
                            "pattern": scan_result.pattern,
                            "length": scan_result.length,
                            "padas": [
                                {
                                    "index": p.index,
                                    "text_pattern": p.text_pattern,
                                    "variety": p.variety,
                                    "is_valid": p.is_valid,
                                    "reason": p.reason,
                                }
                                for p in anu_result.padas
                            ],
                            "quanta": ledger.snapshot(),
                            "attempts_used": attempt,
                        }
                        return

                    last_pattern = scan_result.pattern
                    last_error = "; ".join(anu_result.errors)
                    last_pada_counts = [scan(ln).length for ln in draft.splitlines() if ln.strip()]
                    yield {
                        "stage": "regenerating",
                        "reason": last_error,
                        "per_pada_counts": last_pada_counts,
                        "total_syllables": syllable_count,
                    }
                else:
                    # Non-Anuṣṭubh meters: just report scan
                    yield {
                        "stage": "complete",
                        "previous_verse": previous_verse,
                        "refinement": refinement,
                        "verse": draft,
                        "pattern": scan_result.pattern,
                        "length": scan_result.length,
                        "quanta": ledger.snapshot(),
                        "attempts_used": attempt,
                    }
                    return

            yield {
                "stage": "error",
                "message": f"Could not refine to valid {meter} after {max_attempts} attempts",
                "last_pattern": last_pattern,
                "last_error": last_error,
                "quanta": ledger.snapshot(),
            }

        except Exception as e:
            logger.exception("refiner.refine crashed")
            yield {"stage": "error", "message": str(e)}


if __name__ == "__main__":
    import asyncio

    class MockGemini:
        async def generate(self, **kwargs):
            return (
                "sarasvatī namastubhyaṃ\n"
                "varade kāmarūpini\n"
                "vidyārambhaṃ kariṣyāmi\n"
                "siddhiḥ bhavatu me sadā"
            )

    async def run():
        refiner = Refiner(gemini=MockGemini())
        events = []
        async for e in refiner.refine(
            previous_verse="test verse",
            refinement="add more devotion",
        ):
            events.append(e)
        assert events[-1]["stage"] in ("complete", "error")
        print("refiner.py OK")

    asyncio.run(run())