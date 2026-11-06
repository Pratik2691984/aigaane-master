from backend.engine.pydantic_models import KernelEnvelope

class CegarGatekeeper:
    """
    Deterministic verifier. Currently a structural pass-through.
    Later: wire to kosha_1.5m.db FTS5 for real stem attestation.
    """
    def __init__(self):
        self.valid_stems = None  # None = accept all (stub mode)

    def validate_llm_output(self, llm_proposal: dict) -> dict:
        if self.valid_stems is None:
            return {"passed": True, "reason": "Gatekeeper in stub mode (no Kosha wired)"}
        proposed_split = llm_proposal.get("split", [])
        for stem in proposed_split:
            if stem not in self.valid_stems:
                return {"passed": False, "reason": f"Hallucination: '{stem}' not in Kosha.", "action": "REJECT_422"}
        return {"passed": True, "reason": "Structurally Valid"}