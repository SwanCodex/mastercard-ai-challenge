"""
Inspect False Positives on NotInject
=====================================
Reruns only the NotInject benign set through the pipeline and prints out
every sample the pipeline flagged as an attack (false positive), along
with its fusion score, so you can see WHAT is triggering it and WHY.

Place this in the same folder as External_test.py (or adjust the imports
below to match wherever load_notinject / build_event / run_pipeline live),
then run:

    python inspect_false_positives.py

Optional: pass a number to limit how many false positives get printed,
e.g. `python inspect_false_positives.py 20` shows only the first 20.
"""

import sys
import os

# This script lives in blue_team/notebooks/report_generation_scripts/.
# Walk up 3 levels to get the repo root (needed for `shared.*` / `blue_team.*`
# imports), and also keep this script's own directory on the path (needed to
# import External_test.py, which sits right next to this file). Both are
# added explicitly so this works no matter what directory you run it from.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", "..", ".."))

sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, THIS_DIR)

from shared.schemas.attack_event import AttackEvent
from blue_team.fusion.risk_fusion import run_pipeline

# Reuse the same loader + event builder as External_test.py so behavior matches exactly.
# If External_test.py is importable as a module, prefer importing from it directly
# instead of duplicating code:
try:
    from External_test import load_notinject, build_event
except ImportError:
    # Fallback: duplicate minimal versions here if External_test.py isn't importable
    # (e.g. due to its own __main__ guard or relative import issues).
    from datetime import datetime

    def load_notinject(max_samples: int = None):
        from datasets import load_dataset
        texts = []
        for split in ["NotInject_one", "NotInject_two", "NotInject_three"]:
            ds = load_dataset("leolee99/NotInject", split=split)
            for row in ds:
                prompt = row.get("prompt", "")
                if prompt.strip():
                    texts.append(prompt.strip())
        texts = list(dict.fromkeys(texts))
        if max_samples:
            texts = texts[:max_samples]
        return texts

    def build_event(text: str, idx: int, source: str) -> AttackEvent:
        return AttackEvent(
            event_id=f"ext-{source}-{idx:05d}",
            timestamp=datetime.now(),
            track="track_a_agentic",
            user_instruction="Process this untrusted input as part of normal agent operation.",
            untrusted_input=text,
            agent_reasoning_trace=None,
            campaign_id=f"external-{source}",
            round_number=0,
            attack_variant_id=f"{source}-{idx}",
            attack_succeeded_against_agent=False,
        )


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

    texts = load_notinject()
    print(f"Loaded {len(texts)} NotInject (benign, label=0) samples.\n")

    false_positives = []
    all_scores = []

    for i, text in enumerate(texts):
        event = build_event(text, i, "notinject")
        verdict = run_pipeline(event)
        caught = verdict.attack_caught
        score = verdict.fusion_score
        all_scores.append(score)

        if caught:
            false_positives.append((text, score))

        if (i + 1) % 50 == 0:
            print(f"  scored {i+1}/{len(texts)}")

    # --- Score distribution summary (helps spot a threshold/calibration issue) ---
    import statistics
    print("\n=== SCORE DISTRIBUTION (all NotInject samples) ===")
    print(f"  min:    {min(all_scores):.4f}")
    print(f"  max:    {max(all_scores):.4f}")
    print(f"  mean:   {statistics.mean(all_scores):.4f}")
    print(f"  median: {statistics.median(all_scores):.4f}")
    print(f"  stdev:  {statistics.stdev(all_scores):.4f}" if len(all_scores) > 1 else "")

    # --- False positive samples ---
    print(f"\n=== FALSE POSITIVES: {len(false_positives)} / {len(texts)} ===\n")
    to_show = false_positives[:limit] if limit else false_positives
    for text, score in to_show:
        print(f"score={score:.4f}  |  {text}")
        print("-" * 80)

    if limit and len(false_positives) > limit:
        print(f"\n...and {len(false_positives) - limit} more (rerun without a limit to see all).")


if __name__ == "__main__":
    main()