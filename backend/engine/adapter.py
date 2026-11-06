import sys
from pathlib import Path
import logging

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

try:
    import legacy_engine
    _LEGACY_OK = True
except Exception as _e:
    legacy_engine = None
    _LEGACY_OK = False
    logging.warning(f"Legacy engine not loaded: {_e}")

from backend.engine.pydantic_models import (
    KernelEnvelope, Candidate, RejectedCandidate,
    OrthographicTriad, Authority, ParseToken
)

logger = logging.getLogger(__name__)

class EngineAdapter:
    def __init__(self):
        self.version = "1.0.8-adapter"

    def _triad(self, legacy: dict, fallback_input: str) -> OrthographicTriad:
        tl = legacy.get("transliteration") or {}
        
        # Fallback SLP1 -> IAST map for basic display
        iast_fallback = fallback_input.replace("H", "ḥ").replace("M", "ṃ").replace("A", "ā").replace("I", "ī").replace("U", "ū").replace("R", "ṭ").replace("S", "ṣ")
        
        deva = tl.get("devanagari") or iast_fallback
        iast = tl.get("iast") or iast_fallback
        slp1 = legacy.get("surface") or fallback_input
        return OrthographicTriad(slp1=slp1, devanagari=deva, iast=iast)

    def parse(self, slp1_input: str) -> KernelEnvelope:
        if not _LEGACY_OK or not hasattr(legacy_engine, "parse"):
            return KernelEnvelope(
                input_triad=OrthographicTriad(slp1=slp1_input, devanagari=slp1_input, iast=slp1_input),
                candidates=[], rejected=[], engine_version=self.version + "-no-legacy"
            )

        try:
            legacy = legacy_engine.parse(slp1_input)
        except Exception as e:
            logger.error(f"Legacy parse failed on {slp1_input}: {e}")
            return KernelEnvelope(
                input_triad=OrthographicTriad(slp1=slp1_input, devanagari=slp1_input, iast=slp1_input),
                candidates=[], rejected=[], engine_version=self.version + "-error"
            )

        if legacy is None:
            return KernelEnvelope(
                input_triad=OrthographicTriad(slp1=slp1_input, devanagari=slp1_input, iast=slp1_input),
                candidates=[],
                rejected=[RejectedCandidate(
                    parse=[ParseToken(surface=slp1_input, stem="UNKNOWN", role="unknown")],
                    reason_code="UNATTESTED_STEM"
                )],
                engine_version=self.version
            )

        triad = self._triad(legacy, slp1_input)
        candidates = []
        
        primary = self._adapt_primary(legacy)
        if primary is not None:
            candidates.append(primary)

        for amb in legacy.get("ambiguous_parses") or []:
            adapted = self._adapt_ambiguous(amb, rank=len(candidates) + 1)
            if adapted is not None:
                candidates.append(adapted)

        rejected = []
        if not candidates:
            rejected.append(RejectedCandidate(
                parse=[ParseToken(surface=slp1_input, stem="UNPARSED", role="unknown")],
                reason_code="UNATTESTED_STEM"
            ))

        candidates.sort(key=lambda c: c.score, reverse=True)
        for idx, cand in enumerate(candidates):
            cand.candidate_id = f"cand_{idx + 1:02d}"

        return KernelEnvelope(
            input_triad=triad,
            candidates=candidates,
            rejected=rejected,
            engine_version=self.version
        )

    def _adapt_primary(self, legacy: dict) -> Candidate | None:
        tokens = legacy.get("tokens") or []
        if not tokens:
            return None

        parse_tokens = []
        for tok in tokens:
            parse_tokens.append(ParseToken(
                surface=tok.get("pada") or tok.get("surface") or "unknown",
                stem=tok.get("stem") or "unknown",
                role=self._role_from_token(tok)
            ))

        samasa_tree = legacy.get("samasa_tree") or {}
        samasa_type = samasa_tree.get("type") if samasa_tree else None
        vigraha = samasa_tree.get("vigraha") if samasa_tree else None
        sutra_chain = self._extract_sutra_chain(legacy, samasa_type)

        provenance = legacy.get("provenance") or []
        engine_ver = next((p.split("=", 1)[1] for p in provenance if p.startswith("engine=")), "unknown")
        
        authority = Authority(
            recension="Kasika_Vrtti",
            primary_source=f"Aṣṭādhyāyī ({engine_ver})",
            authority_notes="; ".join(provenance) or None,
            disputed_alternatives=[]
        )

        score = float(legacy.get("confidence") or 0.0)
        score = max(0.0, min(1.0, score))

        return Candidate(
            candidate_id="cand_01",
            parse=parse_tokens,
            samasa_type=samasa_type,
            vigraha=vigraha,
            sutra_chain=sutra_chain,
            authority=authority,
            score=score
        )

    def _adapt_ambiguous(self, amb: dict, rank: int) -> Candidate | None:
        tokens = amb.get("tokens") or []
        if not tokens:
            return None

        parse_tokens = []
        for tok in tokens:
            parse_tokens.append(ParseToken(
                surface=tok.get("pada") or tok.get("surface") or "unknown",
                stem=tok.get("stem") or "unknown",
                role=self._role_from_token(tok)
            ))

        sutra_chain = ["1.4.14"]
        score = float(amb.get("confidence") or 0.0)
        score = max(0.0, min(1.0, score))
        ambiguity_type = amb.get("ambiguity_type") or "unspecified"

        authority = Authority(
            recension="Kasika_Vrtti",
            primary_source=f"Ambiguous reading ({ambiguity_type})",
            authority_notes=f"ambiguity_type={ambiguity_type}",
            disputed_alternatives=[]
        )

        return Candidate(
            candidate_id=f"cand_{rank + 1:02d}",
            parse=parse_tokens,
            samasa_type=None,
            vigraha=None,
            sutra_chain=sutra_chain,
            authority=authority,
            score=score
        )

    def _role_from_token(self, tok: dict) -> str:
        pos = tok.get("pos")
        vibhakti = tok.get("vibhakti")
        if pos == "subhanta":
            return f"subanta:{vibhakti}" if vibhakti else "subanta"
        if pos == "tinanta":
            return "tinanta"
        return pos or "token"

    def _extract_sutra_chain(self, legacy: dict, samasa_type: str | None) -> list[str]:
        canon_refs = legacy.get("canon_refs") or []
        if canon_refs:
            refs = []
            for ref in canon_refs:
                if isinstance(ref, str):
                    refs.append(ref)
                elif isinstance(ref, dict) and "sutra" in ref:
                    refs.append(str(ref["sutra"]))
            if refs:
                return refs

        samasa_to_sutra = {
            "tatpurusha": ["2.1.22", "2.2.8"],
            "karmadharaya": ["2.1.57"],
            "bahuvrihi": ["2.2.24"],
            "dvandva": ["2.2.29"],
            "avyayibhava": ["2.1.5"],
            "dvigu": ["2.1.52"],
        }
        if samasa_type and samasa_type in samasa_to_sutra:
            return samasa_to_sutra[samasa_type]
            
        return ["2.1.1"]