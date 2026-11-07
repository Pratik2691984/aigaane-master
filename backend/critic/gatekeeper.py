"""
CEGAR Gatekeeper — Two-Tier Stem Attestation (v1.3.0).

Tier 1: `_lexicon.lookup()` — primary source, ~2,500–5,000 curated stems
Tier 2: `canon.db` FTS5 — secondary source, 701 Gītā verses (proper nouns)

Fail-closed design:
  - If `_lexicon` cannot be imported, backend refuses to start
  - If `canon.db` is missing, Tier 2 is skipped (with a warning)
  - Any exception during lookup = UNATTESTED (fail-closed)
  - The Critic boots only if Tier 1 is available
"""

import logging
import sqlite3
import sys
from pathlib import Path

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

CANON_DB_PATH = Path("C:/aigaane-master/frontend/public/sqlite/canon.db")


class CegarGatekeeper:
    def __init__(self):
        if not _LEXICON_OK or not hasattr(legacy_lexicon, "lookup"):
            raise RuntimeError(
                "FATAL: CegarGatekeeper cannot boot. "
                "_lexicon.lookup is unavailable. "
                "Fail-closed design requires the primary attestation source."
            )
        self.lookup_fn = legacy_lexicon.lookup

        # Tier 2: canon.db (optional, does not fail-closed on absence)
        if CANON_DB_PATH.exists():
            try:
                # Smoke-test: verify table exists
                conn = sqlite3.connect(str(CANON_DB_PATH))
                conn.execute("SELECT 1 FROM verses_fts LIMIT 1").fetchone()
                conn.close()
                self.canon_db = str(CANON_DB_PATH)
                logger.info(f"Gatekeeper online — Tier 1 (_lexicon) + Tier 2 ({CANON_DB_PATH.name})")
            except Exception as e:
                logger.warning(f"canon.db present but unusable: {e}. Running with Tier 1 only.")
                self.canon_db = None
        else:
            logger.warning(f"canon.db not found at {CANON_DB_PATH}. Running with Tier 1 only.")
            self.canon_db = None

    # ---------------------------------------------------------------- #
    #   Tier 1: Engine lexicon                                          #
    # ---------------------------------------------------------------- #
    def _attest_lexicon(self, stem: str) -> bool:
        try:
            return self.lookup_fn(stem) is not None
        except Exception as e:
            logger.warning(f"_lexicon.lookup('{stem}') raised: {e} — rejecting (fail-closed)")
            return False

    # ---------------------------------------------------------------- #
    #   Tier 2: canon.db FTS5                                           #
    # ---------------------------------------------------------------- #
    def _attest_canon(self, stem: str) -> bool:
        if not self.canon_db:
            return False
        try:
            # FTS5 MATCH searches for the term as a word; use prefix matching
            # to catch inflected forms (e.g., "indr" matches "indra", "indrāḥ")
            term = stem.lower().strip()
            if not term:
                return False
            # Use FTS5 prefix search: "indr*" catches indra, indrāḥ, indreṇa, etc.
            query = f"{term}*"
            conn = sqlite3.connect(self.canon_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM verses_fts WHERE verses_fts MATCH ? LIMIT 1",
                (query,)
            )
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.warning(f"canon.db FTS query for '{stem}' failed: {e} — rejecting")
            return False

    # ---------------------------------------------------------------- #
    #   Combined attestation                                            #
    # ---------------------------------------------------------------- #
    def _attest_stem(self, stem: str) -> bool:
        if not stem or not isinstance(stem, str):
            return False
        if stem.lower() in {"unknown", "unparsed", "error"}:
            return False

        # Tier 1: engine lexicon (primary)
        if self._attest_lexicon(stem):
            return True

        # Tier 2: canon.db (secondary, for proper nouns)
        if self._attest_canon(stem):
            logger.info(f"Stem '{stem}' attested via canon.db (Tier 2)")
            return True

        return False

    # ---------------------------------------------------------------- #
    #   Envelope verification                                           #
    # ---------------------------------------------------------------- #
    def verify(self, envelope: KernelEnvelope) -> KernelEnvelope:
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
                    f"stem '{bad_stem}' not in Tier 1 or Tier 2"
                )

        kept.sort(key=lambda c: c.score, reverse=True)
        for idx, cand in enumerate(kept):
            cand.candidate_id = f"cand_{idx + 1:02d}"

        envelope.candidates = kept
        envelope.rejected = rejected

        return envelope