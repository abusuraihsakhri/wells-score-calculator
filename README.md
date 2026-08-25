# Wells Score Calculator

A Python implementation of the Wells clinical prediction rules for estimating the probability of **deep vein thrombosis (DVT)** and **pulmonary embolism (PE)** in adult patients.

**This is a clinical decision support tool, not a diagnostic device.** Always correlate results with clinical judgment and confirmatory testing.

## What This Actually Does

Implements three validated scoring systems:

| Score | Purpose | Range | Tiers |
|-------|---------|-------|-------|
| **Wells DVT** | Estimate DVT probability | -2 to 9 | Low / Moderate / High |
| **Wells PE** | Estimate PE probability | 0 to 12.5 | Unlikely / Likely (2-tier) or Low / Moderate / High (3-tier) |
| **Revised Geneva** | Alternative PE estimate | 0 to 25 | Unlikely / Likely (2-tier) or Low / Moderate / High (3-tier) |

Each score sums weighted clinical criteria. The total maps to a probability tier with associated prevalence estimates and recommended next steps (e.g., D-dimer testing vs. imaging).

## Requirements

**Python 3.8+** — stdlib only, zero external dependencies.

## Usage

### CLI

```bash
# Interactive DVT scoring (prompts for each criterion)
python cli.py dvt

# Interactive PE scoring
python cli.py pe

# Interactive Revised Geneva scoring
python cli.py geneva

# Non-interactive with JSON input
python cli.py dvt --json '{"active_cancer": true, "previous_dvt": true}'
python cli.py pe --json '{"clinical_dvt_signs": true, "heart_rate_100": true}'

# List all criteria for all scoring systems
python cli.py criteria
```

### Python API

```python
from wells import calculate_dvt, calculate_pe, calculate_geneva

# DVT scoring
result = calculate_dvt({
    "active_cancer": True,
    "recently_bedridden": True,
    "entire_leg_swollen": True,
})
print(result["score"])                    # 3
print(result["two_tier"]["category"])     # "High probability"
print(result["ddimer_guidance"])          # D-dimer recommendation

# PE scoring
result = calculate_pe({
    "clinical_dvt_signs": True,
    "pe_most_likely": True,
    "heart_rate_100": True,
})
print(result["score"])                    # 7.5
print(result["three_tier"]["category"])   # "High probability"

# Revised Geneva scoring
result = calculate_geneva({
    "age_over_65": True,
    "heart_rate_95_plus": True,
    "surgery_fracture_1mo": True,
})
print(result["score"])                    # 8
print(result["two_tier"]["category"])     # "PE likely"
```

## Wells DVT Criteria

| Criterion | Points |
|-----------|--------|
| Active cancer (treatment within 6 months, or palliative) | +1 |
| Paralysis, paresis, or recent cast immobilization of lower extremity | +1 |
| Recently bedridden >3 days, or major surgery within 12 weeks | +1 |
| Localized tenderness along the deep venous system | +1 |
| Entire leg swollen | +1 |
| Calf swelling >3 cm compared to asymptomatic leg | +1 |
| Pitting edema confined to symptomatic leg | +1 |
| Collateral superficial veins (non-varicose) | +1 |
| Previously documented DVT | +1 |
| Alternative diagnosis at least as likely as DVT | **-2** |

**Interpretation (three-tier):** ≤0 Low (5%) · 1–2 Moderate (17%) · ≥3 High (53%)

## Wells PE Criteria

| Criterion | Points |
|-----------|--------|
| Clinical signs/symptoms of DVT | +3 |
| PE is #1 diagnosis OR equally likely | +3 |
| Heart rate >100 bpm | +1.5 |
| Immobilization ≥3 days, or surgery in past 4 weeks | +1.5 |
| Previous DVT or PE | +1.5 |
| Hemoptysis | +1 |
| Malignancy (treatment within 6 months, or palliative) | +1 |

**Interpretation (two-tier):** ≤4 PE Unlikely (12%) · >4 PE Likely (37%)  
**Interpretation (three-tier):** ≤0 Low (3%) · 1–6 Moderate (20%) · ≥7 High (65%)

## D-dimer Integration

The calculator provides D-dimer guidance based on the probability tier:

- **Low/Unlikely probability** → Check D-dimer. If negative (<500 ng/mL FEU), VTE effectively excluded.
- **Moderate probability** → D-dimer recommended. If elevated, proceed to imaging.
- **High/Likely probability** → D-dimer not recommended for ruling out. Proceed directly to imaging.

## Running Tests

```bash
python -m pytest test_wells.py -v
# or
python -m unittest test_wells.py -v
```

## Files

| File | Purpose |
|------|---------|
| `wells.py` | Core scoring engine — all criteria, calculations, and interpretations |
| `cli.py` | Command-line interface (interactive and JSON modes) |
| `test_wells.py` | Test suite covering all scoring systems, criteria, and clinical scenarios |

## References

- Wells PS, Hirsh J, Anderson DR, et al. "Value of assessment of pretest probability of deep-vein thrombosis in clinical management." *Lancet*. 1997;350(9094):1795-8.
- Wells PS, Anderson DR, Rodger M, et al. "Excluding pulmonary embolism at the bedside without diagnostic imaging." *Ann Intern Med*. 2001;135(2):98-107.
- Le Gal G, Righini M, Roy PM, et al. "Prediction of pulmonary embolism in the emergency department: the revised Geneva score." *Ann Intern Med*. 2006;144(3):165-71.

## License

MIT License. See [LICENSE](LICENSE).
