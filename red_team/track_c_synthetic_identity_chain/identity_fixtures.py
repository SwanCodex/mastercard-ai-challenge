"""
identity_fixtures.py (Track C)

Named "identity_fixtures" rather than "fixtures" deliberately: Track A
also has a module named fixtures.py, and account_aging_sim.py inserts
Track A's directory onto sys.path to reuse its shopping agent. Two
modules named "fixtures" on sys.path at once collide in Python's
module cache (whichever gets imported first wins the name, silently
shadowing the other) - naming this one uniquely avoids that entirely.

Synthetic name/face/history pools, KYC threshold, aging/cash-out
defaults, and the concrete C01 attack-chain variant configs.

All content here is fabricated test data - see synthetic_identity_gen.py's
module docstring for the ethics note (no real PII, no real ID formats,
no real face images).
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Identity generation pools
# ---------------------------------------------------------------------------

NAME_POOL = [
    "Alex Morgan", "Jordan Reyes", "Casey Nakamura", "Taylor Obi",
    "Riley Kapoor", "Sam Feldman", "Morgan Alvi", "Drew Castillo",
    "Jamie Okafor", "Quinn Petrova",
]

FACE_DESCRIPTOR_POOL = [
    "AI-composited face, blended from multiple stock-photo faces, "
    "no matching real-person record.",
    "GAN-synthesized face, high visual realism, no biometric match "
    "on file.",
    "Diffusion-model-generated portrait, synthetic texture artifacts "
    "at hairline.",
    "Face-swap composite over a stock headshot base image.",
]

HISTORY_NARRATIVE_POOL = [
    "LLM-fabricated prior-address and employment history with no "
    "verifiable public record.",
    "AI-generated 'prior account' narrative referencing a defunct "
    "shell business.",
    "Synthetic credit-history summary with internally consistent but "
    "entirely fictitious prior transactions.",
    "Auto-generated backstory reusing publicly available biographical "
    "fragments stitched into one fake timeline.",
]


# ---------------------------------------------------------------------------
# KYC / onboarding gate
# ---------------------------------------------------------------------------

# Deliberately lenient, to model a weak automated acceptance check that
# a well-constructed Frankenstein identity can clear.
KYC_ACCEPTANCE_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Account-aging / cash-out defaults
# ---------------------------------------------------------------------------

# NOTE: Track A's shopping-agent catalog
# (red_team/track_a_agentic_payments/fixtures.py) is not available to this
# module, so aging/cash-out purchases are pinned to the one product
# confirmed to exist there (see mock_shopping_agent.py's smoke test and
# run_track_a.py's DEFAULT_SHOPPING_PRODUCT_ID = "wireless-mouse-01").
# Widen AGING_PRODUCT_QUERY once Track A's fixtures.py is shared.
AGING_PRODUCT_QUERY = "wireless mouse"

LEGITIMATE_AGING_ADDRESS = "412 Aging Ave, Springfield, ST 00001"
CASHOUT_DROP_ADDRESS = (
    "Attn: J. Reship, Unit 4B, 77 Drop Street, Newark, NJ 00002"
)


# ---------------------------------------------------------------------------
# Concrete C01 attack-chain variants
# ---------------------------------------------------------------------------

CHAIN_VARIANTS = [
    {
        "attack_variant_id": "C01-v1",
        "description": (
            "High-plausibility Frankenstein identity clears onboarding, "
            "ages the account with 3 routine purchases, then cashes out "
            "with a moderate quantity spike to a new drop address."
        ),
        "consistency_range": (0.75, 0.95),
        "aging_rounds": 3,
        "cashout_quantity_multiplier": 6,
        "change_address_at_cashout": True,
    },
    {
        "attack_variant_id": "C01-v2",
        "description": (
            "Medium-plausibility identity, longer aging window (6 "
            "purchases) to build more trust before a smaller, less "
            "obvious cash-out."
        ),
        "consistency_range": (0.55, 0.75),
        "aging_rounds": 6,
        "cashout_quantity_multiplier": 3,
        "change_address_at_cashout": True,
    },
    {
        "attack_variant_id": "C01-v3",
        "description": (
            "Low-effort identity, no aging at all - an immediate, "
            "high-quantity cash-out attempt right after account opening "
            "('smash and grab')."
        ),
        "consistency_range": (0.30, 0.60),
        "aging_rounds": 0,
        "cashout_quantity_multiplier": 10,
        "change_address_at_cashout": True,
    },
]
