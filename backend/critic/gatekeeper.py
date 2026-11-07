"""
CEGAR Gatekeeper — Real Lexicon-Backed Stem Attestation.

Uses the engine's own `_lexicon.lookup()` as the authoritative source of
truth. If a candidate's stem cannot be found in the lexicon, the candidate
is REJECTED with reason_code UNATTESTED_STEM.

Fail-closed design:
  - If `_lexicon` cannot be imported, the backend refuses to start
  - If `lookup()` raises for any reason, the stem is REJECTED (not accepted)
  - No silent pass-through, no whitelist fallback, no LLM guessing
"""

import logging
import sys
from pathlib import Path

# The legacy engine lives in backend/engine/. We import its sibling _lexicon.
_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

try:
    import _lexicon as legacy_lexicon
    _LEXICON_OK = True
except Exception as e:
    legacy_lexicon = None
    _LEXICON_OK = False
    logging.error(f"FATAL: _lexicon not importable from {_ENGINE_DIR}: {e}")

from backend.engine.pydantic_models import (
    KernelEnvelope,
    RejectedCandidate,
    Candidate,
)

logger = logging.getLogger(__name__)


class CegarGatekeeper:
    def __init__(self):
        if not _LEXICON_OK or not hasattr(legacy_lexicon, "lookup"):
            raise RuntimeError(
                "FATAL: CegarGatekeeper cannot boot. "
                "_lexicon.lookup is unavailable. "
                "The Critic's entire purpose is stem attestation against "
                "the engine's own lexicon. Without it, the backend refuses "
                "to start (fail-closed)."
            )
        self.lookup_fn = legacy_lexicon.lookup
        logger.info("CegarGatekeeper online — backed by _lexicon.lookup()")

    # ---------------------------------------------------------------- #
    #   Per-stem attestation                                            #
    # ---------------------------------------------------------------- #
    def _attest_stem(self, stem_iast: str) -> bool:
        """
        Return True iff the stem is attested in the engine's lexicon.

        Fails CLOSED: any exception from lookup() = unattested.
        Empty/unknown/None stems are unattested.
        """
        if not stem_iast or not isinstance(stem_iast, str):
            return False
        if stem_iast.lower() in {"unknown", "unparsed", "error"}:
            return False

        try:
            result = self.lookup_fn(stem_iast)
        except Exception as e:
            logger.warning(f"lookup('{stem_iast}') raised: {e} — rejecting (fail-closed)")
            return False

        return result is not None

    # ---------------------------------------------------------------- #
    #   Envelope verification                                           #
    # ---------------------------------------------------------------- #
    def verify(self, envelope: KernelEnvelope) -> KernelEnvelope:
        """
        Walk every candidate, attest every stem.

        If ALL stems in a candidate are attested → keep the candidate.
        If ANY stem fails → move it to rejected[] with UNATTESTED_STEM.
        """
        kept: list[Candidate] = []
        rejected: list[RejectedCandidate] = list(envelope.rejected)

        for cand in envelope.candidates:
            bad_stem = None
            for token in cand.parse:
                if not self._attest_stem(token.stem):
                    bad_stem = token.stem
                    break

            if bad_stem is None:
                kept.append(cand)
            else:
                rejected.append(
                    RejectedCandidate(
                        parse=cand.parse,
                        reason_code="UNATTESTED_STEM",
                        violated_sutra=None,
                    )
                )
                logger.info(
                    f"Candidate {cand.candidate_id} rejected: "
                    f"stem '{bad_stem}' not in lexicon"
                )

        # Stable sort by score descending
        kept.sort(key=lambda c: c.score, reverse=True)

        # Reassign candidate IDs in final ranking order
        for idx, cand in enumerate(kept):
            cand.candidate_id = f"cand_{idx + 1:02d}"

        envelope.candidates = kept
        envelope.rejected = rejected

        return envelope