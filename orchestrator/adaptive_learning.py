import json
import re
from collections import Counter
from pathlib import Path

from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict


class AdaptiveThreatLearner:
    """Learns recurring threat patterns from confirmed attack events."""

    KNOWN_PATTERNS = (
        "ignore previous instructions",
        "ignore all previous instructions",
        "system instruction",
        "override",
        "change shipping address",
        "change payment",
        "redirect payment",
        "unauthorized",
        "bypass verification",
        "skip verification",
    )

    STOP_WORDS = {
        "the", "and", "for", "this", "that", "with", "from",
        "user", "agent", "please", "should", "would", "could",
        "your", "their", "have", "has", "was", "were", "into",
        "then", "than", "when", "where", "what", "will", "must",
        "transaction", "payment", "instruction", "instructions",
    }

    def __init__(
        self,
        knowledge_path="orchestrator/adaptive_learning/threat_knowledge.json",
    ):
        self.knowledge_path = Path(knowledge_path)

    def _extract_patterns(self, text: str) -> set[str]:
        """Extract known patterns plus candidate novel phrases."""

        text_lower = text.lower()
        patterns = {
            pattern
            for pattern in self.KNOWN_PATTERNS
            if pattern in text_lower
        }

        words = re.findall(r"[a-zA-Z0-9]+", text_lower)
        words = [
            word
            for word in words
            if word not in self.STOP_WORDS and len(word) > 2
        ]

        for size in (2, 3, 4, 5):
            for i in range(len(words) - size + 1):
                phrase = " ".join(words[i:i + size])

                if len(phrase) >= 10:
                    patterns.add(phrase)

        return patterns

    def learn(
        self,
        attack_events: list[AttackEvent],
        verdicts: list[Verdict],
    ) -> dict:

        verdict_by_id = {v.event_id: v for v in verdicts}

        confirmed_attacks = [
            event
            for event in attack_events
            if event.attack_succeeded_against_agent
            and event.event_id in verdict_by_id
        ]

        missed_attacks = [
            event
            for event in confirmed_attacks
            if not verdict_by_id[event.event_id].attack_caught
        ]

        patterns = Counter()

        for event in confirmed_attacks:
            text = " ".join(
                filter(
                    None,
                    [
                        event.user_instruction,
                        event.untrusted_input,
                        event.agent_reasoning_trace,
                    ],
                )
            )

            for pattern in self._extract_patterns(text):
                patterns[pattern] += 1

        previous = self.load().get("patterns", {})

        for pattern, count in previous.items():
            patterns[pattern] = max(patterns[pattern], count)

        useful_patterns = {
            pattern: count
            for pattern, count in patterns.items()
            if count >= 2 or pattern in self.KNOWN_PATTERNS
        }

        knowledge = {
            "version": 2,
            "total_confirmed_attacks": len(confirmed_attacks),
            "missed_attacks": len(missed_attacks),
            "patterns": useful_patterns,
        }

        self.knowledge_path.parent.mkdir(parents=True, exist_ok=True)

        self.knowledge_path.write_text(
            json.dumps(knowledge, indent=2),
            encoding="utf-8",
        )

        return knowledge

    def load(self) -> dict:
        if not self.knowledge_path.exists():
            return {
                "version": 2,
                "total_confirmed_attacks": 0,
                "missed_attacks": 0,
                "patterns": {},
            }

        return json.loads(
            self.knowledge_path.read_text(encoding="utf-8")
        )
