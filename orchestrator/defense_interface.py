from abc import ABC, abstractmethod

from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict


class DefensePipeline(ABC):
    """Interface that every SENTINEL defense pipeline must implement."""

    @abstractmethod
    def evaluate(self, event: AttackEvent) -> Verdict:
        """Evaluate an attack event and return a verdict."""
        raise NotImplementedError