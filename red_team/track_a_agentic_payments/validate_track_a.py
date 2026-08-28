"""
Track A offline structural validator.

No OpenAI.
No Anthropic.
No network calls.

Run from repository root:

    python red_team/track_a_agentic_payments/validate_track_a.py
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRACK_A = ROOT / "red_team" / "track_a_agentic_payments"
PAYLOAD_DIR = TRACK_A / "injection_payloads"


EXPECTED_FILES = [
    "mock_shopping_agent.py",
    "mock_invoice_agent.py",
    "run_track_a.py",
]

EXPECTED_ATTACK_IDS = {
    f"A{i:02d}"
    for i in range(1, 27)
}


def check_file_structure():
    print("\n=== FILE STRUCTURE ===")

    failures = []

    for filename in EXPECTED_FILES:
        path = TRACK_A / filename

        if path.exists():
            print(f"[PASS] {filename}")
        else:
            print(f"[FAIL] Missing: {filename}")
            failures.append(filename)

    if PAYLOAD_DIR.exists():
        print("[PASS] injection_payloads/")
    else:
        print("[FAIL] Missing injection_payloads/")
        failures.append("injection_payloads")

    return failures


def check_python_syntax():
    print("\n=== PYTHON SYNTAX ===")

    failures = []

    for path in TRACK_A.rglob("*.py"):
        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(path))
            print(f"[PASS] {path.relative_to(ROOT)}")
        except SyntaxError as exc:
            print(f"[FAIL] {path.relative_to(ROOT)}")
            print(f"       {exc}")
            failures.append(str(path))

    return failures


def check_for_paid_api_dependencies():
    print("\n=== OFFLINE / NO-API CHECK ===")

    failures = []

    forbidden_imports = {
        "anthropic",
        "openai",
    }

    for path in TRACK_A.rglob("*.py"):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            continue

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".")[0]

                    if root_name in forbidden_imports:
                        print(
                            f"[FAIL] {path.relative_to(ROOT)} "
                            f"imports {root_name}"
                        )
                        failures.append(
                            f"{path}:{root_name}"
                        )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_name = node.module.split(".")[0]

                    if root_name in forbidden_imports:
                        print(
                            f"[FAIL] {path.relative_to(ROOT)} "
                            f"imports {root_name}"
                        )
                        failures.append(
                            f"{path}:{root_name}"
                        )

    if not failures:
        print("[PASS] No OpenAI/Anthropic imports detected.")

    return failures


def load_json_files():
    """
    Load all JSON files in injection_payloads/.
    """

    documents = []

    if not PAYLOAD_DIR.exists():
        return documents

    for path in PAYLOAD_DIR.rglob("*.json"):

        try:
            data = json.loads(
                path.read_text(encoding="utf-8")
            )

            documents.append((path, data))

        except Exception as exc:
            print(
                f"[FAIL] Invalid JSON: "
                f"{path.relative_to(ROOT)}"
            )
            print(f"       {exc}")

    return documents


def extract_variant_records(data):
    """
    Recursively locate dictionaries containing an attack/variant ID.
    """

    records = []

    if isinstance(data, dict):

        for key, value in data.items():

            if isinstance(value, str):
                if re.fullmatch(
                    r"A(?:0[1-9]|1[0-9]|2[0-6])-v\d+",
                    value,
                ):
                    records.append(
                        {
                            "id": value,
                            "container": data,
                        }
                    )

            records.extend(
                extract_variant_records(value)
            )

    elif isinstance(data, list):

        for item in data:
            records.extend(
                extract_variant_records(item)
            )

    return records


def check_payload_variants():
    print("\n=== PAYLOAD VARIANT CHECK ===")

    documents = load_json_files()

    all_variants = []
    locations = {}

    for path, data in documents:

        records = extract_variant_records(data)

        for record in records:

            variant_id = record["id"]

            locations.setdefault(
                variant_id,
                []
            ).append(path)

            all_variants.append(variant_id)

    unique_variants = set(all_variants)

    print(
        f"Found {len(unique_variants)} unique "
        f"concrete variant IDs."
    )

    expected_count = 58

    if len(unique_variants) == expected_count:
        print(
            f"[PASS] Exactly {expected_count} "
            "unique variants found."
        )
    else:
        print(
            f"[FAIL] Expected {expected_count} "
            f"unique variants, found "
            f"{len(unique_variants)}."
        )
        return False

    duplicates = {
        variant_id: paths
        for variant_id, paths in locations.items()
        if len(paths) > 1
    }

    if duplicates:
        print(
            "[WARN] Variant IDs appear in multiple "
            "JSON files."
        )

        for variant_id, paths in duplicates.items():
            print(f"       {variant_id}")

            for path in paths:
                print(
                    f"          "
                    f"{path.relative_to(ROOT)}"
                )

    return True


def check_attack_family_coverage():
    print("\n=== ATTACK FAMILY COVERAGE ===")

    documents = load_json_files()

    variants = set()

    for _, data in documents:
        for record in extract_variant_records(data):
            variants.add(record["id"])

    attack_ids = {
        variant.split("-")[0]
        for variant in variants
    }

    missing = EXPECTED_ATTACK_IDS - attack_ids

    print(
        f"Found {len(attack_ids)}/26 attack families "
        "in payload JSON."
    )

    for attack_id in sorted(attack_ids):
        print(f"[PASS] {attack_id}")

    if missing:

        for attack_id in sorted(missing):
            print(f"[FAIL] {attack_id} missing")

        return False

    return True


def check_payload_files():
    print("\n=== PAYLOAD FILE CHECK ===")

    files = list(PAYLOAD_DIR.rglob("*"))

    payload_files = [
        path
        for path in files
        if path.is_file()
    ]

    print(
        f"Found {len(payload_files)} "
        "payload-related files."
    )

    if not payload_files:
        print("[FAIL] No payload files found.")
        return False

    for path in payload_files:
        print(
            f"[PASS] {path.relative_to(ROOT)}"
        )

    return True


def main():

    print("=" * 70)
    print("TRACK A OFFLINE VALIDATION")
    print("=" * 70)

    failures = []

    failures.extend(
        check_file_structure()
    )

    failures.extend(
        check_python_syntax()
    )

    failures.extend(
        check_for_paid_api_dependencies()
    )

    payload_files_ok = check_payload_files()

    attack_coverage_ok = (
        check_attack_family_coverage()
    )

    variants_ok = check_payload_variants()

    print("\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    if (
        failures
        or not payload_files_ok
        or not attack_coverage_ok
        or not variants_ok
    ):
        print(
            "[FAIL] Offline structural validation "
            "found problems."
        )
        return 1

    print(
        "[PASS] Offline structural validation "
        "completed successfully."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())