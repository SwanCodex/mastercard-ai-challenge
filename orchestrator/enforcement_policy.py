from shared.schemas.security_decision import SecurityDecision
from shared.schemas.verdict import Verdict


class EnforcementPolicy:
    """
    Deterministic authority for final security enforcement.

    The Security Agent can recommend an action, but it cannot override
    a stronger deterministic security verdict.
    """

    def evaluate(self, verdict: Verdict) -> SecurityDecision:
        """Create a baseline enforcement decision from the Verdict."""

        action_map = {
            "approve": "allow",
            "step_up": "review",
            "review": "review",
            "decline": "block",
        }

        action = action_map[verdict.decision]

        evidence = [
            f"{layer.layer_name}: {layer.reason}"
            for layer in verdict.layer_scores
            if layer.flagged
        ]

        if not evidence:
            evidence = ["No individual defense layer flagged the event."]

        if verdict.decision == "decline":
            reason = (
                "The defense pipeline produced a decline verdict; "
                "the proposed action is blocked."
            )
            confidence = max(verdict.fusion_score, 0.90)

        elif verdict.decision == "review":
            reason = (
                "The defense pipeline identified elevated risk; "
                "the proposed action requires human review."
            )
            confidence = max(verdict.fusion_score, 0.70)

        elif verdict.decision == "step_up":
            reason = (
                "The defense pipeline identified moderate risk; "
                "additional verification is required before execution."
            )
            confidence = max(verdict.fusion_score, 0.60)

        else:
            reason = (
                "The defense pipeline found no sufficient evidence "
                "to prevent the proposed action."
            )
            confidence = max(1.0 - verdict.fusion_score, 0.50)

        return SecurityDecision(
            event_id=verdict.event_id,
            timestamp=verdict.timestamp,
            action=action,
            confidence=min(confidence, 1.0),
            reason=reason,
            evidence=evidence,
            requires_human_review=action == "review",
            source_verdict_decision=verdict.decision,
            fusion_score=verdict.fusion_score,
        )

    def apply(
        self,
        verdict: Verdict,
        agent_decision: SecurityDecision,
    ) -> SecurityDecision:
        """
        Reconcile the Security Agent recommendation with the deterministic
        Verdict. The policy always has final authority.
        """

        baseline = self.evaluate(verdict)

        # A deterministic BLOCK can never be weakened by the agent.
        if baseline.action == "block":
            return SecurityDecision(
                event_id=baseline.event_id,
                timestamp=baseline.timestamp,
                action="block",
                confidence=max(
                    baseline.confidence,
                    agent_decision.confidence,
                ),
                reason=(
                    f"{baseline.reason} "
                    f"Security Agent assessment: {agent_decision.reason}"
                ),
                evidence=baseline.evidence + agent_decision.evidence,
                requires_human_review=False,
                source_verdict_decision=baseline.source_verdict_decision,
                fusion_score=baseline.fusion_score,
            )

        # If the deterministic system requires review, the agent
        # cannot downgrade it to ALLOW.
        if baseline.action == "review":
            return SecurityDecision(
                event_id=baseline.event_id,
                timestamp=baseline.timestamp,
                action="review",
                confidence=max(
                    baseline.confidence,
                    agent_decision.confidence,
                ),
                reason=(
                    f"{baseline.reason} "
                    f"Security Agent assessment: {agent_decision.reason}"
                ),
                evidence=baseline.evidence + agent_decision.evidence,
                requires_human_review=True,
                source_verdict_decision=baseline.source_verdict_decision,
                fusion_score=baseline.fusion_score,
            )

        # If the detection system says ALLOW but the security agent
        # identifies a concern, escalate rather than silently allowing.
        if agent_decision.action in {"review", "block"}:
            return SecurityDecision(
                event_id=baseline.event_id,
                timestamp=baseline.timestamp,
                action=agent_decision.action,
                confidence=agent_decision.confidence,
                reason=agent_decision.reason,
                evidence=agent_decision.evidence,
                requires_human_review=agent_decision.action == "review",
                source_verdict_decision=baseline.source_verdict_decision,
                fusion_score=baseline.fusion_score,
            )

        return baseline
