from datetime import datetime, timezone

from orchestrator.defense_interface import DefensePipeline
from orchestrator.event_log.store import EventStore
from shared.schemas.attack_event import AttackEvent
from orchestrator.campaign_manager import CampaignManager
from shared.schemas.verdict import LayerScore, Verdict


def make_attack_event() -> AttackEvent:
    return AttackEvent(
        event_id="event-001",
        timestamp=datetime.now(timezone.utc),
        track="track_a_agentic",
        user_instruction="Buy the product for ₹1000",
        campaign_id="campaign-001",
        round_number=1,
        attack_variant_id="attack-001",
        attack_succeeded_against_agent=True,
    )


class FakeDefensePipeline(DefensePipeline):
    def evaluate(self, event: AttackEvent) -> Verdict:
        return Verdict(
            event_id=event.event_id,
            timestamp=datetime.now(timezone.utc),
            layer_scores=[
                LayerScore(
                    layer_name="layer1_fast_filters",
                    score=0.9,
                    flagged=True,
                    reason="Test detection",
                )
            ],
            fusion_score=0.9,
            decision="decline",
            attack_caught=True,
            explanation="Test defense pipeline detected the attack.",
            latency_ms=1.0,
        )


def test_process_attack(tmp_path):
    store = EventStore(tmp_path / "events.jsonl")
    fake_defense = FakeDefensePipeline()
    manager = CampaignManager(FakeDefensePipeline(), store)

    attack = make_attack_event()

    verdict = manager.process_attack(attack)

    assert verdict.event_id == attack.event_id
    assert verdict.attack_caught is True

    assert len(store.get_attack_events()) == 1
    assert len(store.get_verdicts()) == 1


def test_run_campaign(tmp_path):
    store = EventStore(tmp_path / "events.jsonl")
    manager = CampaignManager(FakeDefensePipeline(), store)

    attacks = [
        make_attack_event(),
        make_attack_event().model_copy(
            update={"event_id": "event-002", "attack_variant_id": "attack-002"}
        ),
    ]

    verdicts = manager.run_campaign(attacks)

    assert len(verdicts) == 2
    assert len(store.get_attack_events()) == 2
    assert len(store.get_verdicts()) == 2

def test_run_campaign_from_file(tmp_path):
    event_log = tmp_path / "attack_events.jsonl"

    attack = make_attack_event()

    event_log.write_text(
        attack.model_dump_json() + "\n",
        encoding="utf-8",
    )

    store = EventStore(tmp_path / "events.jsonl")
    manager = CampaignManager(FakeDefensePipeline(), store)

    verdicts = manager.run_campaign_from_file(str(event_log))

    assert len(verdicts) == 1
    assert verdicts[0].event_id == attack.event_id

    assert len(store.get_attack_events()) == 1
    assert len(store.get_verdicts()) == 1