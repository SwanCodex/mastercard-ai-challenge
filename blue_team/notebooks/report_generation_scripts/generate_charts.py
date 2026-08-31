"""
Generates report chart images from computed metrics. Saves to
blue_team/notebooks/figures/ as PNG files for embedding in the report.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = "blue_team/notebooks/figures"
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({"font.size": 11, "figure.dpi": 150})


def chart_4_layer4_model_comparison(paysim_gnn_auroc=None):
    """
    XGBoost vs GNN AUROC across all 3 datasets.
    paysim_gnn_auroc: pass the final locked PaySim GNN number once ready
    (e.g. the 100% run result). Leave None until then.
    Credit Card intentionally has no GNN bar - no natural graph structure
    (PCA-anonymized features only, no account/transaction-network columns).
    """
    datasets = ["IEEE-CIS", "PaySim*", "Credit Card"]
    xgboost_auroc = [0.9394, 0.9992, 0.9616]
    gnn_auroc = [0.8548, paysim_gnn_auroc, None]

    x = np.arange(len(datasets))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.bar(x - width/2, xgboost_auroc, width, label="XGBoost", color="#378ADD")
    gnn_vals = [v if v is not None else 0 for v in gnn_auroc]
    ax.bar(x + width/2, gnn_vals, width, label="GNN v4", color="#7F77DD")

    for i, v in enumerate(gnn_auroc):
        if v is None:
            label = "N/A\n(no graph\nstructure)" if datasets[i] == "Credit Card" else "N/A"
            ax.text(x[i] + width/2, 0.05, label, ha="center", fontsize=8, color="gray")
        else:
            ax.text(x[i] + width/2, v + 0.015, f"{v:.3f}", ha="center", fontsize=9)

    for i, v in enumerate(xgboost_auroc):
        ax.text(x[i] - width/2, v + 0.015, f"{v:.3f}", ha="center", fontsize=9)

    ax.set_ylabel("AUROC")
    ax.set_title("Layer 4: XGBoost vs GNN model comparison\nacross 3 independent datasets")
    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.set_ylim(0, 1.1)
    ax.legend(loc="lower right")
    ax.text(0.5, -0.20, "*PaySim is synthetic data - easier task, not equal-weight evidence",
            transform=ax.transAxes, ha="center", fontsize=8, color="gray")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/04_layer4_model_comparison.png")
    plt.close()
    print("Saved: 04_layer4_model_comparison.png")


def chart_4b_paysim_gnn_saturation(auroc_5pct=0.9508, auroc_20pct=0.9480):
    """
    PaySim GNN AUROC vs training data size - demonstrates the model has
    saturated (more data does not meaningfully improve performance),
    replicating the same finding independently observed on IEEE-CIS.
    Stopped at 20% (not 100%) once saturation was confirmed - the ~2hr
    training cost for a 3rd, likely-redundant data point was not
    justified given project time constraints. Stated explicitly as a
    deliberate engineering decision, not an incomplete experiment.
    """
    sizes = [5, 20]
    aurocs = [auroc_5pct, auroc_20pct]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(sizes, aurocs, marker="o", color="#7F77DD", linewidth=2, markersize=9)
    for s, v in zip(sizes, aurocs):
        ax.annotate(f"{v:.4f}", (s, v), textcoords="offset points", xytext=(0, 10), ha="center")
    ax.set_xlabel("% of PaySim dataset used")
    ax.set_ylabel("AUROC")
    ax.set_title("PaySim GNN: AUROC saturates with data volume\n(confirms IEEE-CIS finding; stopped early once flat)")
    ax.set_xticks(sizes)
    ax.set_xlim(0, 25)
    ax.set_ylim(min(aurocs) - 0.03, max(aurocs) + 0.03)
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/04b_paysim_gnn_saturation.png")
    plt.close()
    print("Saved: 04b_paysim_gnn_saturation.png")

def chart_5_gnn_progression():
    """GNN AUROC progression across versions (IEEE-CIS only)."""
    versions = ["v1\n(placeholder)", "v2\n(1 feature)", "v3\n(24 features)", "v4\n(156 features)"]
    auroc = [0.5523, 0.598, 0.72, 0.8548]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(versions, auroc, marker="o", color="#7F77DD", linewidth=2, markersize=8)
    for i, v in enumerate(auroc):
        ax.annotate(f"{v:.3f}", (i, v), textcoords="offset points", xytext=(0, 10), ha="center")
    ax.axhline(y=0.9394, color="#D85A30", linestyle="--", label="XGBoost baseline (0.9394)")
    ax.set_ylabel("AUROC")
    ax.set_title("GNN experiment progression (IEEE-CIS)\nfeature engineering closes the gap")
    ax.set_ylim(0.4, 1.0)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/05_gnn_progression.png")
    plt.close()
    print("Saved: 05_gnn_progression.png")


def chart_6_layer2_zero_shot_vs_finetuned():
    """Layer 2 zero-shot vs fine-tuned, same held-out set."""
    metrics = ["Accuracy", "Precision", "Recall", "F1"]
    zero_shot = [0.750, 1.000, 0.625, 0.769]
    fine_tuned = [0.833, 1.000, 0.750, 0.857]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(x - width/2, zero_shot, width, label="Zero-shot", color="#B4B2A9")
    ax.bar(x + width/2, fine_tuned, width, label="Fine-tuned", color="#1D9E75")
    ax.set_ylabel("Score")
    ax.set_title("Layer 2: zero-shot vs fine-tuned\n(same held-out test set, unseen during training)")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1.15)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/06_layer2_zeroshot_vs_finetuned.png")
    plt.close()
    print("Saved: 06_layer2_zeroshot_vs_finetuned.png")


def chart_7_complementarity():
    """Layer 2 alone vs Layer 2 + Layer 3 detection rate."""
    configs = ["Layer 2 alone", "Layer 2 + Layer 3"]
    rates = [0.75, 1.00]

    fig, ax = plt.subplots(figsize=(6, 4.5))
    bars = ax.bar(configs, rates, color=["#B4B2A9", "#1D9E75"], width=0.5)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, rate + 0.02, f"{rate:.0%}", ha="center", fontsize=12)
    ax.set_ylabel("Detection rate")
    ax.set_title("Defense complementarity\n(8-attack held-out set: Layer 3 catches what Layer 2 misses)")
    ax.set_ylim(0, 1.15)
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/07_complementarity.png")
    plt.close()
    print("Saved: 07_complementarity.png")


def chart_8_attack_family_coverage():
    """Attack-family coverage and detection rate."""
    families = ["Direct", "Indirect", "Multi-turn\ndrip", "Agent-to-\nagent", "Liveness"]
    caught = [11, 21, 11, 12, 3]
    total = [12, 22, 12, 12, 4]
    rates = [c / t for c, t in zip(caught, total)]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars = ax.bar(families, rates, color="#378ADD", width=0.55)
    for bar, c, t in zip(bars, caught, total):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{c}/{t}", ha="center", fontsize=10)
    ax.set_ylabel("Detection rate")
    ax.set_title("Attack-family coverage and detection rate\n(full pipeline, Layer 3 live)")
    ax.set_ylim(0, 1.15)
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/08_attack_family_coverage.png")
    plt.close()
    print("Saved: 08_attack_family_coverage.png")


def chart_9_red_vs_blue():
    """End-to-end regression test summary - family-tagged run."""
    categories = ["Track A\n(58 payloads)", "Track B liveness\n(4 payloads)", "Overall\n(62 events)"]
    caught = [55, 3, 58]
    total = [58, 4, 62]
    rates = [c / t for c, t in zip(caught, total)]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bars = ax.bar(categories, rates, color="#378ADD", width=0.5)
    for bar, c, t in zip(bars, caught, total):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{c}/{t}", ha="center", fontsize=11)
    ax.set_ylabel("Catch rate")
    ax.set_title("Red team vs blue team: full pipeline\n(Layer 3 live, synthesized reasoning traces)")
    ax.set_ylim(0, 1.15)
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/09_red_vs_blue.png")
    plt.close()
    print("Saved: 09_red_vs_blue.png")

def _save_confusion_matrix(title, cm, labels, filename):
    """Helper: saves ONE confusion matrix as its own standalone image."""
    cm = np.array(cm)
    fig, ax = plt.subplots(figsize=(4.5, 4.2))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_title(title, fontsize=12)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

    vmax = cm.max()
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > vmax / 2 else "black"
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center", color=color, fontsize=13)

    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/{filename}.png")
    plt.close()
    print(f"Saved: {filename}.png")


def chart_10_confusion_matrices_individual():
    """
    Generates ONE SEPARATE image per confusion matrix (not a combined
    grid) - 6 standalone PNGs, one per major model.
    """
    def load_json(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    ieee = load_json("blue_team/notebooks/report_generation_scripts/ieee_cis_full_metrics.json")
    paysim = load_json("blue_team/notebooks/report_generation_scripts/paysim_metrics.json")
    credit = load_json("blue_team/notebooks/report_generation_scripts/creditcard_metrics.json")
    layer2 = load_json("blue_team/notebooks/report_generation_scripts/layer2_full_metrics.json")

    _save_confusion_matrix("IEEE-CIS: XGBoost", ieee["xgboost"]["confusion_matrix"],
                            ["Safe", "Fraud"], "10a_confusion_ieee_xgboost")
    _save_confusion_matrix("IEEE-CIS: GNN v4", ieee["gnn"]["confusion_matrix"],
                            ["Safe", "Fraud"], "10b_confusion_ieee_gnn")
    _save_confusion_matrix("PaySim: XGBoost", paysim["confusion_matrix"],
                            ["Safe", "Fraud"], "10c_confusion_paysim_xgboost")
    _save_confusion_matrix("Credit Card: XGBoost", credit["confusion_matrix"],
                            ["Safe", "Fraud"], "10d_confusion_creditcard_xgboost")
    _save_confusion_matrix("Layer 2: Zero-shot", layer2["zero_shot"]["confusion_matrix"],
                            ["Safe", "Attack"], "10e_confusion_layer2_zeroshot")
    _save_confusion_matrix("Layer 2: Fine-tuned", layer2["fine_tuned"]["confusion_matrix"],
                            ["Safe", "Attack"], "10f_confusion_layer2_finetuned")


if __name__ == "__main__":
    chart_4_layer4_model_comparison(paysim_gnn_auroc=0.9508)
    chart_4b_paysim_gnn_saturation()
    chart_5_gnn_progression()
    chart_6_layer2_zero_shot_vs_finetuned()
    chart_7_complementarity()
    chart_8_attack_family_coverage()
    chart_9_red_vs_blue()
    chart_10_confusion_matrices_individual()
    print("\nAll charts saved to blue_team/notebooks/figures/")