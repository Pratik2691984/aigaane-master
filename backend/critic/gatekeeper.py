"""
CEGAR Gatekeeper — Two-Tier Stem Attestation (v1.4.1).

Tier 1: `_lexicon.lookup()` — primary source, ~2,500–5,000 curated stems
        + `_lexicon_supplement.py` — 30+ epic proper nouns
Tier 2: `canon.db` FTS5 — secondary source, 701 Gītā verses

Improvement (v1.4.1): Sanskrit endings are stripped before lookup so
inflected surface stems (e.g. `nāgāḥ`) are recovered to their root
(`nāga`) and successfully attested.

Fail-closed design:
  - If `_lexicon` cannot be imported, backend refuses to start
  - If `canon.db` is missing, Tier 2 is skipped (with a warning)
  - Any exception during lookup = UNATTESTED (fail-closed)
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

# Try to import the supplement (optional — loader in _lexicon.py may already do this)
try:
    from _lexicon_supplement import SUPPLEMENT_STEMS
    _SUPPLEMENT_OK = True
except Exception:
    SUPPLEMENT_STEMS = {}
    _SUPPLEMENT_OK = False

from backend.engine.pydantic_models import (
    KernelEnvelope,
    RejectedCandidate,
    Candidate,
)

logger = logging.getLogger(__name__)

CANON_DB_PATH = Path("C:/aigaane-master/frontend/public/sqlite/canon.db")


# Endings to strip, ordered from most specific to least specific.
# This is a pragmatic heuristic: for a bare stem lookup to succeed,
# we walk down this list until we find an attested form.
_ENDINGS_TO_STRIP = [
    # IAST endings (with diacritics)
    "āḥ", "aḥ", "āṇi", "āni",
    "āya", "āt", "asya",
    "oḥ", "au", "īḥ", "ūḥ",
    "ā", "ī", "ū", "ḥ", "m",
    # SLP1 endings (engine may return stems in SLP1)
    "aH", "AH", "iH", "IH", "uH", "UH",
    "aM", "AM",
    "H", "M",
]


def _candidate_forms(stem: str):
    """
    Yield candidate bare-stem forms for a possibly-inflected stem.
    Yields the original first, then progressively shorter forms.
    """
    seen = set()
    if stem and stem not in seen:
        seen.add(stem)
        yield stem

    for ending in _ENDINGS_TO_STRIP:
        if stem.endswith(ending) and len(stem) > len(ending) + 1:
            base = stem[: -len(ending)]

            # Try the stripped base directly
            if base not in seen:
                seen.add(base)
                yield base

            # Try base + 'a' (most common masc stem termination)
            with_a = base + "a"
            if with_a not in seen:
                seen.add(with_a)
                yield with_a

            # Try base + 'ā' (feminine stem termination)
            with_aa = base + "ā"
            if with_aa not in seen:
                seen.add(with_aa)
                yield with_aa


class CegarGatekeeper:
    def __init__(self):
        if not _LEXICON_OK or not hasattr(legacy_lexicon, "lookup"):
            raise RuntimeError(
                "FATAL: CegarGatekeeper cannot boot. "
                "_lexicon.lookup is unavailable. "
                "Fail-closed design requires the primary attestation source."
            )
        self.lookup_fn = legacy_lexicon.lookup

        # Tier 1b: supplement (also injected into _lexicon.py by its loader,
        # but we hold a direct reference here as a backup)
        self.supplement_stems = SUPPLEMENT_STEMS if isinstance(SUPPLEMENT_STEMS, dict) else {}

        # Tier 2: canon.db (optional, does not fail-closed on absence)
        if CANON_DB_PATH.exists():
            try:
                conn = sqlite3.connect(str(CANON_DB_PATH))
                conn.execute("SELECT 1 FROM verses_fts LIMIT 1").fetchone()
                conn.close()
                self.canon_db = str(CANON_DB_PATH)
                logger.info(
                    f"Gatekeeper online — Tier 1 (_lexicon, {len(self.supplement_stems)} supplement) "
                    f"+ Tier 2 ({CANON_DB_PATH.name})"
                )
            except Exception as e:
                logger.warning(f"canon.db present but unusable: {e}. Running with Tier 1 only.")
                self.canon_db = None
        else:
            logger.warning(f"canon.db not found at {CANON_DB_PATH}. Running with Tier 1 only.")
            self.canon_db = None

    # ---------------------------------------------------------------- #
    #   Tier 1: Engine lexicon (with ending stripping)                  #
    # ---------------------------------------------------------------- #
    def _attest_lexicon(self, stem: str) -> bool:
        """
        Try the stem as-is, then progressively strip Sanskrit endings.
        Recovers inflected forms like `nāgāḥ` -> `nāga`.
        """
        for cand in _candidate_forms(stem):
            try:
                if self.lookup_fn(cand) is not None:
                    if cand != stem:
                        logger.info(f"Stem '{stem}' attested as '{cand}' (Tier 1a)")
                    return True
            except Exception as e:
                logger.warning(f"_lexicon.lookup('{cand}') raised: {e}")

            # Also try supplement (Tier 1b)
            if cand in self.supplement_stems:
                if cand != stem:
                    logger.info(f"Stem '{stem}' attested as '{cand}' (Tier 1b supplement)")
                return True

        return False

    # ---------------------------------------------------------------- #
    #   Tier 2: canon.db FTS5                                           #
    # ---------------------------------------------------------------- #
    def _attest_canon(self, stem: str) -> bool:
        if not self.canon_db:
            return False
        try:
            term = stem.lower().strip()
            if not term:
                return False
            query = f"{term}*"
            conn = sqlite3.connect(self.canon_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM verses_fts WHERE verses_fts MATCH ? LIMIT 1",
                (query,),
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

        if self._attest_lexicon(stem):
            return True

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
                    f"stem '{bad_stem}' not attested"
                )

        kept.sort(key=lambda c: c.score, reverse=True)
        for idx, cand in enumerate(kept):
            cand.candidate_id = f"cand_{idx + 1:02d}"

        envelope.candidates = kept
        envelope.rejected = rejected

        return envelope