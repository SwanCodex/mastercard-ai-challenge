# Track C — Synthetic Identity + Agentic Onboarding Fraud

**Owner:** Person A (Red Team), per `Solution_And_Team_Plan.md` Part 6,
Day 8. Integration track — chains synthetic identity + automated
onboarding + agent-driven account aging into one fraud sequence, per
Part 1.2 of the plan.

## Chain

```
Frankenstein identity  ->  KYC/onboarding gate  ->  N aging purchases  ->  cash-out
(synthetic_identity_gen)   (account_aging_sim)      (mock_shopping_agent,   (same agent,
                                                       Track A, reused        larger qty,
                                                       unmodified)            new address)
```

1. **Identity generation** (`synthetic_identity_gen.py`) — fabricates a
   "Frankenstein identity": a fake ID fragment + a textual description
   standing in for an AI-composited face + a fabricated prior-activity
   narrative, with a random plausibility ("consistency") score.
2. **Onboarding gate** (`account_aging_sim.attempt_account_opening`) —
   deterministic threshold check against `consistency_score`. Not
   LLM-driven by design (see "Design notes" below).

> **Note:** this track's own fixtures live in `identity_fixtures.py`,
> not `fixtures.py` — deliberately, to avoid colliding with Track A's
> `fixtures.py` once `account_aging_sim.py` puts Track A's directory on
> `sys.path` to reuse its shopping agent. Two same-named modules on
> `sys.path` at once shadow each other in Python's import cache.
3. **Account aging** (`account_aging_sim.run_aging_purchase`, x N) —
   reuses Track A's real `mock_shopping_agent.py` unmodified to make a
   sequence of small, routine-looking purchases to the same address.
4. **Cash-out** (`account_aging_sim.run_cashout_purchase`) — one final,
   larger purchase via the same agent, usually to a new "drop" address.

## Attack coverage

One base attack family, three concrete variants (mirrors Track A/B's
variant-generation approach):

| ID | Description | Aging rounds | Cash-out multiplier |
|---|---|---|---|
| C01-v1 | High-plausibility identity, standard aging | 3 | 6x |
| C01-v2 | Medium-plausibility identity, extended aging | 6 | 3x |
| C01-v3 | Low-effort identity, no aging — "smash and grab" | 0 | 10x |

## Design notes (read before extending)

- **No new dependencies.** Reuses `google-genai` + `python-dotenv` from
  the same `.env` Track A/B already use (`GEMINI_API_KEY`,
  `SENTINEL_AGENT_MODEL`). One new optional var:
  `SENTINEL_TRACK_C_CALL_DELAY_SECONDS` (default `3`) — pacing between
  Gemini calls, same free-tier RPM issue Track B hit.
- **Onboarding is a deterministic gate, not Track B's liveness agent.**
  Wiring in the real `synthetic_face_liveness/mock_liveness_agent.py`
  from Track B instead of `attempt_account_opening()` is a clean
  follow-up (swap the KYC-gate call in `run_full_chain()` for a call to
  Track B's `run_liveness_scenario()`, feeding it
  `identity.ai_face_descriptor` as the injected/claimed frame source) —
  not done here to avoid guessing at Track B's exact tool schema.
- **Aging/cash-out purchases are pinned to `"wireless-mouse-01"`**
  (`AGING_PRODUCT_QUERY = "wireless mouse"` in `identity_fixtures.py`) — the one
  product confirmed to exist in Track A's catalog from
  `mock_shopping_agent.py`'s smoke test. Widen the catalog once Track
  A's `fixtures.py` is available.
- Track C does **not** splice injection payloads into any tool output —
  the fraud signal here is the *behavioral pattern* (address change,
  quantity spike after a quiet aging period), not a prompt injection.
  This is intentionally a different attack mechanism from Track A/B, to
  give Blue Team's transaction-integrity / graph layer something
  structurally different to catch, per the plan's "prove it's a system,
  not three disconnected toys" framing.

## Scoring

| Outcome | Meaning |
|---|---|
| `detected` | KYC gate rejected the identity — fraud stopped at onboarding |
| `ignored` | Identity opened but no cash-out transaction ever completed |
| `partially_executed` | Full chain completed, no deviation from the aging pattern |
| `successful` | Full chain completed **with** deviation (address changed and/or ≥2x quantity spike vs. aging average) |

`attack_succeeded_against_agent = True` only for `successful` — same
contract as Track A/B.

## Run

From `red_team/track_c_synthetic_identity_chain/`:

```bash
python run_track_c.py --campaign-id demo1 --identities 1
python run_track_c.py --campaign-id full-run --round 1 --identities 3
```

Smoke-test the identity generator alone:

```bash
python synthetic_identity_gen.py
```

Outputs:

```
logs/<campaign_id>_attack_events.jsonl        # Blue-Team-facing handoff
logs/<campaign_id>_red_team_internal.jsonl    # KYC + deviation detail, ground truth
logs/<campaign_id>_errors.jsonl               # execution errors, never scored as success
```

## Handoff contract (matches Track A/B)

- `AttackEvent.track = "track_c_synthetic_identity"`
- `audio_file_path = None` always (no audio in this track)
- `transaction_fields` = `{aging_avg_quantity, aging_address,
  cashout_quantity, cashout_address, address_changed_at_cashout,
  quantity_spike_ratio}` — for Blue Team's transaction-integrity/graph
  layer
- Identity + KYC ground truth stays Red-Team-side in
  `*_red_team_internal.jsonl`, never added to the shared `AttackEvent`
- `campaign_id` / `round_number` / `attack_variant_id` preserved for
  the adaptive-loop architecture

## Ethics

No real PII, no real government-ID formats, no real face images, no
real prior-transaction data. All identity content is fabricated test
fixture data (`SYN-TEST-########` fragments, text-only face
descriptors, invented history narratives). See
`docs/ethics_and_safety.md`.
