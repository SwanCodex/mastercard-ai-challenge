"""
External Generalization Evaluation
===================================
Runs the SENTINEL Blue Team full pipeline (Layers 1-3 + fusion; Layers 4/5
auto-skip since these are text-only samples, exactly as risk_fusion.py
already handles via the transaction_fields / audio_file_path checks) against
two external, held-out benchmarks the classifier was never trained or
fine-tuned on:

  - Tensor Trust (hijacking robustness subset)  -> malicious / label=1
  - NotInject                                    -> benign    / label=0

Outputs per-dataset AND combined:
  Evaluation cases, Precision, Recall, F1, AUROC, False-Positive Rate
plus one confusion-matrix PNG per dataset and one combined.

WHERE TO RUN THIS: inside your repo root (same level you already run
`python -m blue_team.notebooks.report_generation_scripts.generate_charts`
from), so that `blue_team.*` and `shared.schemas.*` imports resolve.

INSTALL (once):
    pip install datasets scikit-learn matplotlib requests

USAGE:
    python eval_external_generalization.py
"""

import json
import os
import sys
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
)

# ---- repo imports: adjust the sys.path insert below if this script lives
# ---- somewhere other than the repo root -----------------------------------
sys.path.insert(0, os.getcwd())

from shared.schemas.attack_event import AttackEvent
from blue_team.fusion.risk_fusion import run_pipeline  # adjust path if risk_fusion.py lives elsewhere

OUT_DIR = "blue_team/notebooks/figures"
RESULTS_PATH = "blue_team/notebooks/external_generalization_results.json"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)


# -----------------------------------------------------------------------
# 1. DATA LOADING
# -----------------------------------------------------------------------

def load_tensor_trust(max_samples: int = None):
    """
    Loads the Tensor Trust *hijacking* robustness benchmark (attacker
    inputs only -> these are the malicious/label=1 samples).

    Tries the HuggingFace `datasets` library first (qxcv/tensor-trust).
    If that config errors out (the HF dataset viewer has known schema
    issues across its sub-configs), falls back to pulling the raw JSONL
    straight from the HumanCompatibleAI/tensor-trust-data GitHub repo.
    """
    texts = []

    # --- Attempt 1: HuggingFace datasets ---
    try:
        from datasets import load_dataset
        ds = load_dataset("qxcv/tensor-trust", "hijacking-robustness", split="train")
        for row in ds:
            attack_text = row.get("attack") or row.get("access_code_output") or ""
            if attack_text.strip():
                texts.append(attack_text.strip())
    except Exception as e:
        print(f"[tensor-trust] HF load failed ({e}); falling back to GitHub raw JSONL.")

    # --- Attempt 2: raw GitHub JSONL fallback ---
    if not texts:
        import requests
        url = (
            "https://raw.githubusercontent.com/HumanCompatibleAI/tensor-trust-data/"
            "main/benchmarks/hijacking-robustness/v1/hijacking_robustness_dataset.jsonl"
        )
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        for line in r.text.strip().split("\n"):
            row = json.loads(line)
            attack_text = row.get("attack", "")
            if attack_text.strip():
                texts.append(attack_text.strip())

    if max_samples:
        texts = texts[:max_samples]

    print(f"[tensor-trust] loaded {len(texts)} malicious (label=1) samples.")
    return texts


def load_notinject(max_samples: int = None):
    """
    Loads NotInject (339 benign hard-negative samples, label=0).
    """
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

    print(f"[notinject] loaded {len(texts)} benign (label=0) samples.")
    return texts

# -----------------------------------------------------------------------
# 2. RUN FULL PIPELINE
# -----------------------------------------------------------------------

def build_event(text: str, idx: int, source: str) -> AttackEvent:
    return AttackEvent(
        event_id=f"ext-{source}-{idx:05d}",
        timestamp=datetime.now(),
        track="track_a_agentic",  # closest fit: Layer 2 injection classifier, no live agent
        user_instruction="Process this untrusted input as part of normal agent operation.",
        untrusted_input=text,
        agent_reasoning_trace=None,
        campaign_id=f"external-{source}",
        round_number=0,
        attack_variant_id=f"{source}-{idx}",
        # schema requires a bool here; there's no live agent in this eval so
        # this field isn't semantically meaningful — hardcode False and treat
        # ground truth (the `label` passed into evaluate_dataset) as the
        # source of truth for scoring instead
        attack_succeeded_against_agent=False,
    )

def evaluate_dataset(texts: list[str], label: int, source_name: str):
    """Runs every sample through run_pipeline; returns preds, scores, gt."""
    preds, scores = [], []
    for i, text in enumerate(texts):
        event = build_event(text, i, source_name)
        verdict = run_pipeline(event)
        preds.append(1 if verdict.attack_caught else 0)
        scores.append(verdict.fusion_score)
        if (i + 1) % 50 == 0:
            print(f"  [{source_name}] {i+1}/{len(texts)} scored")
    gt = [label] * len(texts)
    return preds, scores, gt


# -----------------------------------------------------------------------
# 3. METRICS + CONFUSION MATRIX PNG
# -----------------------------------------------------------------------

def compute_metrics(y_true, y_pred, y_score):
    n = len(y_true)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    # AUROC needs both classes present; if a dataset is single-class
    # (e.g. NotInject alone is all label=0), AUROC is undefined for that
    # dataset in isolation -- report it only for the combined set.
    try:
        auroc = roc_auc_score(y_true, y_score)
    except ValueError:
        auroc = None

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else None

    return {
        "evaluation_cases": n,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "auroc": round(auroc, 4) if auroc is not None else None,
        "false_positive_rate": round(fpr, 4) if fpr is not None else None,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def save_confusion_matrix_png(y_true, y_pred, title: str, filename: str):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(5, 4.5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Benign", "Malicious"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["Benign", "Malicious"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(title)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=13)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


# -----------------------------------------------------------------------
# 4. MAIN
# -----------------------------------------------------------------------

def main():
    tt_texts = load_tensor_trust()
    ni_texts = load_notinject()

    tt_preds, tt_scores, tt_gt = evaluate_dataset(tt_texts, label=1, source_name="tensor_trust")
    ni_preds, ni_scores, ni_gt = evaluate_dataset(ni_texts, label=0, source_name="notinject")

    results = {}

    # Tensor Trust alone (recall-focused; AUROC undefined, single class)
    results["tensor_trust"] = compute_metrics(tt_gt, tt_preds, tt_scores)
    save_confusion_matrix_png(tt_gt, tt_preds, "Tensor Trust — Confusion Matrix", "10_confusion_tensor_trust.png")

    # NotInject alone (FPR-focused; AUROC undefined, single class)
    results["notinject"] = compute_metrics(ni_gt, ni_preds, ni_scores)
    save_confusion_matrix_png(ni_gt, ni_preds, "NotInject — Confusion Matrix", "11_confusion_notinject.png")

    # Combined (this is where AUROC becomes meaningful -- both classes present)
    combined_gt = tt_gt + ni_gt
    combined_pred = tt_preds + ni_preds
    combined_score = tt_scores + ni_scores
    results["combined"] = compute_metrics(combined_gt, combined_pred, combined_score)
    save_confusion_matrix_png(combined_gt, combined_pred, "Combined External Benchmark — Confusion Matrix", "12_confusion_combined_external.png")

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print("\n=== EXTERNAL GENERALIZATION RESULTS ===")
    print(json.dumps(results, indent=2))
    print(f"\nSaved full results to {RESULTS_PATH}")
    print(f"Confusion matrix PNGs saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()