from typing import Any, Dict, Iterable, List, Optional, Union

from pydantic import BaseModel


class AmbiguityCandidate(BaseModel):
    candidate_id: str
    final_output: str
    source_engine: str
    confidence: Optional[float] = None
    reason: str
    derivation_path: List[Dict[str, Any]]


class AmbiguityPayload(BaseModel):
    is_ambiguous: bool
    candidates: List[AmbiguityCandidate]
    strategy: str
    selected_candidate_id: Optional[str] = None


CandidateInput = Union[AmbiguityCandidate, Dict[str, Any]]


def make_unambiguous() -> AmbiguityPayload:
    return AmbiguityPayload(
        is_ambiguous=False,
        candidates=[],
        strategy="unambiguous",
    )


def make_ambiguous(
    candidates: Iterable[CandidateInput],
    strategy: str = "enumeration_only",
) -> AmbiguityPayload:
    return AmbiguityPayload(
        is_ambiguous=True,
        candidates=[
            candidate if isinstance(candidate, AmbiguityCandidate) else AmbiguityCandidate(**candidate)
            for candidate in candidates
        ],
        strategy=strategy,
    )
