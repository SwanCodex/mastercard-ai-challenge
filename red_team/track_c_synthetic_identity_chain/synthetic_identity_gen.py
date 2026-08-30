"""
synthetic_identity_gen.py

Track C - Synthetic Identity + Agentic Onboarding Fraud
Person A (Red Team), per Solution_And_Team_Plan.md Part 6, Day 8.

Generates fully synthetic "Frankenstein identity" profiles for the
account-opening stage of the Track C fraud chain: a fabricated
ID-fragment + a textual description of an AI-composited face + a
fabricated prior-activity narrative, combined into a single profile
with a plausibility ("consistency") score.

ETHICS NOTE (see docs/ethics_and_safety.md):
    - No real PII, no real government-ID numbers, no real biometric
      data, and no actual face-image generation happen here.
    - `synthetic_id_fragment` values use an obviously-fake test-fixture
      format (e.g. "SYN-TEST-XXXXXXXX") - never a realistic SSN/Aadhaar
      pattern.
    - `ai_face_descriptor` is a short text description standing in for
      an AI-composited face, not an actual generated image.
    - Everything produced by this module is synthetic test data for
      red-teaming Track C's account-aging simulation only.
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass
from typing import List, Optional, Tuple

from identity_fixtures import (
    NAME_POOL,
    FACE_DESCRIPTOR_POOL,
    HISTORY_NARRATIVE_POOL,
)


@dataclass
class SyntheticIdentity:
    identity_id: str
    full_name: str
    synthetic_id_fragment: str
    ai_face_descriptor: str
    ai_generated_history_summary: str
    claimed_address: str
    consistency_score: float


def _fake_id_fragment(rng: random.Random) -> str:
    """An obviously-synthetic ID-fragment placeholder, never a
    real-ID format."""

    return f"SYN-TEST-{rng.randint(10_000_000, 99_999_999)}"


def generate_frankenstein_identity(
    consistency_range: Tuple[float, float] = (0.3, 0.95),
    claimed_address: Optional[str] = None,
    seed: Optional[int] = None,
) -> SyntheticIdentity:
    """Generate one synthetic "Frankenstein identity" profile.

    consistency_range:
        The plausibility score is sampled uniformly from this range.
        Callers (see fixtures.CHAIN_VARIANTS) use different ranges to
        produce identities that are more or less likely to clear the
        automated onboarding gate in account_aging_sim.py.
    """

    rng = random.Random(seed)

    name = rng.choice(NAME_POOL)
    face_descriptor = rng.choice(FACE_DESCRIPTOR_POOL)
    history_summary = rng.choice(HISTORY_NARRATIVE_POOL)

    low, high = consistency_range
    consistency_score = round(rng.uniform(low, high), 2)

    return SyntheticIdentity(
        identity_id=str(uuid.uuid4()),
        full_name=name,
        synthetic_id_fragment=_fake_id_fragment(rng),
        ai_face_descriptor=face_descriptor,
        ai_generated_history_summary=history_summary,
        claimed_address=(
            claimed_address or "APPLICANT-SUPPLIED ADDRESS ON FILE"
        ),
        consistency_score=consistency_score,
    )


def generate_identity_batch(
    n: int,
    consistency_range: Tuple[float, float] = (0.3, 0.95),
) -> List[SyntheticIdentity]:

    return [
        generate_frankenstein_identity(
            consistency_range=consistency_range
        )
        for _ in range(n)
    ]


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    identity = generate_frankenstein_identity()

    print("Generated synthetic identity:")
    print(f"  identity_id       : {identity.identity_id}")
    print(f"  full_name         : {identity.full_name}")
    print(f"  id_fragment       : {identity.synthetic_id_fragment}")
    print(f"  face_descriptor   : {identity.ai_face_descriptor}")
    print(f"  history_summary   : {identity.ai_generated_history_summary}")
    print(f"  consistency_score : {identity.consistency_score}")
