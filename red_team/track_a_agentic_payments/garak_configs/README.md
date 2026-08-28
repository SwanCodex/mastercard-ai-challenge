# garak_configs/

Automated payload-wording-variant generation for Track A.

Per `Solution_And_Team_Plan.md` (Person A, Day 4): *"Stand up
`garak_configs/` for automated variant generation."*

## What actually runs Track A

`run_track_a.py` (one level up) never depends on anything in this
folder. The taxonomy, payload library (`../injection_payloads/`), the
mock agents, and success scoring are fully self-contained and
garak-free. Nothing here is required for the benchmark to run.

## What this folder adds

Two independent ways to generate MORE wording variants beyond what
`../injection_payloads/payload_generator.py` already produces (docs
§10.1, §19 "Attack Generation Strategy"):

### 1. `generate_variants.py` — no external dependency, use this first

Reads every payload JSON file under `../injection_payloads/*/` and
writes supplementary wording-style variants (explicit command / important
notice / security warning / operational procedure / helpful
recommendation / verification message / system-looking tag) into a
`garak_variants/` subfolder next to each source file. Never overwrites
existing files; safe to re-run at any time.

```bash
cd track_a_agentic_payments/garak_configs
python generate_variants.py
```

### 2. `agentic_payments_probe.py` + `track_a_garak_config.yaml` — optional, requires garak

A thin custom garak probe that surfaces garak's own injection/jailbreak
prompt corpora as additional raw wording material. garak's plugin API
changes between versions; if this probe doesn't load under whatever
version you install, ignore it and use option 1 instead - it covers the
same need without the dependency risk.

```bash
pip install garak
garak --config track_a_garak_config.yaml
```

## Feeding generated variants back into the benchmark

Files written to `../injection_payloads/*/garak_variants/*.json` use the
exact same record shape as the rest of `injection_payloads/`. They are
kept out of the default `run_track_a.py` scan on purpose (so an
experimental/ungraded variant never silently enters a real campaign) -
to include them, add the `garak_variants` subfolders to `PAYLOAD_DIRS`
at the top of `run_track_a.py` once you've reviewed them.
