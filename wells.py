#!/usr/bin/env python3
"""
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
"""

from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Wells Score Criteria for DVT
# ---------------------------------------------------------------------------
DVT_CRITERIA: List[Tuple[str, float, str]] = [
    ("active_cancer", 1.0,
     "Active cancer (treatment within 6 months, or palliative)"),
    ("paralysis_paresis", 1.0,
     "Paralysis, paresis, or recent cast immobilization of lower extremity"),
    ("recently_bedridden", 1.0,
     "Recently bedridden >3 days, or major surgery within 12 weeks"),
    ("localized_tenderness", 1.0,
     "Localized tenderness along the deep venous system"),
    ("entire_leg_swollen", 1.0,
     "Entire leg swollen"),
    ("calf_swelling_3cm", 1.0,
     "Calf swelling >3 cm compared to asymptomatic leg "
     "(measured 10 cm below tibial tuberosity)"),
    ("pitting_edema", 1.0,
     "Pitting edema confined to symptomatic leg"),
    ("collateral_veins", 1.0,
     "Collateral superficial veins (non-varicose)"),
    ("previous_dvt", 1.0,
     "Previously documented DVT"),
    ("alternative_diagnosis", -2.0,
     "Alternative diagnosis at least as likely as DVT"),
]

# Wells DVT two-tier interpretation
DVT_TWO_TIER: List[Tuple[float, float, str, str]] = [
    # (max_score_inclusive, prevalence, category, recommendation)
    (0, 5, "Low probability",
     "Consider D-dimer; if negative, DVT effectively excluded."),
    (float("inf"), 53, "High probability",
     "Proceed to compression ultrasonography."),
]

# Wells DVT three-tier interpretation
DVT_THREE_TIER: List[Tuple[float, float, str, str]] = [
    (0, 5, "Low probability",
     "Consider D-dimer; if negative, DVT effectively excluded."),
    (2, 17, "Moderate probability",
     "D-dimer recommended; if elevated, proceed to ultrasound."),
    (float("inf"), 53, "High probability",
     "Proceed directly to compression ultrasonography."),
]


# ---------------------------------------------------------------------------
# Wells Score Criteria for PE
# ---------------------------------------------------------------------------
PE_CRITERIA: List[Tuple[str, float, str]] = [
    ("clinical_dvt_signs", 3.0,
     "Clinical signs and symptoms of DVT"),
    ("pe_most_likely", 3.0,
     "PE is #1 diagnosis OR equally likely"),
    ("heart_rate_100", 1.5,
     "Heart rate >100 bpm"),
    ("immobilization_surgery", 1.5,
     "Immobilization at least 3 days, or surgery within the past 4 weeks"),
    ("previous_dvt_pe", 1.5,
     "Previous DVT or PE"),
    ("hemoptysis", 1.0,
     "Hemoptysis"),
    ("malignancy", 1.0,
     "Malignancy (treatment within 6 months, or palliative)"),
]

# Wells PE two-tier interpretation
PE_TWO_TIER: List[Tuple[float, float, str, str]] = [
    (4, 12, "PE unlikely",
     "Consider D-dimer; if negative, PE effectively excluded."),
    (float("inf"), 37, "PE likely",
     "Proceed to CT pulmonary angiography (CTPA) or V/Q scan."),
]

# Wells PE three-tier interpretation
PE_THREE_TIER: List[Tuple[float, float, str, str]] = [
    (0, 3, "Low probability",
     "Consider D-dimer; if negative, PE effectively excluded."),
    (6, 20, "Moderate probability",
     "D-dimer recommended; if elevated, proceed to CTPA."),
    (float("inf"), 65, "High probability",
     "Proceed directly to CTPA or V/Q scan."),
]


# ---------------------------------------------------------------------------
# Modified Wells for PE (without "alternative diagnosis" criterion)
# Identical to PE_CRITERIA — the original Wells PE score does not include
# the alternative diagnosis criterion (which is DVT-only).
# Kept as an alias for API clarity and backward compatibility.
# ---------------------------------------------------------------------------
MODIFIED_PE_CRITERIA: List[Tuple[str, float, str]] = PE_CRITERIA


# ---------------------------------------------------------------------------
# Revised Geneva Score for PE (for comparison)
# ---------------------------------------------------------------------------
GENEVA_CRITERIA: List[Tuple[str, float, str]] = [
    ("previous_dvt_pe", 3.0,
     "Previous DVT or PE"),
    ("heart_rate_75_94", 3.0,
     "Heart rate 75-94 bpm"),
    ("heart_rate_95_plus", 5.0,
     "Heart rate >= 95 bpm"),
    ("surgery_fracture_1mo", 2.0,
     "Surgery or lower limb fracture within the past month"),
    ("hemoptysis", 2.0,
     "Hemoptysis"),
    ("active_cancer", 2.0,
     "Active cancer (treatment within 6 months, or palliative)"),
    ("unilateral_leg_pain", 3.0,
     "Unilateral lower limb pain"),
    ("pain_on_palpation", 4.0,
     "Pain on lower limb deep venous palpation and unilateral edema"),
    ("age_over_65", 1.0,
     "Age > 65 years"),
]

GENEVA_TWO_TIER: List[Tuple[float, float, str, str]] = [
    (5, 8, "PE unlikely",
     "Consider D-dimer; if negative, PE effectively excluded."),
    (float("inf"), 28, "PE likely",
     "Proceed to CTPA or V/Q scan."),
]

GENEVA_THREE_TIER: List[Tuple[float, float, str, str]] = [
    (3, 8, "Low probability",
     "Consider D-dimer; if negative, PE effectively excluded."),
    (5, 22, "Moderate probability",
     "D-dimer recommended; if elevated, proceed to CTPA."),
    (float("inf"), 65, "High probability",
     "Proceed directly to CTPA or V/Q scan."),
]


# ---------------------------------------------------------------------------
# Core calculation engine
# ---------------------------------------------------------------------------

def _parse_bool(val) -> bool:
    """Parse a value as boolean. Accepts True/False, 1/0, 'yes'/'no', etc."""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "y", "present")
    return False


def calculate_dvt(criteria: Dict[str, bool]) -> Dict:
    """
    Calculate Wells Score for DVT.

    Args:
        criteria: dict mapping criterion keys to boolean presence.
                  Keys: active_cancer, paralysis_paresis, recently_bedridden,
                  localized_tenderness, entire_leg_swollen, calf_swelling_3cm,
                  pitting_edema, collateral_veins, previous_dvt,
                  alternative_diagnosis

    Returns:
        dict with score, criteria_met, interpretation (two-tier and three-tier),
        prevalence_estimates, and next_steps.
    """
    score = 0.0
    criteria_met = []

    for key, points, description in DVT_CRITERIA:
        present = _parse_bool(criteria.get(key, False))
        if present:
            score += points
            criteria_met.append({
                "key": key,
                "points": points,
                "description": description,
            })

    two_tier = _interpret(score, DVT_TWO_TIER)
    three_tier = _interpret(score, DVT_THREE_TIER)

    ddimer_guidance = _dimer_guidance_dvt(score)

    return {
        "score": score,
        "criteria_met": criteria_met,
        "two_tier": two_tier,
        "three_tier": three_tier,
        "ddimer_guidance": ddimer_guidance,
    }


def calculate_pe(criteria: Dict[str, bool]) -> Dict:
    """
    Calculate Wells Score for PE.

    Args:
        criteria: dict mapping criterion keys to boolean presence.
                  Keys: clinical_dvt_signs, pe_most_likely, heart_rate_100,
                  immobilization_surgery, previous_dvt_pe, hemoptysis,
                  malignancy

    Returns:
        dict with score, criteria_met, interpretation (two-tier and three-tier),
        prevalence_estimates, and next_steps.
    """
    score = 0.0
    criteria_met = []

    for key, points, description in PE_CRITERIA:
        present = _parse_bool(criteria.get(key, False))
        if present:
            score += points
            criteria_met.append({
                "key": key,
                "points": points,
                "description": description,
            })

    two_tier = _interpret(score, PE_TWO_TIER)
    three_tier = _interpret(score, PE_THREE_TIER)

    ddimer_guidance = _dimer_guidance_pe(score)

    return {
        "score": score,
        "criteria_met": criteria_met,
        "two_tier": two_tier,
        "three_tier": three_tier,
        "ddimer_guidance": ddimer_guidance,
    }


def calculate_modified_pe(criteria: Dict[str, bool]) -> Dict:
    """
    Calculate Modified Wells Score for PE (same criteria, no alternative
    diagnosis criterion — which is already absent from PE criteria).

    This is the most commonly used version in clinical practice.
    Identical to calculate_pe for the standard PE criteria set.
    """
    score = 0.0
    criteria_met = []

    for key, points, description in MODIFIED_PE_CRITERIA:
        present = _parse_bool(criteria.get(key, False))
        if present:
            score += points
            criteria_met.append({
                "key": key,
                "points": points,
                "description": description,
            })

    two_tier = _interpret(score, PE_TWO_TIER)
    three_tier = _interpret(score, PE_THREE_TIER)

    return {
        "score": score,
        "criteria_met": criteria_met,
        "two_tier": two_tier,
        "three_tier": three_tier,
    }


def calculate_geneva(criteria: Dict[str, bool]) -> Dict:
    """
    Calculate Revised Geneva Score for PE.

    Args:
        criteria: dict mapping criterion keys to boolean presence.
                  Keys: previous_dvt_pe, heart_rate_75_94, heart_rate_95_plus,
                  surgery_fracture_1mo, hemoptysis, active_cancer,
                  unilateral_leg_pain, pain_on_palpation, age_over_65

    Returns:
        dict with score, criteria_met, interpretation (two-tier and three-tier).
    """
    score = 0.0
    criteria_met = []

    for key, points, description in GENEVA_CRITERIA:
        present = _parse_bool(criteria.get(key, False))
        if present:
            score += points
            criteria_met.append({
                "key": key,
                "points": points,
                "description": description,
            })

    two_tier = _interpret(score, GENEVA_TWO_TIER)
    three_tier = _interpret(score, GENEVA_THREE_TIER)

    return {
        "score": score,
        "criteria_met": criteria_met,
        "two_tier": two_tier,
        "three_tier": three_tier,
    }


# ---------------------------------------------------------------------------
# Interpretation helpers
# ---------------------------------------------------------------------------

def _interpret(score: float, tiers: List[Tuple[float, float, str, str]]) -> Dict:
    """Match score against tier definitions and return interpretation."""
    for max_score, prevalence, category, recommendation in tiers:
        if score <= max_score:
            return {
                "category": category,
                "prevalence_pct": prevalence,
                "recommendation": recommendation,
            }
    # Fallback (should not happen with proper tier definitions)
    return {
        "category": "Unknown",
        "prevalence_pct": None,
        "recommendation": "Clinical correlation required.",
    }


def _dimer_guidance_dvt(score: float) -> str:
    """Provide D-dimer guidance based on Wells DVT score."""
    if score <= 0:
        return ("Low probability. A negative D-dimer (<500 ng/mL FEU) "
                "effectively excludes DVT. No imaging needed if D-dimer negative.")
    elif score <= 2:
        return ("Moderate probability. D-dimer testing recommended. "
                "If negative, DVT unlikely. If positive, proceed to "
                "compression ultrasonography.")
    else:
        return ("High probability. D-dimer not recommended for ruling out. "
                "Proceed directly to compression ultrasonography.")


def _dimer_guidance_pe(score: float) -> str:
    """Provide D-dimer guidance based on Wells PE score."""
    if score <= 4:
        return ("PE unlikely. A negative D-dimer (<500 ng/mL FEU) "
                "effectively excludes PE. No imaging needed if D-dimer negative.")
    else:
        return ("PE likely. D-dimer not recommended for ruling out. "
                "Proceed directly to CT pulmonary angiography (CTPA) or "
                "V/Q scan.")


# ---------------------------------------------------------------------------
# Criterion listing helpers
# ---------------------------------------------------------------------------

def list_dvt_criteria() -> List[Dict]:
    """Return all DVT criteria with keys, points, and descriptions."""
    return [
        {"key": k, "points": p, "description": d}
        for k, p, d in DVT_CRITERIA
    ]


def list_pe_criteria() -> List[Dict]:
    """Return all PE criteria with keys, points, and descriptions."""
    return [
        {"key": k, "points": p, "description": d}
        for k, p, d in PE_CRITERIA
    ]


def list_geneva_criteria() -> List[Dict]:
    """Return all Revised Geneva criteria with keys, points, and descriptions."""
    return [
        {"key": k, "points": p, "description": d}
        for k, p, d in GENEVA_CRITERIA
    ]
