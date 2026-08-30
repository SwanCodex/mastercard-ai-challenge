from dataclasses import dataclass

from shared.schemas.attack_event import AttackEvent
from shared.schemas.verdict import Verdict


@dataclass
class CampaignMetrics:
    total_events: int
    attacks: int
    benign_events: int

    caught_attacks: int
    missed_attacks: int

    false_positives: int
    true_negatives: int

    attack_catch_rate: float
    precision: float
    recall: float
    false_positive_rate: float

    average_latency_ms: float


def compute_metrics(
    attack_events: list[AttackEvent],
    verdicts: list[Verdict],
) -> CampaignMetrics:
    """Compute campaign-level security and performance metrics."""

    verdict_by_event_id = {
        verdict.event_id: verdict
        for verdict in verdicts
    }

    matched_events = [
        event
        for event in attack_events
        if event.event_id in verdict_by_event_id
    ]

    attacks = [
        event
        for event in matched_events
        if event.attack_succeeded_against_agent
    ]

    benign_events = [
        event
        for event in matched_events
        if not event.attack_succeeded_against_agent
    ]

    caught_attacks = sum(
        verdict_by_event_id[event.event_id].attack_caught
        for event in attacks
    )

    missed_attacks = len(attacks) - caught_attacks

    false_positives = sum(
        verdict_by_event_id[event.event_id].attack_caught
        for event in benign_events
    )

    true_negatives = len(benign_events) - false_positives

    total_predicted_positive = caught_attacks + false_positives

    attack_catch_rate = (
        caught_attacks / len(attacks)
        if attacks
        else 0.0
    )

    precision = (
        caught_attacks / total_predicted_positive
        if total_predicted_positive
        else 0.0
    )

    recall = attack_catch_rate

    false_positive_rate = (
        false_positives / len(benign_events)
        if benign_events
        else 0.0
    )

    average_latency_ms = (
        sum(
            verdict_by_event_id[event.event_id].latency_ms
            for event in matched_events
        )
        / len(matched_events)
        if matched_events
        else 0.0
    )

    return CampaignMetrics(
        total_events=len(matched_events),
        attacks=len(attacks),
        benign_events=len(benign_events),
        caught_attacks=caught_attacks,
        missed_attacks=missed_attacks,
        false_positives=false_positives,
        true_negatives=true_negatives,
        attack_catch_rate=attack_catch_rate,
        precision=precision,
        recall=recall,
        false_positive_rate=false_positive_rate,
        average_latency_ms=average_latency_ms,
    )