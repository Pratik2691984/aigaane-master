from backend.engine.pydantic_models import KernelEnvelope, RejectedCandidate

class CegarGatekeeper:
    def __init__(self):
        # We accept both SLP1 (rAjan) and IAST (rājan) in our stub
        self.valid_stems = {
            # SLP1
            "rAjan", "putra", "rAjaputra", "candra", "mukha", "candramukha",
            "rAma", "rAmasya", "deva", "manuSya", "nAga", "indra",
            # IAST (What the engine actually outputs)
            "rājan", "putra", "rājaputra", "candra", "mukha", "candramukha",
            "rāma", "rāmasya", "deva", "manuṣya", "nāga", "indra"
        }

    def verify(self, envelope: KernelEnvelope) -> KernelEnvelope:
        verified_candidates = []
        rejected = list(envelope.rejected)

        for cand in envelope.candidates:
            is_valid = True
            for token in cand.parse:
                stem = token.stem
                # If it's a real stem (not the "unknown" fallback) and it's not in the Kosha
                if stem not in self.valid_stems and stem != "unknown":
                    is_valid = False
                    rejected.append(RejectedCandidate(
                        parse=cand.parse,
                        reason_code="UNATTESTED_STEM",
                        violated_sutra="1.1.1"
                    ))
                    break
            
            if is_valid:
                verified_candidates.append(cand)

        envelope.candidates = verified_candidates
        envelope.rejected = rejected
        
        # Re-sort and re-assign IDs
        envelope.candidates.sort(key=lambda c: c.score, reverse=True)
        for idx, cand in enumerate(envelope.candidates):
            cand.candidate_id = f"cand_{idx + 1:02d}"
            
        return envelope