# SENTINEL — Research Citations

## Purpose

This document records the research and industry sources that inform SENTINEL's threat model, system architecture, datasets, and evaluation methodology.

Claims in the project should be attributed to the appropriate source below rather than presented as unsupported facts.

---

## 1. Agentic AI Security

### AgentDojo

**Citation**

Debenedetti, E., Zhang, J., Balunović, M., Beurer-Kellner, L., Fischer, M., & Tramèr, F. (2024). *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents*. Advances in Neural Information Processing Systems (NeurIPS 2024).

**Supports**

* Evaluation of tool-using LLM agents operating in realistic environments.
* Indirect prompt-injection evaluation.
* AgentDojo contains 97 realistic tasks and 629 security test cases.

**Use in SENTINEL**

AgentDojo provides the structural inspiration for SENTINEL's Track A environment: user tasks, tool-using agents, untrusted external content, attack tasks, and measurable attack success.

**Primary source**

https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html

---

### Indirect Prompt Injection

**Citation**

Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., & Fritz, M. (2023). *Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*. Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security.

**Supports**

* Definition and threat model of indirect prompt injection.
* Attacker instructions can be embedded inside externally retrieved content.
* LLM-integrated applications can be manipulated through untrusted data.

**Use in SENTINEL**

Forms the foundation for Track A attacks in which malicious instructions are embedded in merchant pages, reviews, invoices, or other tool outputs rather than directly supplied by the user.

**Primary source**

https://arxiv.org/abs/2302.12173

---

### CaMeL — Defeating Prompt Injections by Design

**Citation**

Debenedetti, E., et al. (2025). *Defeating Prompt Injections by Design*. arXiv preprint.

**Supports**

* Structural defenses against prompt injection.
* Separation of control flow and data flow.
* Capability-based restrictions on tool execution.
* Evaluation on AgentDojo.

**Use in SENTINEL**

CaMeL informs the design philosophy of separating untrusted tool output from trusted instructions and limiting what an agent is allowed to execute.

**Important verified result**

The paper reports **77% of AgentDojo tasks solved with provable security** under its evaluated setting. This replaces the 67% figure appearing in an earlier version of the project plan.

**Primary source**

https://arxiv.org/abs/2503.18813

---

### LlamaFirewall

**Citation**

Meta. (2025). *LlamaFirewall: An Open Source Guardrail System for Building Secure AI Agents*.

**Supports**

A layered agent-security architecture including:

* PromptGuard 2 for prompt-injection/jailbreak detection.
* Agent Alignment Checks.
* CodeShield for insecure generated code.

**Use in SENTINEL**

SENTINEL's layered Track A defense is conceptually aligned with this approach:

1. Fast filtering.
2. Injection classification.
3. Agent alignment verification.
4. Downstream transaction risk analysis.
5. Modality-specific detection.

**Primary source**

https://arxiv.org/abs/2505.03574

---

## 2. Fraud Detection Datasets

### IEEE-CIS Fraud Detection

**Source**

IEEE Computational Intelligence Society Fraud Detection dataset, distributed through Kaggle.

**Characteristics**

The dataset contains transaction and identity information linked through `TransactionID` and uses `isFraud` as the binary fraud target.

The commonly used merged training data contains approximately 590,540 transactions and 434 features.

**Use in SENTINEL**

Used as the primary real-world-inspired benchmark for transaction fraud detection and for comparing:

* XGBoost baseline.
* Graph-based transaction modelling.

**Primary source**

https://www.kaggle.com/c/ieee-fraud-detection/data

---

### PaySim

**Citation**

Lopez-Rojas, E., Elmir, E., & Axelsson, S. (2016). *PaySim: A Financial Mobile Money Simulator for Fraud Detection*. Proceedings of the 28th European Modeling & Simulation Symposium.

**Supports**

* Synthetic financial transaction generation.
* Mobile-money fraud research.
* Controlled experimentation where real financial transaction data cannot be freely distributed.

**Use in SENTINEL**

PaySim provides a complementary synthetic financial dataset for transaction-risk experiments and controlled fraud scenarios.

**Primary source**

https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf

---

## 3. Synthetic / Spoofed Speech Detection

### ASVspoof 5

**Source**

ASVspoof 5 — Automatic Speaker Verification Spoofing and Countermeasures Challenge.

**Supports**

* Evaluation of spoofed and synthetic speech detection.
* Current benchmark resources for speech deepfake/spoofing countermeasures.
* Diverse spoofing attacks and speaker data.

**Use in SENTINEL**

ASVspoof-style data and evaluation methodology inform Track B's audio deepfake detection component.

SENTINEL will use pretrained speech representations rather than attempting to train a large spoofing model from scratch within the hackathon timeframe.

**Primary source**

https://www.asvspoof.org/

---

### wav2vec 2.0

**Citation**

Baevski, A., Zhou, H., Mohamed, A., & Auli, M. (2020). *wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations*. Advances in Neural Information Processing Systems.

**Supports**

* Self-supervised speech representation learning.
* Transferable speech embeddings from pretrained models.

**Use in SENTINEL**

wav2vec-style pretrained embeddings can serve as the feature-extraction backbone for the lightweight Track B spoof classifier.

**Primary source**

https://arxiv.org/abs/2006.11477

---

## 4. Financial Institution Deepfake Threats

### FinCEN Alert FIN-2024-Alert004

**Source**

Financial Crimes Enforcement Network (FinCEN). *Alert on Fraud Schemes Involving Deepfake Media Targeting Financial Institutions*.

**Supports**

* Deepfake media being used in financial fraud.
* Risks to financial institutions from manipulated or synthetic identity media.

**Use in SENTINEL**

Provides regulatory/financial-sector grounding for the deepfake component of SENTINEL and supports the premise that synthetic media represents a legitimate financial-security threat.

**Primary source**

https://www.fincen.gov/system/files/shared/FinCEN-Alert-DeepFakes-Alert508FINAL.pdf

---

## 5. Evaluation Methodology

### Adaptive Red Teaming

SENTINEL follows an adversarial evaluation methodology rather than relying only on a static benchmark.

The system records successful attacks and uses them as feedback for subsequent defensive adaptation. A later red-team round then attempts to discover new evasions.

**Why this matters**

A defense that performs well against a fixed attack set does not necessarily remain robust against an adaptive attacker. SENTINEL therefore evaluates:

* Attack success rate before adaptation.
* Attack success rate after adaptation.
* New evasions discovered by the red team.
* False positives on legitimate transactions.
* Detection latency.
* Per-layer and fused detection performance.

Any quantitative result produced by SENTINEL will be measured experimentally and recorded in the repository rather than assumed from published literature.

---

## 6. Claims We Will Verify Experimentally

The following should **not** be presented as predetermined results:

### GNN vs. XGBoost

The project plan proposes that graph-based transaction models may outperform flat tabular models because they represent relationships between entities.

However, SENTINEL will **not claim a fixed 12–25% AUROC improvement** before experimentation.

The project will train:

* XGBoost baseline.
* GraphSAGE/GAT model.

Both models will use an equivalent evaluation setup, and the actual measured results will be reported.

### Adaptive Defense Improvement

The project will not claim that adaptive retraining eliminates attacks.

Instead, we will measure whether successful attack examples incorporated into the defensive pipeline reduce attack success in subsequent rounds.

---

## 7. Dataset and Data-Safety Principle

SENTINEL uses:

* Public benchmark datasets.
* Synthetic transaction fields.
* Synthetic identities.
* Team-consented audio for demonstration purposes.

No real customer payment information, card numbers, bank credentials, or personally identifiable financial data should be introduced into the repository.

See `docs/ethics_and_safety.md` for the project's safety boundaries.
