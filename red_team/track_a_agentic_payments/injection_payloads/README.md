# Track A Injection Payload Library

This directory contains the executable payload definitions for A01-A26.

- `direct/` — A01-A05 and A21
- `indirect/` — A06-A10 and A22-A24
- `multi_turn_drip/` — A11-A15 and A25
- `agent_to_agent/` — A16-A20 and A26
- `payload_generator.py` — deterministic loader/variant iterator

The JSON files are the source data for the Track A runner. They do not
execute anything against real systems; they describe payloads for the
deterministic mock agents.
