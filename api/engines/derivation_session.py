from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class DerivationSessionStep:
    step_id: str
    engine: str
    operation: str
    input_state: Dict[str, Any]
    output_state: Dict[str, Any]
    parent_step_id: Optional[str] = None
    derivation_path: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DerivationSession:
    session_id: str
    created_at: str
    input_text: str
    steps: List[DerivationSessionStep] = field(default_factory=list)
    ambiguity_branches: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        input_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "DerivationSession":
        return cls(
            session_id=str(uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            input_text=input_text,
            metadata=metadata or {},
        )

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "DerivationSession":
        if not isinstance(payload, dict):
            raise ValueError("Derivation session payload must be a dict.")

        required_fields = ["session_id", "created_at", "input_text"]
        missing_fields = [field_name for field_name in required_fields if field_name not in payload]
        if missing_fields:
            raise ValueError(f"Malformed derivation session payload; missing {', '.join(missing_fields)}.")

        raw_steps = payload.get("steps", [])
        if not isinstance(raw_steps, list):
            raise ValueError("Malformed derivation session payload; steps must be a list.")

        steps: List[DerivationSessionStep] = []
        for raw_step in raw_steps:
            if not isinstance(raw_step, dict):
                raise ValueError("Malformed derivation session payload; each step must be a dict.")
            steps.append(
                DerivationSessionStep(
                    step_id=raw_step["step_id"],
                    engine=raw_step["engine"],
                    operation=raw_step["operation"],
                    input_state=raw_step["input_state"],
                    output_state=raw_step["output_state"],
                    parent_step_id=raw_step.get("parent_step_id"),
                    derivation_path=raw_step.get("derivation_path") or [],
                    metadata=raw_step.get("metadata") or {},
                )
            )

        ambiguity_branches = payload.get("ambiguity_branches", [])
        if not isinstance(ambiguity_branches, list):
            raise ValueError("Malformed derivation session payload; ambiguity_branches must be a list.")

        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("Malformed derivation session payload; metadata must be a dict.")

        return cls(
            session_id=payload["session_id"],
            created_at=payload["created_at"],
            input_text=payload["input_text"],
            steps=steps,
            ambiguity_branches=ambiguity_branches,
            metadata=metadata,
        )

    def add_step(
        self,
        engine: str,
        operation: str,
        input_state: Dict[str, Any],
        output_state: Dict[str, Any],
        parent_step_id: Optional[str] = None,
        derivation_path: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DerivationSessionStep:
        if parent_step_id is not None and self.get_step(parent_step_id) is None:
            raise ValueError(f"Unknown parent_step_id: {parent_step_id}")

        step = DerivationSessionStep(
            step_id=f"s_{len(self.steps) + 1:04d}",
            engine=engine,
            operation=operation,
            input_state=input_state,
            output_state=output_state,
            parent_step_id=parent_step_id,
            derivation_path=derivation_path or [],
            metadata=metadata or {},
        )
        self.steps.append(step)
        return step

    def add_ambiguity_branch(self, branch_payload: Dict[str, Any]) -> None:
        if not isinstance(branch_payload, dict):
            raise TypeError("ambiguity branch payload must be a dict")
        self.ambiguity_branches.append(branch_payload)

    def get_step(self, step_id: str) -> Optional[DerivationSessionStep]:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "input_text": self.input_text,
            "steps": [step.to_dict() for step in self.steps],
            "ambiguity_branches": self.ambiguity_branches,
            "metadata": self.metadata,
            "total_steps": len(self.steps),
            "total_ambiguity_branches": len(self.ambiguity_branches),
        }
