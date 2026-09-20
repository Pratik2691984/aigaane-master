from dataclasses import asdict, dataclass
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class DerivationStep:
    sutra: str
    sutra_name: str
    operation: str
    input_state: str
    output_state: str
    engine_node: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class DerivationTraceGraph:
    steps: Sequence[DerivationStep]

    def __post_init__(self):
        object.__setattr__(self, "steps", tuple(self.steps))

    def to_list(self) -> List[Dict[str, str]]:
        return [step.to_dict() for step in self.steps]

    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {"derivation_path": self.to_list()}
