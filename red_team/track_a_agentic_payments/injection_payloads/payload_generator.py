"""
Track A payload loader/generator.

Loads the A01-A26 payload families from JSON and exposes deterministic
variant iteration. The scenario definitions are derived directly from the
Track A implementation contract; this module does not invent new attack
families.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


BASE_DIR = Path(__file__).resolve().parent
PAYLOAD_DIR = BASE_DIR

FILES = (
    PAYLOAD_DIR / "direct" / "direct_payloads.json",
    PAYLOAD_DIR / "indirect" / "indirect_payloads.json",
    PAYLOAD_DIR / "multi_turn_drip" / "multi_turn_drip_payloads.json",
    PAYLOAD_DIR / "agent_to_agent" / "agent_to_agent_payloads.json",
)


def load_payload_families() -> List[Dict[str, Any]]:
    families: List[Dict[str, Any]] = []
    for path in FILES:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        families.extend(data["payloads"])
    return families


def iter_variants() -> Iterable[Dict[str, Any]]:
    for family in load_payload_families():
        for variant in family["variants"]:
            yield {
                "attack_id": family["id"],
                "attack_name": family["name"],
                "target": family["target"],
                "injection_location": family["injection_location"],
                "objective": family["objective"],
                "ground_truth_authorized": family["ground_truth_authorized"],
                "success_check": family["success_check"],
                **variant,
            }


def get_variant(attack_variant_id: str) -> Dict[str, Any]:
    for variant in iter_variants():
        if variant["id"] == attack_variant_id:
            return variant
    raise KeyError(f"Unknown Track A attack variant: {attack_variant_id}")


def list_variant_ids() -> List[str]:
    return [variant["id"] for variant in iter_variants()]


if __name__ == "__main__":
    variants = list(iter_variants())
    print(f"Loaded {len(load_payload_families())} attack families.")
    print(f"Loaded {len(variants)} concrete variants.")
    print("\n".join(v["id"] for v in variants))
