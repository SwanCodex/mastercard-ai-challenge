# SENTINEL — Blue Team Defense Architecture (Person B)

## Overview
The defense stack is a **5-layer pipeline** that scores an incoming `attack_event`
(from the red team) and produces a calibrated `verdict`: approve / step-up / decline / review.
Each layer is independent and can run/be tested in isolation, then wired together
by the fusion layer.

## Why layered, not one model
A single model is a single point of failure and hard to explain to judges/analysts.
Mirrors LlamaFirewall's proven design: fast filter → classifier → reasoning audit →
downstream risk model → modality-specific detectors → fusion.

## Layer 1 — Fast Filters
- **What**: regex/heuristic rules + LLM Guard input scanners
- **Why first**: near-zero latency, catches obvious/known payloads, gives us a
  working (if crude) defense on Day 2
- **Input**: raw agent instruction / tool output text
- **Output**: boolean flag + matched-rule reason

## Layer 2 — Injection Classifier
- **What**: ProtectAI `deberta-v3-base-prompt-injection-v2`, fine-tuned further
  on payments-specific payloads as Samiksha produces them
- **Why**: small (184M params), fast enough to fine-tune on Colab/single GPU in a day
- **Input**: same text as Layer 1
- **Output**: injection probability score (0-1)

## Layer 3 — Agent Alignment Check (LLM-as-judge)
- **What**: single-shot LLM call comparing the agent's tool-call trace / reasoning
  against the user's original authorized instruction
- **Why**: catches injections that don't look like "attacks" lexically but cause
  the agent to act outside the user's actual intent
- **Input**: (user_instruction, agent_reasoning_trace, tool_calls_made)
- **Output**: alignment score + natural-language rationale

## Layer 4 — Transaction Risk Model
- **What**: GraphSAGE/GAT (PyTorch Geometric) on a transaction-entity graph
  (nodes: card/account, merchant, device; edges: transactions)
- **Baseline**: flat XGBoost on same features — REQUIRED for the "GNN beats
  XGBoost by X% AUROC" headline stat
- **Data**: IEEE-CIS Fraud Detection + PaySim, augmented with synthetic
  agentic fields (agent_id, tool_call_trace, consent_token, injection_score)
- **Output**: fraud risk score (0-1)

## Layer 5 — Deepfake/Audio Detector
- **What**: pretrained wav2vec2 embeddings + lightweight classifier head,
  evaluated ASVspoof-style
- **Input**: audio clip from Track B vishing attempts
- **Output**: spoof probability score (0-1)

## Fusion Layer
- Combines all 5 layer scores into one calibrated risk score
- Maps to decision: approve / step-up / decline / review
- Outputs SHAP-based explanation (tabular/graph) + LLM-judge rationale (Layer 3)
  for the analyst "why flagged" view

## Data Flow
```
attack_event (from red team)
      │
      ▼
 Layer 1 (fast filters) ──┐
      │                    │
      ▼                    │
 Layer 2 (injection clf)  │  each layer emits a
      │                    │  partial score, all
      ▼                    │  logged independently
 Layer 3 (alignment)  ────┤  for debugging/explainability
      │                    │
      ▼                    │
 Layer 4 (txn risk GNN) ──┤
      │                    │
      ▼                    │
 Layer 5 (deepfake) ──────┘
      │
      ▼
   Fusion → verdict.py output → orchestrator → dashboard
```

## Key Metrics to Track (own these numbers, don't inflate them)
- Zero-shot vs fine-tuned Layer 2 catch rate
- GNN AUROC vs XGBoost AUROC (Day 6)
- Attack success rate before/after adaptive retrain (Day 8-9)
- False positive rate on legitimate transactions (Day 8 stress test)
- Per-layer + end-to-end latency
