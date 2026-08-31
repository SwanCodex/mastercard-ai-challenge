import json
from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel

from shared.schemas.attack_event import AttackEvent
from shared.schemas.security_decision import SecurityDecision
from shared.schemas.verdict import Verdict


T = TypeVar("T", bound=BaseModel)


class EventStore:
    """JSONL-based storage for SENTINEL security records."""

    def __init__(self, log_path: str | Path = "orchestrator/event_log/events.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _append(self, record_type: str, record: BaseModel) -> None:
        entry = {
            "record_type": record_type,
            "data": record.model_dump(mode="json"),
        }

        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry) + "\n")

    def append_attack_event(self, event: AttackEvent) -> None:
        self._append("attack_event", event)

    def append_verdict(self, verdict: Verdict) -> None:
        self._append("verdict", verdict)

    def append_security_decision(self, decision: SecurityDecision) -> None:
        self._append("security_decision", decision)

    def _read_records(self) -> list[dict]:
        if not self.log_path.exists():
            return []

        records = []

        with self.log_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    records.append(json.loads(line))

        return records

    def get_attack_events(self) -> list[AttackEvent]:
        return [
            AttackEvent.model_validate(record["data"])
            for record in self._read_records()
            if record["record_type"] == "attack_event"
        ]

    def get_verdicts(self) -> list[Verdict]:
        return [
            Verdict.model_validate(record["data"])
            for record in self._read_records()
            if record["record_type"] == "verdict"
        ]

    def get_security_decisions(self) -> list[SecurityDecision]:
        return [
            SecurityDecision.model_validate(record["data"])
            for record in self._read_records()
            if record["record_type"] == "security_decision"
        ]

    def get_campaign_records(self, campaign_id: str) -> dict[str, list[BaseModel]]:
        attacks = [
            event
            for event in self.get_attack_events()
            if event.campaign_id == campaign_id
        ]

        event_ids = {event.event_id for event in attacks}

        verdicts = [
            verdict
            for verdict in self.get_verdicts()
            if verdict.event_id in event_ids
        ]

        security_decisions = [
            decision
            for decision in self.get_security_decisions()
            if decision.event_id in event_ids
        ]

        return {
            "attack_events": attacks,
            "verdicts": verdicts,
            "security_decisions": security_decisions,
        }
