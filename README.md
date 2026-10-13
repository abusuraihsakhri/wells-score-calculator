# Wells Score Calculator

A clinical prediction-rule calculator for suspected deep vein thrombosis (DVT) and pulmonary embolism (PE) in adults. Includes a static browser interface, a standard-library Python scoring module, a CLI, and an optional FastAPI server.

## Clinical rules

| Rule | Two-tier classification | Three-tier classification |
| --- | --- | --- |
| Wells DVT | ≤1 DVT unlikely; ≥2 DVT likely | ≤0 low; 1–2 moderate; ≥3 high |
| Wells PE | ≤4 PE unlikely; >4 PE likely | <2 low; 2–6 moderate; >6 high |
| Revised Geneva | ≤5 PE unlikely; ≥6 PE likely | 0–3 low; 4–10 moderate; ≥11 high |

**Clinical limitation:** Scores are pretest-probability classifications, not diagnoses or individualized event probabilities. Clinical judgment, appropriate D-dimer testing, imaging, and local validated diagnostic pathways remain essential. Not a diagnostic device.

## Browser application

The repository-root `index.html` runs directly in a modern browser or through GitHub Pages configured to publish from the repository root. Select Wells DVT, Wells PE, or Revised Geneva, then check the applicable criteria; the score and two-/three-tier interpretation update immediately. `web/index.html` redirects to the main interface.

The static app uses JavaScript only—no Python server or Pyodide, third-party requests, cookies, tracking, or browser storage. Reloading clears the assessment. Do not enter patient identifiers.

## Command line

Requires Python 3.10 or later. Core scoring has no external dependencies.

```bash
git clone https://github.com/abusuraihsakhri/wells-score-calculator.git
cd wells-score-calculator
python cli.py dvt --json '{"active_cancer":true,"previous_dvt":true}'
python cli.py pe --json '{"clinical_dvt_signs":true,"heart_rate_100":true}'
python cli.py geneva --json '{"heart_rate_95_plus":true,"age_over_65":true}'
python cli.py dvt       # guided interactive questions
python cli.py criteria  # print all available criteria
```

Use `calculate_dvt`, `calculate_pe`, and `calculate_geneva` from `wells.py` in Python. Invalid keys and non-boolean inputs are rejected, and Geneva heart-rate categories are mutually exclusive.

## Optional API

```bash
python -m pip install -e '.[web]'
python -m uvicorn agents.api:app --host 127.0.0.1 --port 8000
```

The stateless scoring endpoints are `GET /api/score/criteria` and `POST /api/score/dvt`, `/api/score/pe`, or `/api/score/geneva` (JSON objects mapping criterion names to booleans).

The separate, pre-existing `/api/audit` and `/api/chat` functionality is a generic demonstration, **not clinical triage or medical inference**. Its audit functionality requires an `AUDIT_SECRET_KEY` environment variable; its mock chat provider performs no clinical analysis. Do not supply PHI to those demonstration endpoints.

Docker: `docker build -t wells-score-calculator .` followed by `docker run -p 8000:8000 wells-score-calculator`.

## Testing and development

```bash
python -m pip install -e '.[web,test]'
AUDIT_SECRET_KEY=local-testing-key python -m pytest -q
node --check web/calculator.js
node web/calculator.test.cjs
```

The GitHub Actions workflow is configured for Python 3.10–3.12, isolated test audit keys, and JavaScript scoring checks. Additional legacy enrichment modules are unrelated to Wells scoring and are not clinically validated.

## References

- [NICE NG158](https://www.nice.org.uk/guidance/ng158/chapter/Recommendations): two-tier Wells criteria and diagnostic pathways.
- [2026 multisociety guideline for acute PE](https://www.jacc.org/doi/10.1016/j.jacc.2025.11.005): Wells PE and Revised Geneva classifications.
- Wells PS et al. *Lancet*. 1997;350:1795–1798; Wells PS et al. *Ann Intern Med*. 2001;135:98–107.

Python outputs may include prevalence estimates from historical study cohorts; they must not be interpreted as patient-specific probabilities.

## License

MIT; see [LICENSE](LICENSE). Clinical scoring instruments are attributed to their published literature.
