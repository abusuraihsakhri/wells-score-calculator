# WELLS Score Calculator

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Wells Score Calculator for DVT and PE.

Implements the Wells clinical prediction rules for estimating the probability
of deep vein thrombosis (DVT) and pulmonary embolism (PE) in adult patients.

References:
  - Wells PS et al. "Value of assessment of pretest probability of deep-vein
    thrombosis in clinical management." Lancet. 1997;350(9094):1795-8.
  - Wells PS et al. "Excluding pulmonary embolism at the bedside without
    diagnostic imaging." Ann Intern Med. 2001;135(2):98-107.

This is a clinical decision support tool, NOT a diagnostic device.
Always correlate with clinical judgment and confirmatory testing.

Stdlib only — no external dependencies.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_dvt()`**: Calculate Wells Score for DVT.

Args:
    criteria: dict mapping criterion keys to boolean presence.
              Keys: active_cancer, paralysis_paresis, recently_bedridden,
              localized_tenderness, entire_leg_swollen, calf_swelling_3cm,
              pitting_edema, collateral_veins, previous_dvt,
              alternative_diagnosis

Returns:
    dict with score, criteria_met, interpretation (two-tier and three-tier),
    prevalence_estimates, and next_steps.
- **`calculate_pe()`**: Calculate Wells Score for PE.

Args:
    criteria: dict mapping criterion keys to boolean presence.
              Keys: clinical_dvt_signs, pe_most_likely, heart_rate_100,
              immobilization_surgery, previous_dvt_pe, hemoptysis,
              malignancy

Returns:
    dict with score, criteria_met, interpretation (two-tier and three-tier),
    prevalence_estimates, and next_steps.
- **`calculate_modified_pe()`**: Calculate Modified Wells Score for PE (same criteria, no alternative
diagnosis criterion — which is already absent from PE criteria).

This is the most commonly used version in clinical practice.
Identical to calculate_pe for the standard PE criteria set.
- **`calculate_geneva()`**: Calculate Revised Geneva Score for PE.

Args:
    criteria: dict mapping criterion keys to boolean presence.
              Keys: previous_dvt_pe, heart_rate_75_94, heart_rate_95_plus,
              surgery_fracture_1mo, hemoptysis, active_cancer,
              unilateral_leg_pain, pain_on_palpation, age_over_65

Returns:
    dict with score, criteria_met, interpretation (two-tier and three-tier).
- **`list_dvt_criteria()`**: Return all DVT criteria with keys, points, and descriptions.

---

## 📐 Mathematical Formulation & Logic

```text
  Calculate Wells Score for DVT.
  score = 0.0
  Calculate Wells Score for PE.
  Calculate Modified Wells Score for PE (same criteria, no alternative
  Identical to calculate_pe for the standard PE criteria set.
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --json <value> --- <value>
```

### Parameter Reference
- `--json`: Specifies input measurement or parameter value.
- `---`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `patient_id` | Parameter / observation metric | Required |
| `age` | Parameter / observation metric | Required |
| `sex` | Parameter / observation metric | Required |
| `prior_vte` | Parameter / observation metric | Required |
| `cancer` | Parameter / observation metric | Required |
| `immobility` | Parameter / observation metric | Required |
| `surgery` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t wells-score-calculator .
docker run -p 8000:8000 wells-score-calculator
```
