"""
agent/quanta_ledger.py
Budget enforcement for Track A agentic RAG.

Billing model:
  - 25 Q fixed for vector retrieval (debited once per request)
  - 1 Q per generated akṣara (syllable)
  - 300 Q default ceiling per request

Fail-closed: any debit that would exceed the ceiling raises QuantaExceeded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class QuantaExceeded(Exception):
    """Raised when a debit would exceed the ledger ceiling."""


@dataclass
class QuantaLedger:
    """
    Tracks Quanta spend against a ceiling for a single request.

    Usage:
        ledger = QuantaLedger(ceiling=300)
        ledger.debit_retrieval()         # 25 Q
        ledger.debit_aksaras(32)         # 32 Q
        print(ledger.remaining)          # 243
    """

    ceiling: int = 300
    retrieval_cost: int = 25
    spent: int = field(default=0, init=False)
    log: list[tuple[str, int]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if self.ceiling < 0:
            raise ValueError("ceiling must be >= 0")
        if self.retrieval_cost < 0:
            raise ValueError("retrieval_cost must be >= 0")
        if self.ceiling < self.retrieval_cost:
            raise ValueError(
                f"ceiling ({self.ceiling}) must be >= "
                f"retrieval_cost ({self.retrieval_cost})"
            )

    @property
    def remaining(self) -> int:
        """Quanta remaining before the ceiling is hit."""
        return max(0, self.ceiling - self.spent)

    def debit(self, label: str, amount: int) -> None:
        """Debit `amount` Quanta under `label`."""
        if amount < 0:
            raise ValueError("amount must be >= 0")
        if self.spent + amount > self.ceiling:
            raise QuantaExceeded(
                f"Would exceed {self.ceiling} Q "
                f"(spent: {self.spent}, attempted: {amount})"
            )
        self.spent += amount
        self.log.append((label, amount))

    def debit_retrieval(self) -> None:
        """Charge the fixed retrieval fee."""
        self.debit("retrieval", self.retrieval_cost)

    def debit_aksaras(self, count: int) -> None:
        """Charge 1 Q per akṣara (syllable)."""
        self.debit("aksaras", count)

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-serializable snapshot of current state."""
        return {
            "ceiling": self.ceiling,
            "retrieval_cost": self.retrieval_cost,
            "spent": self.spent,
            "remaining": self.remaining,
            "log": [{"label": lbl, "amount": amt} for lbl, amt in self.log],
        }

    def __repr__(self) -> str:
        return (
            f"QuantaLedger(ceiling={self.ceiling}, "
            f"spent={self.spent}, remaining={self.remaining})"
        )


if __name__ == "__main__":
    ledger = QuantaLedger(ceiling=300)
    assert ledger.remaining == 300

    ledger.debit_retrieval()
    assert ledger.spent == 25
    assert ledger.remaining == 275

    ledger.debit_aksaras(32)
    assert ledger.spent == 57
    assert ledger.remaining == 243

    try:
        ledger.debit_aksaras(1000)
        raise AssertionError("Expected QuantaExceeded")
    except QuantaExceeded:
        pass

    try:
        ledger.debit("bad", -1)
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass

    import json
    snap = ledger.snapshot()
    json.dumps(snap)
    assert snap["spent"] == 57
    assert snap["remaining"] == 243

    print("quanta_ledger.py OK")