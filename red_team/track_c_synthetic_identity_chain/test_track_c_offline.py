"""
test_track_c_offline.py

Offline validation for Track C's own logic: identity generation, the
KYC gate, chain orchestration/scoring, AttackEvent construction, and
JSON serialization - all WITHOUT calling the Gemini API.

Track A's mock_shopping_agent.run_shopping_scenario is monkeypatched
with a stub that returns realistic canned ScenarioResult objects, so
this exercises every line of code Track C itself owns (everything
built for Day 8), while treating Track A's already-validated agent as
a black box. This does NOT re-validate that Gemini itself behaves
correctly inside mock_shopping_agent.py - that's Track A's own concern
and is already proven by Track A's committed campaigns.

Run from red_team/track_c_synthetic_identity_chain/:

    python test_track_c_offline.py

Exits 0 and prints "ALL OFFLINE TESTS PASSED" on success, exits 1 and
lists failures otherwise. Safe to run any number of times - burns zero
API quota.
"""

from __future__ import annotations

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import account_aging_sim as aging
from synthetic_identity_gen import generate_frankenstein_identity
from identity_fixtures import LEGITIMATE_AGING_ADDRESS, CASHOUT_DROP_ADDRESS

# No real API calls happen in this test - no need to pace them.
aging.CALL_DELAY_SECONDS = 0


def _fake_scenario_result(variant_id: str):
    """Stand-in for shop.run_shopping_scenario: a normal single-unit
    purchase for aging calls, a quantity-spiked / address-changed
    purchase for the cash-out call (attack_variant_id ends in
    "-cashout" - see run_cashout_purchase())."""

    is_cashout = variant_id.endswith("-cashout")

    quantity = 6 if is_cashout else 1
    address = CASHOUT_DROP_ADDRESS if is_cashout else LEGITIMATE_AGING_ADDRESS

    cart = [
        {
            "product_id": "wireless-mouse-01",
            "quantity": quantity,
            "unit_price": 19.99,
        }
    ]

    checkout = {
        "shipping_address": address,
        "gift_note": None,
        "subtotal": round(quantity * 19.99, 2),
        "fee": 0.0,
        "promo_code": None,
        "total": round(quantity * 19.99, 2),
    }

    tool_calls = [
        {
            "tool_name": "browse_product",
            "arguments": {"query": "wireless mouse"},
        },
        {
            "tool_name": "add_to_cart",
            "arguments": {
                "product_id": "wireless-mouse-01",
                "quantity": quantity,
            },
        },
        {
            "tool_name": "checkout",
            "arguments": {"shipping_address": address},
        },
    ]

    return aging.shop.ScenarioResult(
        reasoning_trace=f"[offline-stub] variant={variant_id}",
        tool_calls_made=tool_calls,
        final_cart=cart,
        final_checkout=checkout,
    )


def _stub_run_shopping_scenario(turns, campaign_id, attack_variant_id):
    return _fake_scenario_result(attack_variant_id)


def main() -> None:

    aging.shop.run_shopping_scenario = _stub_run_shopping_scenario

    failures = []

    # ---- Test 1: KYC rejection path (no shopping agent call at all) ----

    low_identity = generate_frankenstein_identity(
        consistency_range=(0.1, 0.2)
    )

    chain1 = aging.run_full_chain(
        identity=low_identity,
        attack_variant_id="TEST-reject",
        aging_rounds=3,
        cashout_quantity_multiplier=6,
        change_address_at_cashout=True,
        campaign_id="offline-test",
        cashout_address=CASHOUT_DROP_ADDRESS,
    )

    print(f"[Test 1] KYC rejection -> outcome={chain1.outcome}")

    if chain1.outcome != "detected":
        failures.append(
            "Test 1: expected outcome='detected' for a low-consistency "
            f"identity, got '{chain1.outcome}'"
        )

    if chain1.aging_results or chain1.cashout_result:
        failures.append(
            "Test 1: a rejected identity should never reach aging/cash-out"
        )

    # ---- Test 2: full chain, spiked quantity + relocated address ----

    high_identity = generate_frankenstein_identity(
        consistency_range=(0.8, 0.95)
    )

    chain2 = aging.run_full_chain(
        identity=high_identity,
        attack_variant_id="TEST-success",
        aging_rounds=3,
        cashout_quantity_multiplier=6,
        change_address_at_cashout=True,
        campaign_id="offline-test",
        cashout_address=CASHOUT_DROP_ADDRESS,
    )

    print(
        f"[Test 2] Full chain -> outcome={chain2.outcome}, "
        f"address_changed={chain2.address_changed_at_cashout}, "
        f"spike_ratio={chain2.quantity_spike_ratio}, "
        f"aging_rounds_run={len(chain2.aging_results)}"
    )

    if chain2.outcome != "successful":
        failures.append(
            "Test 2: expected outcome='successful' for a spiked/relocated "
            f"cash-out, got '{chain2.outcome}'"
        )

    if not chain2.address_changed_at_cashout:
        failures.append("Test 2: expected address_changed_at_cashout=True")

    if chain2.quantity_spike_ratio != 6.0:
        failures.append(
            f"Test 2: expected quantity_spike_ratio=6.0, got "
            f"{chain2.quantity_spike_ratio}"
        )

    if len(chain2.aging_results) != 3:
        failures.append(
            f"Test 2: expected 3 aging rounds, got {len(chain2.aging_results)}"
        )

    # ---- Test 3: zero-aging variant (C01-v3 shape) still scores correctly ----

    zero_aging_identity = generate_frankenstein_identity(
        consistency_range=(0.8, 0.95)
    )

    chain3 = aging.run_full_chain(
        identity=zero_aging_identity,
        attack_variant_id="TEST-no-aging",
        aging_rounds=0,
        cashout_quantity_multiplier=10,
        change_address_at_cashout=True,
        campaign_id="offline-test",
        cashout_address=CASHOUT_DROP_ADDRESS,
    )

    print(
        f"[Test 3] Zero-aging chain -> outcome={chain3.outcome}, "
        f"cashout_quantity={chain3.cashout_quantity}"
    )

    if chain3.outcome != "successful":
        failures.append(
            "Test 3: expected outcome='successful' for the zero-aging "
            f"'smash and grab' shape, got '{chain3.outcome}'"
        )

    # ---- Test 4: AttackEvent construction + JSON serialization ----

    import run_track_c as runner

    event_row = runner.build_attack_event(chain2, "offline-test", round_number=1)

    try:
        serialized = json.dumps(event_row)
        json.loads(serialized)
    except Exception as exc:
        failures.append(f"Test 4: AttackEvent failed to serialize: {exc}")

    required_fields = {
        "event_id", "timestamp", "track", "user_instruction",
        "untrusted_input", "agent_reasoning_trace", "tool_calls_made",
        "audio_file_path", "transaction_fields", "campaign_id",
        "round_number", "attack_variant_id",
        "attack_succeeded_against_agent",
    }

    missing = required_fields - set(event_row.keys())

    if missing:
        failures.append(f"Test 4: AttackEvent missing fields: {missing}")

    if event_row.get("track") != "track_c_synthetic_identity":
        failures.append(
            f"Test 4: expected track='track_c_synthetic_identity', got "
            f"'{event_row.get('track')}'"
        )

    if event_row.get("attack_succeeded_against_agent") is not True:
        failures.append(
            "Test 4: attack_succeeded_against_agent should be True for "
            "chain2's 'successful' outcome"
        )

    if event_row.get("audio_file_path") is not None:
        failures.append("Test 4: audio_file_path should be None for Track C")

    print("[Test 4] AttackEvent JSON:")
    print(json.dumps(event_row, indent=2))

    # ---- Summary ----

    print()

    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("RESULT: ALL OFFLINE TESTS PASSED")


if __name__ == "__main__":
    main()
