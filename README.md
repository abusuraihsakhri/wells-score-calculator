# WELLS Score Calculator

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Standard:** Clinical Practice Guidelines

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-71%20passed-brightgreen.svg)
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

**This is a clinical decision support tool, NOT a diagnostic device.**
Always correlate with clinical judgment and confirmatory testing.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_dvt(criteria)`**: Calculate Wells Score for DVT.
  - Keys: `active_cancer`, `paralysis_paresis`, `recently_bedridden`,
    `localized_tenderness`, `entire_leg_swollen`, `calf_swelling_3cm`,
    `pitting_edema`, `collateral_veins`, `previous_dvt`,
    `alternative_diagnosis`
  - Returns: `score`, `criteria_met`, `two_tier`, `three_tier`, `ddimer_guidance`

- **`calculate_pe(criteria)`**: Calculate Wells Score for PE.
  - Keys: `clinical_dvt_signs`, `pe_most_likely`, `heart_rate_100`,
    `immobilization_surgery`, `previous_dvt_pe`, `hemoptysis`, `malignancy`
  - Returns: `score`, `criteria_met`, `two_tier`, `three_tier`, `ddimer_guidance`

- **`calculate_modified_pe(criteria)`**: Calculate Modified Wells Score for PE.
  Same as `calculate_pe` — the standard PE criteria do not include an
  "alternative diagnosis" criterion.

- **`calculate_geneva(criteria)`**: Calculate Revised Geneva Score for PE.
  - Keys: `previous_dvt_pe`, `heart_rate_75_94`, `heart_rate_95_plus`,
    `surgery_fracture_1mo`, `hemoptysis`, `active_cancer`,
    `unilateral_leg_pain`, `pain_on_palpation`, `age_over_65`
  - Returns: `score`, `criteria_met`, `two_tier`, `three_tier`

- **`list_dvt_criteria()`**, **`list_pe_criteria()`**, **`list_geneva_criteria()`**:
  Return all criteria with keys, points, and descriptions.

---

## 📐 Scoring Interpretation

### Wells DVT (range: -2 to 9)
| Two-tier | Three-tier | Score | Prevalence |
|:---------|:-----------|:------|:-----------|
| Low | Low | <= 0 | ~5% |
| High | Moderate | 1-2 | ~17% |
| High | High | >= 3 | ~53% |

### Wells PE (range: 0 to 12.5)
| Two-tier | Three-tier | Score | Prevalence |
|:---------|:-----------|:------|:-----------|
| PE unlikely | Low | <= 0 | ~3% |
| PE unlikely | Moderate | 0.5-6 | ~20% |
| PE likely | High | >= 6.5 | ~65% |

### Revised Geneva PE (range: 0 to 25)
| Two-tier | Three-tier | Score | Prevalence |
|:---------|:-----------|:------|:-----------|
| PE unlikely | Low | 0-3 | ~8% |
| PE unlikely | Moderate | 4-5 | ~22% |
| PE likely | High | >= 6 | ~65% |

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/wells-score-calculator.git
cd wells-score-calculator

# Optional: Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

No external dependencies required for core functionality.

### 1. Guided Interactive Mode
```bash
python cli.py dvt      # Interactive DVT scoring
python cli.py pe       # Interactive PE scoring
python cli.py geneva   # Interactive Revised Geneva scoring
```

### 2. Direct Parameterized Evaluation (JSON input)
```bash
python cli.py dvt --json '{"active_cancer": true, "previous_dvt": true}'
python cli.py pe --json '{"clinical_dvt_signs": true, "heart_rate_100": true}'
python cli.py geneva --json '{"age_over_65": true, "heart_rate_95_plus": true}'
```

### 3. List All Criteria
```bash
python cli.py criteria
```

### 4. Enterprise Audit System (requires `pydantic`)
```bash
# Set the audit secret key
export AUDIT_SECRET_KEY="your-secret-key"

# Run audit
python cli.py audit --task-id "TASK-001"

# Verify audit trail
python cli.py verify-audit

# Query LLM reasoning adapter
python cli.py chat "Explain Wells criteria"
```

### 5. Web API (requires `fastapi`, `uvicorn`)
```bash
pip install fastapi uvicorn pydantic
python -m uvicorn agents.api:app --host 0.0.0.0 --port 8000
```

---

## 🛡️ Security Features

* **Zero-PHI Outbound Interceptor:** AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation. Requires `AUDIT_SECRET_KEY` environment variable.
* **Input Validation:** Robust boolean parsing and JSON error handling in CLI.

---

## 🧪 Testing & Verification

### Core Tests (stdlib only)
```bash
python -m pytest test_wells.py -v
```

### Full Test Suite (requires `pydantic`)
```bash
# Set audit secret key first
export AUDIT_SECRET_KEY="test-key-for-validation"

python -m pytest -v
```

### Run with Docker
```bash
docker build -t wells-score-calculator .
docker run -e AUDIT_SECRET_KEY=change-me -p 8000:8000 wells-score-calculator
```

Or using Docker Compose:
```bash
# Create .env file with your secret key
echo "AUDIT_SECRET_KEY=change-me" > .env

docker-compose up -d
```

---

## 📁 Project Structure

```
wells-score-calculator/
├── wells.py              # Core Wells score calculation engine
├── cli.py                # Command-line interface
├── enrichment.py         # Extended clinical enrichment modules
├── simulator.py          # High-throughput simulation/testing
├── test_wells.py         # Comprehensive unittest test suite (66 tests)
├── tests/
│   ├── test_enrichment.py
│   └── test_wells_score_calculator.py
├── agents/
│   ├── __init__.py
│   ├── api.py            # FastAPI REST API
│   ├── base.py           # Security, PHI guard, HMAC audit
│   ├── models.py         # Pydantic data models
│   ├── supervisor.py     # Multi-agent supervisor orchestrator
│   ├── workers.py        # Specialized worker agents
│   ├── llm_factory.py    # LLM provider abstraction
│   ├── metrics.py        # Prometheus metrics exporter
│   ├── learning.py       # Bayesian calibration engine
│   └── streamer.py       # WebSocket telemetry broadcaster
├── web/
│   └── index.html        # Operations console dashboard
├── pyproject.toml        # Package configuration
├── Dockerfile            # Container build
├── docker-compose.yml    # Service orchestration
├── benchmark_dataset.json
├── sample.csv
└── LICENSE
```

---

## ⚠️ Disclaimer

This software is a clinical decision support tool intended for use by qualified healthcare professionals. It is **NOT** a diagnostic device. All results must be correlated with clinical judgment and confirmatory testing.
