# ARGUS

### Adversarial Defense for AI-Powered Payments

ARGUS is an end-to-end adversarial AI security platform designed to protect AI-powered payment agents from attacks that manipulate their instructions, behavior, authentication, or transactions.

Instead of relying on a single fraud detector, ARGUS continuously **attacks, detects, investigates, enforces, and learns**:

```text
Red Team Attack
      ↓
AI Payment Agent
      ↓
Five-Layer Defense
      ↓
Risk Fusion
      ↓
Security Agent
      ↓
Deterministic Enforcement
      ↓
Threat Learning
      ↺
```

The result is a defense-in-depth security architecture designed specifically for the emerging risks created when AI agents can access untrusted content, use tools, and initiate financial actions.

---

## Key Innovation

ARGUS combines several security capabilities into one closed-loop system:

* **Adversarial Red Teaming** — generates and executes attacks against AI payment workflows.
* **Five-Layer Blue Team Defense** — combines independent security signals rather than trusting one model.
* **Behavioral Alignment Verification** — checks whether the agent actually followed the user's authorized intent.
* **Transaction Risk Detection** — evaluates financial and behavioral transaction risk.
* **Deepfake Detection** — detects synthetic/spoofed audio used in authentication attacks.
* **Risk Fusion** — combines heterogeneous security signals into a unified verdict.
* **Agentic Security Investigation** — an LLM-based security investigator reasons over the evidence.
* **Deterministic Enforcement** — prevents the AI investigator from overriding critical security policies.
* **Adaptive Threat Learning** — converts confirmed attack outcomes into threat intelligence for future investigations.
* **Explainable Decisions** — exposes layer scores, evidence, reasons, and final decisions to analysts.

The central security principle is:

> **Use AI for contextual reasoning; use deterministic controls for security-critical enforcement.**

---

# Architecture

```text
                         USER
                           │
                           ▼
                  AI PAYMENT AGENT
                           │
                    Proposed Action
                           │
                           ▼
                     ATTACK EVENT
                           │
                           ▼
             ┌───────────────────────────┐
             │     FIVE-LAYER DEFENSE    │
             │                           │
             │ L1  Fast Security Filters │
             │ L2  Injection Classifier  │
             │ L3  Alignment Check       │
             │ L4  Transaction Risk      │
             │ L5  Deepfake Detection    │
             └─────────────┬─────────────┘
                           │
                           ▼
                    RISK FUSION
                           │
                           ▼
                  SECURITY VERDICT
                           │
                           ▼
                  SECURITY AGENT
                           │
                           ▼
              DETERMINISTIC POLICY
                           │
                ┌──────────┼──────────┐
                ▼          ▼          ▼
              ALLOW      REVIEW      BLOCK
                │          │          │
                └──────────┼──────────┘
                           ▼
                      EVENT STORE
                           │
                           ▼
                 ADAPTIVE LEARNING
                           │
                           └──────► Future investigations
```

---

# Blue Team

## Layer 1 — Fast Security Filters

A low-latency heuristic layer performs initial screening for obvious malicious patterns, including:

* Prompt-injection phrases
* Instruction overrides
* Suspicious security instructions
* Known manipulation patterns
* Rule-based anomalies

This layer provides inexpensive first-pass protection before more expensive analysis.

## Layer 2 — Prompt-Injection Classifier

Layer 2 uses a fine-tuned **DeBERTa-v3** prompt-injection classifier.

It analyzes potentially untrusted content such as:

* Direct prompt injections
* Indirect prompt injections
* Malicious merchant content
* Poisoned product descriptions
* Manipulated external instructions
* Payment-agent instruction hijacking

The trained model is included in the repository under:

```text
blue_team/layer2_injection_classifier/layer2_finetuned_v1/
```

## Layer 3 — Agent Alignment Check

Layer 3 uses an LLM-based alignment judge to determine whether the agent's behavior matches the user's authorized intent.

It evaluates:

```text
Original User Instruction
        +
Agent Reasoning / Context
        +
Tool Calls / Proposed Action
        ↓
Alignment Assessment
```

For example:

```text
User:
Pay the invoice for ₹5,000.

Agent:
Pays ₹50,000 to a different beneficiary.
```

The transaction may appear technically valid, but the agent has violated the user's intended authorization.

## Layer 4 — Transaction Risk

Layer 4 evaluates transaction-level fraud and risk signals.

The architecture supports relationship-aware fraud analysis involving:

```text
Account / Card
      │
      ├── Merchant
      ├── Device
      └── Transaction
```

The production inference path uses the available trained transaction-risk model and checkpoint:

```text
blue_team/layer4_transaction_risk_model/
```

The architecture is designed to support graph-based transaction analysis using PyTorch Geometric.

## Layer 5 — Deepfake Detection

Layer 5 analyzes audio for synthetic or spoofed speech that could be used in:

* Voice-based authentication attacks
* Vishing
* Step-up verification bypass
* AI-generated voice impersonation

The trained model is included under:

```text
blue_team/layer5_deepfake_detector/layer5_finetuned_v1/
```

---

# Risk Fusion

Each applicable defense layer produces security evidence.

ARGUS combines these signals into a unified risk assessment:

```text
L1 ─┐
L2 ─┤
L3 ─┤──► Risk Fusion ──► Final Verdict
L4 ─┤
L5 ─┘
```

The system supports:

* `APPROVE`
* `STEP-UP`
* `REVIEW`
* `DECLINE`

Strong individual security signals can trigger protective overrides rather than being diluted by safer signals from unrelated layers.

---

# Agentic Security Investigation

The Security Agent receives structured security evidence including:

* Original user instruction
* Untrusted content
* Agent context
* Tool calls
* Layer scores
* Layer flags
* Fusion score
* Fusion explanation
* Previously learned threat patterns

It produces a structured recommendation such as:

```json
{
  "recommendation": "block",
  "confidence": 0.94,
  "reason": "The proposed action conflicts with the user's authorized payment intent.",
  "evidence": [
    "Agent action differs from original instruction",
    "Transaction risk is elevated"
  ]
}
```

The Security Agent is **not** the final authority.

Its recommendation is passed through deterministic enforcement.

---

# Deterministic Enforcement

Security-critical decisions are protected by a deterministic policy layer.

```text
Security Evidence
       ↓
Security Agent
       ↓
Enforcement Policy
       ↓
ALLOW / REVIEW / BLOCK
```

The agent can investigate and explain an event, but it cannot arbitrarily override critical security controls.

This separation provides an important security boundary between:

**AI reasoning** and **financial enforcement**.

---

# Adaptive Threat Learning

ARGUS maintains a threat knowledge base based on confirmed attack outcomes.

```text
Attack
  ↓
Detection
  ↓
Security Verdict
  ↓
Outcome
  ↓
Threat Learning
  ↓
Threat Knowledge
  ↓
Future Security Investigation
```

The current implementation learns recurring attack patterns and makes them available to future Security Agent investigations.

The architecture can be extended to candidate-model promotion:

```text
New Attack Data
      ↓
Candidate Model
      ↓
Regression Testing
      ↓
Known + Unseen Attacks
      ↓
False-Positive Evaluation
      ↓
PROMOTE / REJECT
```

---

# Red Team

ARGUS evaluates its own defenses through three major attack surfaces.

## Track A — Agentic Payment Attacks

Targets AI agents that interact with payment workflows.

Attack categories include:

* Direct prompt injection
* Indirect prompt injection
* Malicious merchant content
* Malicious tool output
* Transaction manipulation
* Payment redirection
* Unauthorized address changes
* Agent-to-agent manipulation
* Multi-turn goal hijacking

Attack payloads are organized under:

```text
red_team/track_a_agentic_payments/
```

## Track B — Deepfake & Vishing

Targets authentication workflows using synthetic or manipulated identity signals.

Includes:

* Voice-clone attacks
* Vishing
* Fake verification
* OTP manipulation
* Urgency-based verification bypass
* Synthetic face/liveness scenarios

Located under:

```text
red_team/track_b_deepfake_vishing/
```

## Track C — Synthetic Identity

Models fraud chains involving synthetic identities and sequences of individually plausible actions.

```text
Synthetic Identity
       ↓
Account Activity
       ↓
Agent Interaction
       ↓
Fraudulent Transaction
```

Located under:

```text
red_team/track_c_synthetic_identity_chain/
```

---

# Technology Stack

| Area            | Technologies                          |
| --------------- | ------------------------------------- |
| Language        | Python                                |
| API             | FastAPI                               |
| Dashboard       | Streamlit                             |
| Validation      | Pydantic                              |
| Testing         | Pytest                                |
| Deep Learning   | PyTorch                               |
| NLP             | Hugging Face Transformers, DeBERTa-v3 |
| Audio           | wav2vec2                              |
| Fraud ML        | XGBoost                               |
| Graph ML        | PyTorch Geometric                     |
| Agentic AI      | LLM-based Security Agent              |
| LLM Inference   | Groq API                              |
| Data            | JSON / JSONL                          |
| Configuration   | `.env`                                |
| Infrastructure  | Docker Compose                        |
| Version Control | Git / GitHub                          |

---

# Repository Structure

```text
mastercard-ai-challenge/
│
├── README.md
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
│
├── blue_team/
│   ├── fusion/
│   ├── layer1_fast_filters/
│   ├── layer2_injection_classifier/
│   │   └── layer2_finetuned_v1/
│   ├── layer3_alignment_check/
│   ├── layer4_transaction_risk_model/
│   │   └── layer4_checkpoints/
│   └── layer5_deepfake_detector/
│       └── layer5_finetuned_v1/
│
├── red_team/
│   ├── orchestrator/
│   ├── track_a_agentic_payments/
│   ├── track_b_deepfake_vishing/
│   └── track_c_synthetic_identity_chain/
│
├── orchestrator/
│   ├── api/
│   ├── event_log/
│   ├── metrics/
│   ├── adaptive_learning/
│   ├── adaptive_learning.py
│   ├── campaign_manager.py
│   ├── defense_interface.py
│   ├── enforcement_policy.py
│   ├── real_defense_pipeline.py
│   ├── red_team_adapter.py
│   └── security_agent.py
│
├── shared/
│   └── schemas/
│
├── dashboard/
│   └── app.py
│
├── evaluation/
│   ├── benign_dataset_v1.json
│   └── run_benign_v1.py
│
├── data/
│   └── raw/
│
└── tests/
```

---

# Setup

## 1. Clone the repository

```bash
git clone <repository-url>
cd mastercard-ai-challenge
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create `.env` from the provided template:

```powershell
Copy-Item .env.example .env
```

Configure:

```env
# LLM provider
GROQ_API_KEY=your_groq_api_key

# Application
APP_ENV=development
LOG_LEVEL=INFO

# API
API_HOST=127.0.0.1
API_PORT=8000

# Detection thresholds
INJECTION_THRESHOLD=0.80
TRANSACTION_RISK_THRESHOLD=0.70
```

`GROQ_API_KEY` is required for LLM-based security investigation.

**Never commit `.env` or API credentials to Git.**

---

# Model Setup

The repository includes the trained model artifacts required by the implemented defense pipeline.

### Layer 2

```text
blue_team/layer2_injection_classifier/layer2_finetuned_v1/
```

Contains the fine-tuned DeBERTa model and tokenizer configuration.

### Layer 4

```text
blue_team/layer4_transaction_risk_model/layer4_checkpoints/
```

Contains the transaction-risk model and associated label encoders.

### Layer 5

```text
blue_team/layer5_deepfake_detector/layer5_finetuned_v1/
```

Contains the fine-tuned audio model and preprocessing configuration.

No additional training is required to run the supplied defense pipeline.

---

# Running ARGUS

## Start the API

From the repository root:

```powershell
python -m uvicorn orchestrator.api.main:app --host 127.0.0.1 --port 8000
```

The API is then available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Start the Dashboard

In a second terminal:

```powershell
streamlit run dashboard/app.py
```

The dashboard provides campaign-level and event-level security views.

---

# Running Red-Team Campaigns

## Track A

```powershell
python red_team/track_a_agentic_payments/run_track_a.py
```

## Track B

```powershell
python red_team/track_b_deepfake_vishing/run_track_b.py
```

## Track B Liveness Simulation

```powershell
python red_team/track_b_deepfake_vishing/synthetic_face_liveness/run_liveness_sim.py
```

## Track C

```powershell
python red_team/track_c_synthetic_identity_chain/run_track_c.py
```

Track C validation can be run with:

```powershell
python red_team/track_c_synthetic_identity_chain/validate_track_c.py
```

---

# Evaluation

ARGUS includes a benign evaluation set to measure whether security controls incorrectly flag legitimate activity.

Run:

```powershell
python evaluation/run_benign_v1.py
```

The dataset is located at:

```text
evaluation/benign_dataset_v1.json
```

The evaluation is intended to complement adversarial testing by measuring false-positive behavior.

---

# Testing

Run the complete automated regression suite:

```powershell
python -m pytest -q
```

Current validation:

```text
40 passed
8 warnings
0 failures
```

The warnings are dependency/environment compatibility warnings and do not represent failed project tests.

The test suite covers:

* API behavior
* Campaign management
* Security Agent behavior
* Authorization checks
* Risk fusion
* Deterministic enforcement
* Event storage
* Metrics
* Adaptive learning
* Security integration
* Security decision schemas

---

# Security Decision Flow

A complete event follows this general path:

```text
1. Red Team generates an attack
              ↓
2. Attack is executed against the payment-agent scenario
              ↓
3. AttackEvent is generated
              ↓
4. Five defense layers analyze the event
              ↓
5. Risk Fusion combines security evidence
              ↓
6. Security Agent investigates the event
              ↓
7. Deterministic policy enforces the result
              ↓
8. Event is recorded
              ↓
9. Attack outcome feeds adaptive learning
```

This creates a closed-loop adversarial security system rather than a static classifier.

---

# Explainability

For individual events, ARGUS exposes security evidence including:

* Final decision
* Fusion risk
* Attack-caught status
* Layer scores
* Layer flags
* Layer explanations
* Agent/tool information
* Investigation evidence
* Security Agent reasoning

This allows an analyst to answer:

> **Why did ARGUS make this decision?**

rather than receiving only an unexplained risk score.

---

# Evaluation Philosophy

ARGUS evaluates both **security effectiveness** and **operational behavior**.

Relevant metrics include:

* Attack Success Rate
* Attack Catch Rate
* Precision
* Recall
* F1
* False Positive Rate
* True Negative Rate
* Detection latency
* Per-layer performance
* Known vs. unseen attack performance
* Campaign-level performance

The project distinguishes between:

**Engineering validation**

and

**Research generalization**.

Passing the internal test suite demonstrates implementation correctness; it does not imply that every possible real-world attack will be detected.

---

# Security Philosophy

ARGUS follows several principles:

### Never trust a single detector

Different attack types produce different signals.

### Separate reasoning from enforcement

An LLM can investigate evidence without receiving unrestricted authority over financial actions.

### Treat external content as untrusted

Merchant pages, invoices, tool outputs, and external documents may contain instructions intended to manipulate an AI agent.

### Learn from failures

Missed attacks provide valuable information for improving future defenses.

### Validate before promotion

Future adaptive models should be evaluated against known attacks, unseen attacks, and benign hard negatives before deployment.

### Optimize for practical deployment

Security improvements must be balanced against latency, false positives, cost, and operational complexity.

---

# Responsible Use

ARGUS is a research and hackathon security prototype.

Red-team capabilities are intended for controlled security evaluation of authorized systems. Attack generation, voice synthesis, and other adversarial capabilities should only be used in environments where the operator has permission to perform security testing.

The system should not be treated as a production banking authorization control without additional security, compliance, monitoring, isolation, authentication, and operational safeguards.

---

# Limitations

Current limitations include:

* The internal attack library does not represent the full distribution of real-world attacks.
* External benchmark evaluation should be expanded before making broad generalization claims.
* LLM-based investigation can produce imperfect judgments.
* Adaptive learning currently focuses on threat-pattern knowledge rather than autonomous production model replacement.
* Graph-based fraud detection depends on sufficiently rich relationship data.
* Audio detection performance depends on the quality and distribution of evaluation audio.
* Production deployment would require significantly stronger infrastructure and governance.

ARGUS is therefore designed to **improve resilience against evolving attacks**, not to guarantee detection of every attack.

---

# Project Status

| Component                      | Status        |
| ------------------------------ | ------------- |
| Red Team attack infrastructure | Implemented   |
| Track A                        | Implemented   |
| Track B                        | Implemented   |
| Track C                        | Implemented   |
| Layer 1                        | Implemented   |
| Layer 2                        | Implemented   |
| Layer 3                        | Implemented   |
| Layer 4                        | Implemented   |
| Layer 5                        | Implemented   |
| Risk Fusion                    | Implemented   |
| Security Agent                 | Implemented   |
| Deterministic Enforcement      | Implemented   |
| Adaptive Threat Learning       | Implemented   |
| FastAPI backend                | Implemented   |
| Streamlit dashboard            | Implemented   |
| Benign evaluation              | Implemented   |
| Automated regression suite     | **40 passed** |

---

# Core Concept

ARGUS can be summarized in one loop:

```text
             ┌───────────────┐
             │     ATTACK    │
             └───────┬───────┘
                     ↓
             ┌───────────────┐
             │     DETECT    │
             └───────┬───────┘
                     ↓
             ┌───────────────┐
             │      FUSE     │
             └───────┬───────┘
                     ↓
             ┌───────────────┐
             │  INVESTIGATE  │
             └───────┬───────┘
                     ↓
             ┌───────────────┐
             │    ENFORCE    │
             └───────┬───────┘
                     ↓
             ┌───────────────┐
             │     LEARN     │
             └───────┬───────┘
                     │
                     └──────────► DEFEND BETTER
```

**ARGUS is built around a simple idea: don't wait for attackers to discover weaknesses in AI-powered payment agents—attack the system yourself, measure what the defense catches, enforce safe decisions, and use what was learned to make the next defense stronger.**