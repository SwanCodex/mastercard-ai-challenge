# Adversarial AI Defense Lab for Payment Security
### Full Solution Architecture, Research Foundation & 11-Day Execution Plan
### Mastercard Innovation Challenge 2026 · Global Fintech Fest, Mumbai

---

## PART 1 — THE WINNING IDEA (grounded in real research, not vibes)

### 1.1 The core insight

Every competing team at GFF 2026 will pitch some version of "deepfake KYC bypass detector" or "AI phishing detector" — these are the most over-covered fraud stories of 2026 (Sumsub, Entrust, Shufti, PwC, Deloitte all published near-identical reports this year: ~495% projected growth in deepfake identity fraud, 40% YoY rise in injection attacks, $40B in GenAI-enabled fraud losses projected by 2027). If that's your *whole* pitch, you're the tenth team judges see doing it.

**The differentiator is the attack surface nobody else is building for: AI payment agents.** In 2026, agentic commerce is live — ChatGPT/Claude/Comet-style agents complete checkouts, AP-automation agents pay invoices, and bank "assistant" agents move money on instruction. Academic security research confirms this is now a formally studied attack surface: **AgentDojo** (Debenedetti et al., NeurIPS 2024) established the standard benchmark — 97 realistic agent tasks and 629 indirect-prompt-injection security test cases across tool-using LLM agents — and a fast-growing 2025–2026 literature (InjecAgent, ASB, CaMeL, Progent, LlamaFirewall, FinHarness) is actively racing to defend it. **This is a real, current, unsolved, peer-reviewed research problem — not a hackathon toy.** Almost no other team at a fintech hackathon will have read this literature or have a working demo against it.

**SENTINEL's pitch in one line:**
> "GenAI fraud isn't just better phishing and better deepfakes — it created a brand-new attack surface: autonomous AI agents that pay on our behalf. SENTINEL is the first red-team/blue-team system that attacks and defends *agentic payment flows*, and we prove it also generalizes to the deepfake/synthetic-identity fraud everyone already knows about."

### 1.2 The three attack tracks (Identify → Generate, per the brief)

**Track A — Agentic Payment Hijacking (headline / novel track)**
Built directly on the AgentDojo threat model, adapted to a payments context:
1. **Indirect prompt injection via merchant content** — a poisoned product page, review, or return-policy text instructs a shopping agent to change the shipping address, add a "processing fee," or approve a higher amount than the user authorized.
2. **Malicious tool-output injection in AP automation** — a GenAI-crafted invoice/PDF with a swapped IBAN/beneficiary is fed to an invoice-paying agent, echoing FinCEN's 2024 alert on deepfake-enabled fraud targeting financial institutions and real 2025–2026 "AI-drafted invoice" fraud-as-a-service reporting.
3. **Agent-to-agent social engineering** — an attacker-controlled agent negotiates with a merchant checkout agent, exploiting the fact that the paying agent cannot verify whether it is talking to a human-authorized counterparty.

**Track B — Deepfake-Enabled Onboarding & Step-Up Auth Fraud (grounding / familiar track)**
Cites hard, citable 2026 numbers directly: 495% projected surge in deepfake identity fraud (Shufti Identity Fraud Index 2026); synthetic faces were 42.3% of 2025 deepfake fraud and projected to grow ~73% in 2026; injection attacks (virtual-camera feeding fake video into liveness checks) up 40% YoY (Entrust 2026 Identity Fraud Report); deepfake selfie attempts up 58% in one year; humans distinguish real vs. cloned voices correctly only 37.5–62.5% of the time across recent trials.
1. Voice-clone vishing against an OTP/step-up-authorization flow.
2. Synthetic-face injection at onboarding liveness check (virtual-camera attack pattern, per ID.me's 2026 Identity Fraud Landscape Report).

**Track C — Synthetic Identity + Agentic Onboarding Fraud (integration track)**
A "Frankenstein identity" (real stolen SSN/Aadhaar-style ID fragment + AI-generated face + AI-generated transaction history) opens an account, then uses an AI shopping agent to "age" the account with legitimate-looking purchases before cashing out — directly citing the Sumsub/PwC 2026 finding that fraud rings now *combine* synthetic identity, deepfakes, and agent automation in a single coordinated attack chain rather than using one technique in isolation. This track is what proves your system isn't three disconnected toys — it's a payments fraud *system* that models how real 2026 fraud actually chains together.

### 1.3 Why this specific combination wins Round 1 and the final

- **Round 1 (usually a written/video submission or short pitch)** is won by *clarity + credibility*: a one-line differentiated thesis ("we defend AI payment agents"), backed by citable numbers, with a clean architecture diagram. Judges skimming 50+ submissions reward the team that is instantly legible and instantly different from the pack.
- **The final** is won by the live demo. Judges in payments security have all seen a static confusion matrix — they have not seen an attack succeed, get logged, retrain a defense, and fail on the second attempt, live, with the AgentDojo-style success/refusal trace visible on screen.

---

## PART 2 — RESEARCH FOUNDATION (what to cite, and where it comes from)

Use these citations across the deck, the one-pager, and (critically) in Q&A — judges will test whether you actually understand the space or just skimmed it.

### 2.1 Threat landscape (industry reports — cite for "why now")
| Source | Fact to cite |
|---|---|
| Shufti Identity Fraud Index 2026 | 495% projected surge in deepfake-powered identity fraud in 2026; synthetic faces = 42.3% of 2025 deepfake fraud, +73% projected growth |
| Entrust 2026 Identity Fraud Report | Injection attacks (virtual camera → liveness check) up 40% YoY; deepfake selfies up 58% YoY; deepfakes = 1 in 5 biometric fraud attempts |
| Sumsub 2026 Fraud Trends / Identity Fraud Trends | Advanced/coordinated fraud attempts nearly tripled 2024→2025 (10%→28%); fraud rings now chain synthetic identity + deepfake + device spoofing + repeated variant attempts |
| FinCEN Alert FIN-2024-Alert004 | Official U.S. Treasury alert on deepfake media fraud schemes targeting financial institutions — regulatory-grade backing |
| FTC 2024 Identity Theft Data | 1.1M+ identity theft reports, $12.7B losses, +23% YoY |
| Deloitte Center for Financial Services | GenAI-enabled fraud losses projected to reach $40B in the U.S. by 2027 (from $12.3B in 2023) |
| MAS Singapore (2026 guidance) | Regulators now *require* financial institutions to demonstrate adversarial robustness of biometric identity-verification systems — frame SENTINEL as "MAS-style adversarial robustness testing, productized" |
| ID.me 2026 Identity Fraud Landscape Report | Documents the shift from presentation attacks (holding a photo to camera) to **injection attacks** (virtual camera feeding synthetic video directly into the pipeline) — this is the exact attack pattern your Track B detector should target |

### 2.2 Academic / technical foundation (cite for credibility on the build)

**Agentic AI security (Track A — your novelty):**
- Debenedetti et al., *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents*, NeurIPS 2024 — **the benchmark your Track A red team should structurally mirror** (environment + tools + user task + injection task + task suite).
- Greshake et al., *Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*, 2023 — foundational paper defining indirect prompt injection, the mechanism behind your Track A attacks.
- Debenedetti et al., *Defeating Prompt Injections by Design* (CaMeL), 2025 — control-flow/data-flow separation defense; solves 67% of AgentDojo tasks with *provable* security properties rather than probabilistic ones. **Cite this as the design philosophy behind your strictest defense layer** (structural separation of untrusted tool output from agent instructions), even if you implement a lighter version given the 11-day timeline.
- Chennabasappa et al. (Meta), *LlamaFirewall: An Open Source Guardrail System for Building Secure AI Agents*, 2025 — three-layer guardrail (PromptGuard 2 classifier + AlignmentCheck chain-of-thought auditor + CodeShield); **this is your reference architecture for the Track A defense stack.**
- ProtectAI, *DeBERTa-v3-base fine-tuned for prompt injection detection* (HuggingFace, v1/v2) — a small, fast, open-weights classifier you can realistically fine-tune/deploy in 11 days as your first detection layer.
- "Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents," 2026 — **important honesty note for your "limitations" slide**: even state-of-the-art defenses (CaMeL, Progent, FIDES) that claim near-elimination of attacks on static benchmarks can be degraded by adaptive, iterative attackers (one study cut Progent's defense from 25.8% down to 4.2% attack success, but flags that adaptive red-teaming is the only way to trust that number). **This is exactly what your red-team/adapt loop demonstrates you understand — cite it as validation of your methodology, not just your results.**

**Fraud/transaction detection (Track B/C — your defense core):**
- Multiple 2025–2026 papers (heterogeneous GNN with graph attention, TS-GNN, LayerWeighted-GCN) converge on one finding: **Graph Neural Networks outperform XGBoost/tabular ML by 12–25% AUROC** on relational fraud (fraud rings, mule networks, shared devices/IPs) because they model *relationships between transactions*, not just row-level features. **This is your technical differentiator on the transaction-scoring side** — most hackathon teams will submit a plain XGBoost/Random Forest model; a graph-based model (GraphSAGE/GAT on a transaction-entity graph) is both more defensible academically and directly citable to Mastercard's own known interest in network-based fraud detection (Mastercard acquired Brighterion and integrates behavioral/graph signals in its Decision Intelligence platform — mention this as the direction you're aligned with, not competing against).
- IEEE-CIS Fraud Detection dataset (590,540 transactions, 434 features, ~3.5% fraud rate) and PaySim (synthetic mobile-money simulator) — your two base datasets; both are standard, well-documented, and instantly recognizable to judges, which matters for credibility.

**Deepfake/voice detection (Track B):**
- ASVspoof 5 (2026) — the current standard benchmark/dataset for synthetic/spoofed speech detection; use ASVspoof-derived features (or a lightweight pretrained detector) rather than building a detector from scratch.
- RawNet2 (Tak et al., ICASSP 2021) and wav2vec2.0-based spoofing countermeasures (Tak et al., 2022) — realistic, pretrained-weight-available architectures for your audio deepfake detector; frame your detector as "wav2vec2-embedding + lightweight classifier head," which is buildable in days, not a from-scratch model.
- Barrington, Cooper & Farid, *People Are Poorly Equipped to Detect AI-Powered Voice Clones*, Scientific Reports 2025 — cite for the human-vs-model comparison stat in your deck ("humans get this wrong more than half the time; our detector doesn't have to be perfect, just better than the status quo").

### 2.3 Existing tools you should build *on top of*, not reinvent
| Tool | What it gives you | Use it for |
|---|---|---|
| **LlamaFirewall / PromptGuard 2** (Meta, open source) | Pretrained jailbreak/injection classifier | First-layer, fast input scanner for Track A |
| **ProtectAI deberta-v3-base-prompt-injection-v2** (HuggingFace) | Small (184M param) fine-tuned injection classifier | Fine-tune further on your agentic-payments-specific injection payloads |
| **LLM Guard** (open source, self-hosted) | 15 input / 20 output scanners incl. PII, injection, toxicity | Rapid baseline guardrail layer while you build your custom classifier |
| **garak** (NVIDIA/open source LLM red-teaming framework) | Automated LLM vulnerability probing | Use for Person A's red-team payload generation/QA, not just manual payloads |
| **AgentDojo repo (ETH Zurich, open source)** | Reference environment/tool/task harness | Fork the *structure*, not the exact tasks — rebuild tasks around payments (checkout tool, invoice-pay tool, refund tool) instead of email/calendar |
| **NetworkX / PyTorch Geometric** | Graph construction + GNN layers (GraphSAGE, GAT) | Track B/C transaction risk model |
| **SHAP** | Model explainability | Analyst-facing "why flagged" view |
| **A pretrained wav2vec2 spoofing checkpoint (e.g. from ASVspoof baseline repos)** | Audio feature extractor for deepfake detection | Track B audio detector backbone |

**Do not build a prompt-injection classifier, a GNN, or an audio-spoofing detector completely from scratch in 11 days — fine-tune/wrap the above.** Judges reward *system design and integration* far more than reinventing a wheel that already has open, citable, state-of-the-art building blocks. Your novelty is the *system* (closed-loop red/blue for agentic payments) and the *dataset/scenario* (payments-specific), not the underlying ML architecture.

---

## PART 3 — SYSTEM ARCHITECTURE

```
                         ┌────────────────────────────────────────────┐
                         │              ORCHESTRATOR (C)                │
                         │  runs N-round adversarial campaigns,         │
                         │  logs everything, triggers retraining,       │
                         │  serves the live dashboard                   │
                         └───────────────┬──────────────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                                                  ▼
┌───────────────────────────────┐                          ┌───────────────────────────────┐
│   RED TEAM  (Person A)         │                          │   BLUE TEAM  (Person B)         │
│                                 │   attack_event JSON      │                                  │
│ Track A: Agentic Payment Attack│ ────────────────────────▶│ Layer 1 — Fast filters           │
│  • mock shopping agent          │                          │   (regex/heuristics, LlamaGuard/  │
│  • mock invoice-pay agent       │                          │    LLM Guard input scanners)      │
│  • injection payload library    │                          │ Layer 2 — Injection classifier    │
│    (direct, indirect, multi-    │                          │   (fine-tuned DeBERTa-v3 on       │
│    turn drip, cross-agent)      │                          │    payments-specific payloads)    │
│  • garak-driven auto-payload    │                          │ Layer 3 — Agent alignment check   │
│    generation                   │                          │   (LLM-as-judge: does agent's     │
│                                 │                          │    reasoning trace match user's    │
│ Track B: Deepfake Vishing       │                          │    original authorized intent?)   │
│  • cloned-voice OTP-bypass      │                          │ Layer 4 — Transaction risk model  │
│    scripts (consenting team     │                          │   (GraphSAGE/GAT on txn-entity    │
│    voices ONLY — see ethics)    │                          │    graph: IEEE-CIS + PaySim +     │
│  • synthetic-face liveness-     │                          │    synthetic agentic-txn fields)   │
│    injection simulation         │                          │ Layer 5 — Audio/video deepfake    │
│                                 │                          │   detector (wav2vec2 embedding +   │
│ Track C: Synthetic ID + Agent   │                          │    classifier head, ASVspoof-      │
│  chained account-aging attack   │                          │    style features)                │
│                                 │                          │ Fusion — combine all layer scores  │
│ Orchestrator: fires N variants, │                          │   into one calibrated risk score   │
│  logs pass/fail per attack      │                          │   + SHAP explanation               │
└───────────────┬─────────────────┘                          └───────────────┬───────────────────┘
                │                                                              │
                │        successful-attack logs feed back in ─────────────────┘
                │        (adaptive retraining: new evasions become new
                │         training examples for Layers 2–4, next round
                │         red team must find NEW evasions — this is the
                └────────▶ round-trip that wins the demo)
                                         │
                                         ▼
                         ┌────────────────────────────────┐
                         │   ANALYST / METRICS DASHBOARD (C) │
                         │  attack success rate per round ↓  │
                         │  precision/recall/F1, FP rate      │
                         │  $ notional blocked                │
                         │  per-transaction latency            │
                         │  "why flagged" analyst trace view   │
                         └────────────────────────────────┘
```

### Key design decisions and why
1. **Layered defense, not one model.** Mirrors LlamaFirewall's proven architecture (fast filter → classifier → reasoning audit → downstream risk model) — defensible in Q&A because it's not a single point of failure, and it's exactly the direction the cited literature has converged on.
2. **Graph-based transaction scoring, not plain tabular ML.** Directly cites 12–25% AUROC improvement over XGBoost from the 2025–2026 GNN fraud-detection literature; this is your single strongest "we did real research" signal for the Mastercard-specific judges, since network/relational fraud detection is core to how card networks actually operate.
3. **Closed adversarial loop with logged rounds.** This is what separates you from every static "here's our F1 score" submission — the system visibly gets better because it was attacked.
4. **Explainability is a first-class output, not an afterthought.** Payments-security judges will ask "what does an analyst actually see" — have a real answer.
5. **Fusion layer with calibrated score, not independent thresholds.** Shows you understand that in production these signals must combine into one decision (approve / step-up / decline / hold-for-review), which is how real issuer risk engines work.

---

## PART 4 — TECH STACK (decided, so nobody wastes Day 1 debating)

| Layer | Choice | Why |
|---|---|---|
| Agent framework (red team mock agents) | Python + OpenAI/Anthropic function-calling / tool-use API (whichever the team has API credits for) | Fastest path to a realistic tool-using agent; matches how AgentDojo and real agentic-commerce systems are structured |
| Red-team payload generation | Manual payload library + **garak** for automated variant generation | garak gives you breadth (dozens of variants) without dozens of hours of manual writing |
| Injection/jailbreak classifier | **ProtectAI deberta-v3-base-prompt-injection-v2**, fine-tuned further | Open weights, small enough to fine-tune in a day on a single GPU/Colab, directly citable |
| Alignment/reasoning-audit layer | LLM-as-judge prompt (GPT-4.1/Claude via API) inspecting agent's chain-of-thought vs. original user instruction | Mirrors LlamaFirewall's AlignmentCheck design without needing to build a custom auditor model |
| Transaction risk model | **PyTorch Geometric** — GraphSAGE or GAT on a transaction-entity graph (nodes: card/account, merchant, device; edges: transactions) | Matches the 2025–2026 literature's best-performing approach; PyG has mature, well-documented layers so this is buildable in days |
| Baseline comparison model | XGBoost on the same features (flat, no graph) | You NEED this — "GNN beats XGBoost by X% AUROC on our data" is your money statistic, and you can't claim it without the baseline |
| Base datasets | **IEEE-CIS Fraud Detection** (Kaggle) + **PaySim** (Kaggle) | Standard, judge-recognizable, well-documented; augment with synthetic `agent_id`, `tool_call_trace`, `consent_token`, `injection_score` fields for the agentic-fraud scenario |
| Audio deepfake detector | Pretrained **wav2vec2** embeddings + lightweight classifier head, evaluated ASVspoof-style | Buildable without training a spoofing model from scratch; cite ASVspoof 5 / RawNet2 lineage |
| Synthetic voice generation (red team, own voices only) | Any accessible open TTS voice-cloning tool, used **only** on consenting team members' own voices for the demo | Keeps you fully within ethical bounds while still producing a real, working demo clip |
| Explainability | **SHAP** for the tabular/graph model; natural-language rationale from the LLM-judge layer for Track A | Standard, credible, fast to wire in |
| Orchestration / backend | Python (FastAPI) service tying red → blue → dashboard together, with a simple event log (SQLite or just JSON-lines for hackathon scope) | No need for Kafka/production infra in 11 days — a clean FastAPI + JSONL event log demos perfectly and is honest about being a prototype |
| Dashboard | React (or a fast Streamlit app if the team is short on frontend time) showing live round metrics | Streamlit is the pragmatic choice if Person C is stretched thin — don't over-invest frontend polish over the actual round-trip working |
| Repo/infra | GitHub monorepo, Python venv/poetry, `.env` for API keys, GitHub Actions for basic CI (lint + smoke test) | Keeps things simple and demonstrably professional without eating build time |

---

## PART 5 — REPOSITORY STRUCTURE

Create this exact structure before sending the plan to the team. Empty folders should get a `.gitkeep` or a stub file so the structure is visible in the initial commit.

```
sentinel-payment-defense/
│
├── README.md                          # Problem statement, architecture diagram, quickstart, team
├── LICENSE
├── .gitignore
├── .env.example                       # API key placeholders (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
├── requirements.txt                   # or pyproject.toml if using poetry
├── docker-compose.yml                 # optional: spins up backend + dashboard together
│
├── docs/
│   ├── research_citations.md          # Full citation list from Part 2, kept live/updated
│   ├── architecture.md                # Architecture diagram + design rationale (Part 3, exported)
│   ├── threat_model.md                # Formal description of Track A/B/C attacks, AgentDojo-style
│   ├── ethics_and_safety.md           # Consent/scope statement — READ before Day 1
│   ├── demo_script.md                 # Exact live-demo walkthrough, timed
│   └── pitch_deck/                    # Slides source (Markdown/Slidev, or .pptx export)
│
├── shared/
│   ├── schemas/
│   │   ├── attack_event.py            # Pydantic schema: the red→blue event contract (LOCK Day 2)
│   │   ├── transaction.py             # Pydantic schema: transaction record incl. agentic fields
│   │   └── verdict.py                 # Pydantic schema: blue-team decision + explanation
│   ├── config.py                      # Central config (model names, thresholds, API keys loader)
│   └── utils/
│       ├── logging.py
│       └── llm_client.py              # Thin wrapper around OpenAI/Anthropic calls, used by both teams
│
├── red_team/                          # PERSON A OWNS THIS DIRECTORY
│   ├── README.md                      # How to run each attack track independently
│   ├── track_a_agentic_payments/
│   │   ├── mock_shopping_agent.py     # Tool-using agent: browse, add_to_cart, checkout tools
│   │   ├── mock_invoice_agent.py      # Tool-using agent: read_invoice, verify_vendor, pay tools
│   │   ├── injection_payloads/
│   │   │   ├── direct/                # Direct injection payload .txt/.json files
│   │   │   ├── indirect/              # Payloads embedded in fake product pages / reviews
│   │   │   ├── multi_turn_drip/       # Slow-drip / split-payload attacks
│   │   │   └── agent_to_agent/        # Simulated malicious counterparty agent scripts
│   │   ├── garak_configs/             # garak probe configs for automated payload generation
│   │   └── run_track_a.py             # Entry point: fires payloads at mock agents, logs attack_event
│   ├── track_b_deepfake_vishing/
│   │   ├── voice_clone_gen.py         # Generates cloned-voice audio clips (TEAM VOICES ONLY)
│   │   ├── vishing_scripts/           # OTP-bypass call scripts (text)
│   │   ├── synthetic_face_liveness/   # Virtual-camera-injection simulation for liveness demo
│   │   └── run_track_b.py
│   ├── track_c_synthetic_identity_chain/
│   │   ├── synthetic_identity_gen.py  # Generates "Frankenstein identity" synthetic profiles
│   │   ├── account_aging_sim.py       # Simulates agent-driven "legitimate" purchase history
│   │   └── run_track_c.py
│   └── orchestrator/
│       └── campaign_runner.py         # Fires N variants across tracks, writes attack_event logs
│
├── blue_team/                         # PERSON B OWNS THIS DIRECTORY
│   ├── README.md
│   ├── layer1_fast_filters/
│   │   ├── regex_heuristics.py
│   │   └── llm_guard_wrapper.py       # Wraps LLM Guard input scanners
│   ├── layer2_injection_classifier/
│   │   ├── finetune_deberta.py        # Fine-tunes ProtectAI deberta-v3 on payments payloads
│   │   ├── inference.py
│   │   └── checkpoints/               # Saved model weights (gitignored if large; use Git LFS or link)
│   ├── layer3_alignment_check/
│   │   └── llm_judge.py               # LLM-as-judge: reasoning trace vs. user intent
│   ├── layer4_transaction_risk_model/
│   │   ├── graph_builder.py           # Builds transaction-entity graph from IEEE-CIS/PaySim + synthetic fields
│   │   ├── gnn_model.py               # GraphSAGE/GAT model (PyTorch Geometric)
│   │   ├── baseline_xgboost.py        # Flat XGBoost baseline for the comparison stat
│   │   ├── train.py
│   │   └── checkpoints/
│   ├── layer5_deepfake_detector/
│   │   ├── audio_feature_extractor.py # wav2vec2 embedding pipeline
│   │   ├── spoof_classifier.py        # Classifier head, ASVspoof-style eval
│   │   └── checkpoints/
│   ├── fusion/
│   │   ├── risk_fusion.py             # Combines all layer scores into one calibrated verdict
│   │   └── explainability.py          # SHAP + natural-language rationale generation
│   └── adaptive_retrain/
│       └── retrain_from_attack_log.py # Takes successful-attack logs → new training examples
│
├── orchestrator/                      # PERSON C OWNS THIS DIRECTORY (system integration)
│   ├── api/
│   │   ├── main.py                    # FastAPI app: /run_campaign, /get_metrics, /get_verdict
│   │   └── routes/
│   ├── event_log/
│   │   └── store.py                   # JSONL/SQLite event store for attack_event + verdict pairs
│   ├── campaign_manager.py            # Coordinates red→blue round-trip, triggers retraining
│   └── metrics/
│       └── compute_metrics.py         # Attack success rate, precision/recall, FP rate, $ blocked
│
├── dashboard/                         # PERSON C OWNS THIS DIRECTORY
│   ├── app.py                         # Streamlit app (pragmatic choice) OR
│   ├── frontend/                      #   React app if time allows
│   └── components/
│       ├── round_metrics_chart.py     # Attack-success-rate-over-rounds chart (THE money slide)
│       ├── analyst_view.py            # "Why flagged" transaction inspector
│       └── live_demo_view.py          # The live round-trip view used in the actual pitch
│
├── data/
│   ├── raw/                           # Downloaded IEEE-CIS, PaySim (gitignored, README with download instructions)
│   ├── synthetic/                     # Generated synthetic agentic-transaction fields, synthetic identities
│   └── processed/                     # Cleaned/joined datasets ready for model training
│
├── notebooks/
│   ├── 01_eda_ieee_cis_paysim.ipynb
│   ├── 02_gnn_vs_xgboost_benchmark.ipynb   # Produces your headline comparison stat
│   ├── 03_injection_classifier_eval.ipynb
│   └── 04_deepfake_detector_eval.ipynb
│
├── tests/
│   ├── test_schemas.py
│   ├── test_red_team_smoke.py
│   ├── test_blue_team_smoke.py
│   └── test_end_to_end_round_trip.py  # THE critical test — does attack→detect→retrain→re-attack actually run?
│
└── .github/
    └── workflows/
        └── ci.yml                     # Lint + smoke tests on push
```

**Why this structure works:** the `shared/schemas/` contract is what lets Person A and Person B build in parallel without collision — as long as both sides honor `attack_event.py` and `verdict.py`, integration on Day 7 is a matter of wiring, not rebuilding. This is the single highest-leverage decision in the whole plan; get it right on Day 2 and everything after it moves fast.

---

## PART 6 — EXACT PER-PERSON ROLES, DAY BY DAY

Each person's section below is written to be handed to that individual directly — it tells them exactly what files they own, what "done" looks like each day, and what they hand off to whom.

---

### PERSON A — Red Team Lead (Attack Simulation)
**Owns:** `red_team/` entirely. **Reads:** `shared/schemas/attack_event.py` (must conform to it — do not invent your own format).

| Day | Task | Deliverable ("done" = ) |
|---|---|---|
| 1 | Read AgentDojo paper + Greshake et al. indirect injection paper. Map out Track A attack taxonomy: list 15–20 concrete payload ideas across direct injection, indirect (embedded in tool output), multi-turn drip, agent-to-agent. | A written taxonomy doc in `docs/threat_model.md` (co-owned with C) |
| 2 | Agree on `attack_event.py` schema with B and C. Set up mock shopping agent (`mock_shopping_agent.py`) with 3 tools: `browse_product`, `add_to_cart`, `checkout`. Draft first 5 injection payloads (indirect, embedded in fake product descriptions). | Mock agent runs end-to-end on a clean (non-attacked) flow |
| 3 | Get 5 injection attacks fooling the mock agent (agent approves something it shouldn't — wrong amount, wrong address, unauthorized "fee"). Log every attempt as `attack_event` JSON. | 5/5 payloads produce a logged attack_event with pass/fail |
| 4 | Expand to 10–12 payload variants. Build `mock_invoice_agent.py` (tools: `read_invoice`, `verify_vendor`, `pay`) and 3–4 synthetic-invoice IBAN-swap payloads for Track C groundwork. Stand up `garak_configs/` for automated variant generation. | 10+ Track A payloads logged; invoice agent runs a clean flow |
| 5 | Build Track B: voice-clone vishing script generation (`voice_clone_gen.py`, **team members' own voices only**) — 3–4 OTP-bypass call scripts. Log attempts against a mock step-up-auth flow (build a trivial mock OTP endpoint if B hasn't supplied one yet). | 3–4 vishing attack clips + transcripts, logged |
| 6 | **Adversarial hardening round.** Take B's Day-5 classifier and actively try to evade it: paraphrase injections, split payloads across turns, use indirect pronoun references ("do what the last message said"), embed instructions in a fake system-looking tag. Log every evasion attempt, successful or not. | A written evasion report + new `attack_event` logs feeding B's retrain step |
| 7 | Full integration day with B. Run Track A + Track B attacks back-to-back through the full pipeline (via C's orchestrator). Fix any schema/format bugs on your side. | 3 full rounds run cleanly end-to-end, no crashes |
| 8 | Build Track C: `synthetic_identity_gen.py` (Frankenstein identity generator) + `account_aging_sim.py` (simulates an agent making a string of "legitimate-looking" purchases to age a synthetic account). Add 3–5 multi-turn slow-drip and cross-agent-handoff edge cases to Track A. | Track C runs one full synthetic-identity-to-cashout scenario end-to-end |
| 9 | **Freeze new attacks.** Run the final, clean benchmark campaign: fire all payloads across all 3 tracks (should be 25–35 total distinct attack variants) through the full pipeline, 3 adaptation rounds, save all logs for C's final numbers. | Final campaign log file(s) handed to C |
| 10 | Full dry-run rehearsals with the team. Know your attack taxonomy cold — you WILL be asked "what happens if the attacker does X" live. Prepare 2–3 answers for attacks you tried that DIDN'T work (this shows depth). | Can explain any attack in the repo in under 60 seconds |
| 11 | Buffer. Bug fixes only. Support the pitch — you speak to the "Identify" and "Generate" parts of the brief. | — |

**A's single most important deliverable:** by Day 6, prove that when the defense adapts, you can still find *new* evasions — this is what makes the round-trip demo credible instead of scripted.

---

### PERSON B — Blue Team Lead (Detection & Defense)
**Owns:** `blue_team/` entirely. **Reads:** `shared/schemas/attack_event.py`, writes `shared/schemas/verdict.py` outputs.

| Day | Task | Deliverable |
|---|---|---|
| 1 | Read LlamaFirewall paper (layered architecture) + the GNN-vs-XGBoost survey findings. Decide final layer architecture (5 layers per Part 3). Pick base datasets (IEEE-CIS + PaySim) and download. | Architecture decision documented in `docs/architecture.md` |
| 2 | Agree on schemas with A and C. Stand up `layer1_fast_filters/` using LLM Guard's input scanners as a fast baseline (this gets you a working, if crude, defense on Day 2 — huge for morale and for having *something* to demo early). Load and clean IEEE-CIS + PaySim into `data/processed/`. | Layer 1 flags at least A's Day-1 payloads at >0% catch rate (baseline to beat) |
| 3 | Build `layer2_injection_classifier/`: pull ProtectAI's deberta-v3-base-prompt-injection-v2, run it as-is first (zero-shot on A's payloads), note the gap, then start fine-tuning on payments-specific payloads as A produces them. | Zero-shot classifier baseline number recorded; fine-tuning pipeline running |
| 4 | Wire Layer 1 + Layer 2 in front of A's mock shopping agent (real integration, not just offline scoring). Start `layer4_transaction_risk_model/`: build `graph_builder.py` (transaction-entity graph: card/account, merchant, device nodes) on IEEE-CIS. | Layer 1+2 actively blocking/flagging live attack attempts from A |
| 5 | Train baseline `baseline_xgboost.py` on IEEE-CIS (flat features) — get a real AUROC number. Start `gnn_model.py` (GraphSAGE via PyTorch Geometric) on the same data. Build `layer5_deepfake_detector/audio_feature_extractor.py` using pretrained wav2vec2. | XGBoost baseline AUROC recorded; GNN training running |
| 6 | Finish GNN training, compare AUROC to XGBoost baseline (this is your headline stat — expect and report the real number, don't force it to match the literature's 12-25% if your data doesn't show that; report what you actually get, honestly). Build `spoof_classifier.py` head on top of wav2vec2 embeddings, evaluate against A's Day-5 voice clips. Patch Layer 2 against A's evasion report from today. | GNN vs XGBoost comparison number; audio detector catching some fraction of A's clips; Layer 2 v2 deployed |
| 7 | Full integration day with A. Build `layer3_alignment_check/llm_judge.py` (LLM-as-judge comparing agent's tool-call trace to original user instruction). Build `fusion/risk_fusion.py` to combine all 5 layers into one calibrated score + decision (approve/step-up/decline/review). | All 5 layers wired into one fusion output via C's orchestrator |
| 8 | Build `adaptive_retrain/retrain_from_attack_log.py` — takes yesterday's/today's successful-attack logs from A and appends them as hard negatives to Layer 2's training set; retrain. Stress-test false positives: run 20–30 of A's/your own "legitimate" agentic transactions through the full pipeline and confirm they pass cleanly. | Retrain script runs on real attack logs and measurably reduces attack success in a second pass; FP rate on legitimate transactions reported and low |
| 9 | **Freeze new features.** Run the final benchmark alongside A's Day-9 campaign — this is where your real, final precision/recall/F1/FP-rate/latency numbers come from. Build `explainability.py` (SHAP for the GNN/XGBoost, natural-language rationale for the LLM-judge layer). | Final metrics + explainability view ready, numbers handed to C |
| 10 | Full dry-run rehearsals. Know your thresholds and trade-offs cold — "what's your false-positive cost" is a guaranteed judge question; have the real number and be ready to explain the precision/recall trade-off honestly. | Can defend every number in the deck under questioning |
| 11 | Buffer. Bug fixes only. Support the pitch — you speak to the "Defend" part of the brief and the technical architecture. | — |

**B's single most important deliverable:** an honest, real GNN-vs-XGBoost comparison number from your own data (Day 6), and a real before/after attack-success-rate number from the adaptive retrain (Day 8–9). Do not fabricate or round these up — a judge who catches an inflated number in Q&A does more damage than a modest, defensible number ever could.

---

### PERSON C — Systems, Research & Narrative Lead
**Owns:** `orchestrator/`, `dashboard/`, `docs/`, root-level repo hygiene. **Floats to unblock A or B whenever either is stuck** — this role has slack built in deliberately because integration and storytelling are what most hackathon teams under-invest in until it's too late.

| Day | Task | Deliverable |
|---|---|---|
| 1 | Build citations doc (`docs/research_citations.md`) from Part 2 of this plan — verify every link resolves and every number is quoted correctly (do not trust secondhand summaries; check primary sources where possible). Set up the GitHub repo with the exact structure in Part 5, `.gitignore`, `requirements.txt`, `README.md` skeleton, branch protection. Write `docs/ethics_and_safety.md` and get both teammates to explicitly agree to it before any voice-clone/synthetic-identity work starts. | Repo live, structured, both teammates onboarded; ethics doc acknowledged by all 3 |
| 2 | Lead the schema design session with A and B (this is the single highest-leverage meeting of the whole project — do not skip or rush it). Finalize and commit `shared/schemas/attack_event.py`, `transaction.py`, `verdict.py`. Start `docs/architecture.md` with the diagram from Part 3. | Schemas committed and both A and B have confirmed they can build against them |
| 3 | Build `orchestrator/api/main.py` skeleton (FastAPI, even if endpoints are stubs) and `orchestrator/event_log/store.py` (JSONL event store). Start deck skeleton: title, problem (with citations), why-now, architecture. | API skeleton runs locally; deck has a real structure, not just bullet placeholders |
| 4 | Build `campaign_manager.py` — the actual code that takes A's attack_event, routes it through B's (currently partial) defense stack, and logs a verdict. Even with only Layer 1+2 live, get ONE real round-trip working today — this de-risks the whole demo. | One real, working attack→detect→log round-trip, howeverthin |
| 5 | Build first version of `dashboard/app.py` (Streamlit, pragmatic) — even with placeholder/fake numbers, get the *shape* of the "attack success rate over rounds" chart and the analyst "why flagged" view built now, not on Day 9. **Midpoint checkpoint with A and B today:** does anything end-to-end actually work? If not, this is the day to sound the alarm, not Day 9. | Dashboard shell renders; midpoint checkpoint run with the team, blockers identified and triaged |
| 6 | Wire the dashboard to real (if partial) data from `orchestrator/event_log/store.py`. Continue deck: add the architecture diagram, the attack taxonomy (from A), the defense-layer breakdown (from B). | Dashboard shows real, live-updating numbers from at least one attack track |
| 7 | Full integration day (with A and B). This is the day the whole loop needs to work at least once, ugly is fine. Fix integration bugs as they surface — you're the person who understands both sides of the contract, so most Day-7 bugs will route through you. | Attack → detect → retrain → re-attack loop demonstrably runs, at least once, on real data |
| 8 | Build `dashboard/components/live_demo_view.py` — the exact screen you'll show live during the pitch. Write `docs/demo_script.md`: the precise, timed sequence of what happens on screen during the live demo, including a scripted fallback if an API call fails live. Record a backup demo video today (assume live demos fail at venues). | Backup demo video recorded and saved; live demo view built |
| 9 | Collect final numbers from A (attack campaign log) and B (precision/recall/AUROC/FP-rate) and put them in the dashboard and the deck. Finalize deck: Problem → Why agentic commerce is the frontier → Architecture → Live round-trip demo → Numbers → 90-day production roadmap → Limitations & ethics. Write the "known limitations" slide explicitly (cite the adaptive-evaluation paper's finding on static-benchmark overconfidence — pre-empting this question is a strength, not a weakness). | Deck is final-draft complete with real numbers, not placeholders |
| 10 | Run full dry-run rehearsals (at least 3 timed run-throughs). Prepare the 5 standard judge questions (see Part 7) with a designated primary answerer for each, but make sure ALL THREE can answer all five reasonably. Confirm backup video plays correctly on the actual venue laptop/setup if possible. | Team has done 3+ full timed rehearsals; backup video verified to play |
| 11 | Submit all deliverables early (repo, deck, video) well before deadline — do not touch the submission portal at the last minute. Final light bug fixes only. | Submitted, with time to spare |

**C's single most important deliverable:** the Day 7 working round-trip and the Day 8 backup video. If either of those doesn't exist, the team is one wifi hiccup away from a broken pitch — protect these two things above all else, including above deck polish.

---

## PART 7 — JUDGE Q&A PREPARATION (assign a primary + backup answerer for each)

1. **"How does this generalize beyond your two/three specific attacks?"** → Primary: C. Answer: layered architecture is attack-agnostic (fast filter → classifier → reasoning audit → risk model → modality-specific detectors); Track B/C demonstrate the same pipeline catching a *structurally different* attack family, which is the generalization proof.
2. **"What's your false-positive cost in production?"** → Primary: B. Have the real number from your Day-8 FP stress test ready, and be honest about the precision/recall trade-off you chose and why.
3. **"How is this different from Mastercard's existing Decision Intelligence / other fraud tools?"** → Primary: C, backup B. Answer: not competing with network-level fraud scoring — SENTINEL targets the *agentic payment layer*, a new surface those systems weren't built for, and is designed as a complementary signal (the fusion layer is exactly where it would plug into an existing risk engine).
4. **"What's your data/privacy story?"** → Primary: C. Answer: synthetic and public benchmark data only (IEEE-CIS, PaySim), no real PII/cardholder data anywhere; voice/face material is team-consented only.
5. **"What would break this defense?"** → Primary: A. This is your chance to show intellectual honesty — name a real limitation (e.g., a sufficiently novel injection phrasing your classifier hasn't seen, or an adaptive attacker per the June 2026 out-of-band-defenses paper) and say what you'd build next to address it. Judges trust teams more, not less, for naming real limitations.
6. **"Why should we believe your GNN number / your attack-success numbers are real and not cherry-picked?"** → Primary: B. Answer: show the raw campaign log / notebook (`02_gnn_vs_xgboost_benchmark.ipynb`), same train/test split for both models, numbers are in the repo, not just the slide.

---

## PART 8 — WHAT TO SEND THE TEAM, IN ORDER

1. This document.
2. The repository, scaffolded exactly per Part 5 (empty files/folders with a one-line docstring each stating their purpose — this alone communicates the plan faster than any meeting).
3. `docs/ethics_and_safety.md` — get explicit sign-off from both teammates before Day 1 work starts, especially before any voice-cloning work.
4. A shared calendar hold for the Day 2 schema-lock session, the Day 5 midpoint checkpoint, the Day 7 integration day, and the Day 9 numbers-freeze — these four moments are where the plan lives or dies; protect them explicitly when you send this.
