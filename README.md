# Wells Score Calculator

Clinical prediction rules for suspected deep vein thrombosis (DVT) and pulmonary embolism (PE) in adults, available as an offline-capable static browser calculator and a Python library/CLI.

## Features

- Wells DVT score with **two-tier** (DVT unlikely ≤1, DVT likely ≥2) and three-tier (≤0, 1–2, ≥3) interpretations.
- Wells PE score with **two-tier** (PE unlikely ≤4, PE likely >4) and three-tier (<2, 2–6, >6) interpretations.
- Revised Geneva score with three-tier (0–3, 4–10, ≥11) and two-tier (≤5, >5) categories.
- Explicit criterion validation, mutually exclusive Geneva heart-rate ranges, and age/assay-aware diagnostic pathway caveats.
- Browser interface in root \`index.html\`, with no server requirement or external scripts. Static scoring uses JavaScript; no Pyodide is needed.
- Optional FastAPI scoring endpoints; legacy audit demonstration modules remain separate from the clinical algorithms.

**Clinical limitation:** These rules estimate pretest probability, not disease presence or individual absolute risk. Apply them only within validated diagnostic algorithms and clinical context, with appropriate D-dimer testing and/or imaging. Not a diagnostic device.

## Browser use

Open \`index.html\` locally or publish the repository root through GitHub Pages. Select Wells DVT, Wells PE, or Revised Geneva; tick applicable clinical criteria. Scores and classifications update immediately. \`web/index.html\` redirects to the root interface.

The static app performs calculations entirely in-browser. It makes **no network requests**, uses no tracking, cookies, or browser storage, and does not accept patient identifiers. Do not enter PHI in any experimental APIs or legacy audit demonstration tools.

## Python CLI

Python 3.10 or later is supported. The clinical scoring module uses only the standard library.

\`\`\`bash
git clone https://github.com/abusuraihsakhri/wells-score-calculator.git
cd wells-score-calculator

python cli.py dvt --json '{"active_cancer":true,"previous_dvt":true}'
python cli.py pe --json '{"clinical_dvt_signs":true,"heart_rate_100":true}'
python cli.py geneva --json '{"heart_rate_95_plus":true,"age_over_65":true}'
python cli.py dvt       # interactive
python cli.py criteria  # supported keys and point weights
\`\`\`

Library example:

\`\`\`python
from wells import calculate_dvt, calculate_pe, calculate_geneva

print(calculate_dvt({"active_cancer": True, "previous_dvt": True}))
\`\`\`

Invalid keys, malformed input, and contradictory Geneva heart-rate inputs are rejected instead of being silently scored as absent.

## Optional API and legacy modules

\`\`\`bash
python -m pip install -e '.[web]'
python -m uvicorn agents.api:app --host 127.0.0.1 --port 8000
\`\`\`

- \`GET /api/score/criteria\`: available clinical rule criteria.
- \`POST /api/score/dvt\`, \`/api/score/pe\`, \`/api/score/geneva\`: JSON mapping of criterion keys to booleans. These scoring routes do not log or persist the payload.
- \`GET /health\`: service status.
- The older \`/api/audit\`, \`/api/chat\`, and audit-log endpoints are generic **demonstration** utilities, not validated clinical triage or medical inference. Set a strong \`AUDIT_SECRET_KEY\` before using audit functions. The mock chat provider does not perform reasoning.

Container use: \`docker build -t wells-score-calculator .\`, followed by \`docker run -p 8000:8000 wells-score-calculator\`. For the generic audit service, set \`AUDIT_SECRET_KEY\` separately.

## Testing

\`\`\`bash
python -m pip install -e '.[web,test]'
AUDIT_SECRET_KEY=local-test-only-key python -m pytest -q
node --check web/calculator.js
node web/calculator.test.cjs
\`\`\`

CI generates an isolated test key and runs Python 3.10, 3.11, and 3.12 plus JavaScript scoring tests. The source tree includes an additional legacy enrichment suite, which is independent of Wells calculations and not a clinically validated model.

## Clinical references

- [NICE NG158 — Venous thromboembolic diseases: diagnosis, management and thrombophilia testing](https://www.nice.org.uk/guidance/ng158/chapter/Recommendations) (two-level Wells DVT/PE criteria and diagnostic pathways).
- [2026 multi-society guideline for acute pulmonary embolism, JACC](https://www.jacc.org/doi/10.1016/j.jacc.2025.11.005) (three-level Wells PE and Revised Geneva classifications).
- Wells PS et al. *Lancet*. 1997;350:1795–1798; Wells PS et al. *Ann Intern Med*. 2001;135:98–107.

Prevalence estimates present in the Python API reflect historical derivation/validation cohorts, not reliable personalized probabilities. Local testing and clinical verification are required before practice integration.

## License

MIT — see [LICENSE](LICENSE). Clinical criteria are attributed to their source publications.
