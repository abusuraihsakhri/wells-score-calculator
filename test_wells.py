#!/usr/bin/env python3
"""
Tests for the Wells Score Calculator.

Covers:
  - DVT: low / moderate / high probability
  - PE: unlikely / likely (two-tier) and low / moderate / high (three-tier)
  - All individual DVT criteria
  - All individual PE criteria
  - Alternative diagnosis criterion (-2 points)
  - Revised Geneva Score
  - Clinical scenarios (realistic patient presentations)
  - Edge cases (no criteria, all criteria, boundary scores)
  - CLI smoke tests

Stdlib only — uses unittest.
"""

import json
import unittest

from wells import (
    calculate_dvt,
    calculate_pe,
    calculate_modified_pe,
    calculate_geneva,
    list_dvt_criteria,
    list_pe_criteria,
    list_geneva_criteria,
    DVT_CRITERIA,
    PE_CRITERIA,
    GENEVA_CRITERIA,
)


class TestDVTLowProbability(unittest.TestCase):
    """DVT score <= 0 → Low probability (5% prevalence)."""

    def test_no_criteria(self):
        """No criteria present → score 0 → low probability."""
        result = calculate_dvt({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["two_tier"]["category"], "Low probability")
        self.assertEqual(result["three_tier"]["category"], "Low probability")
        self.assertEqual(result["two_tier"]["prevalence_pct"], 5)

    def test_only_alternative_diagnosis(self):
        """Alternative diagnosis alone → score -2 → low probability."""
        result = calculate_dvt({"alternative_diagnosis": True})
        self.assertEqual(result["score"], -2)
        self.assertEqual(result["two_tier"]["category"], "Low probability")
        self.assertEqual(result["three_tier"]["category"], "Low probability")

    def test_one_positive_minus_alternative(self):
        """One positive + alternative diagnosis → 1 + (-2) = -1 → low."""
        result = calculate_dvt({
            "active_cancer": True,
            "alternative_diagnosis": True,
        })
        self.assertEqual(result["score"], -1)
        self.assertEqual(result["two_tier"]["category"], "Low probability")

    def test_young_healthy_no_risk(self):
        """Young patient with no risk factors → score 0."""
        result = calculate_dvt({
            "active_cancer": False,
            "paralysis_paresis": False,
            "recently_bedridden": False,
            "localized_tenderness": False,
            "entire_leg_swollen": False,
            "calf_swelling_3cm": False,
            "pitting_edema": False,
            "collateral_veins": False,
            "previous_dvt": False,
            "alternative_diagnosis": False,
        })
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["criteria_met"], [])


class TestDVTModerateProbability(unittest.TestCase):
    """DVT score 1-2 → Moderate probability (17% prevalence)."""

    def test_score_1(self):
        """Single criterion → score 1 → moderate."""
        result = calculate_dvt({"active_cancer": True})
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["three_tier"]["category"], "Moderate probability")
        self.assertEqual(result["three_tier"]["prevalence_pct"], 17)

    def test_score_2(self):
        """Two criteria → score 2 → moderate."""
        result = calculate_dvt({
            "active_cancer": True,
            "recently_bedridden": True,
        })
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["three_tier"]["category"], "Moderate probability")

    def test_three_positive_minus_alternative(self):
        """Three positive + alternative → 3 + (-2) = 1 → moderate."""
        result = calculate_dvt({
            "active_cancer": True,
            "paralysis_paresis": True,
            "recently_bedridden": True,
            "alternative_diagnosis": True,
        })
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["three_tier"]["category"], "Moderate probability")


class TestDVTHighProbability(unittest.TestCase):
    """DVT score >= 3 → High probability (53% prevalence)."""

    def test_score_3(self):
        """Three criteria → score 3 → high."""
        result = calculate_dvt({
            "active_cancer": True,
            "paralysis_paresis": True,
            "recently_bedridden": True,
        })
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["two_tier"]["category"], "High probability")
        self.assertEqual(result["three_tier"]["category"], "High probability")
        self.assertEqual(result["two_tier"]["prevalence_pct"], 53)

    def test_score_5(self):
        """Five criteria → score 5 → high."""
        result = calculate_dvt({
            "active_cancer": True,
            "paralysis_paresis": True,
            "recently_bedridden": True,
            "localized_tenderness": True,
            "entire_leg_swollen": True,
        })
        self.assertEqual(result["score"], 5)
        self.assertEqual(result["two_tier"]["category"], "High probability")

    def test_all_positive_no_alternative(self):
        """All 9 positive criteria (no alternative) → score 9 → high."""
        result = calculate_dvt({
            "active_cancer": True,
            "paralysis_paresis": True,
            "recently_bedridden": True,
            "localized_tenderness": True,
            "entire_leg_swollen": True,
            "calf_swelling_3cm": True,
            "pitting_edema": True,
            "collateral_veins": True,
            "previous_dvt": True,
        })
        self.assertEqual(result["score"], 9)
        self.assertEqual(result["two_tier"]["category"], "High probability")

    def test_all_positive_with_alternative(self):
        """All 10 criteria → 9 + (-2) = 7 → high."""
        result = calculate_dvt({
            "active_cancer": True,
            "paralysis_paresis": True,
            "recently_bedridden": True,
            "localized_tenderness": True,
            "entire_leg_swollen": True,
            "calf_swelling_3cm": True,
            "pitting_edema": True,
            "collateral_veins": True,
            "previous_dvt": True,
            "alternative_diagnosis": True,
        })
        self.assertEqual(result["score"], 7)
        self.assertEqual(result["two_tier"]["category"], "High probability")


class TestDVTIndividualCriteria(unittest.TestCase):
    """Each DVT criterion contributes the correct number of points."""

    def test_each_criterion_points(self):
        expected = {
            "active_cancer": 1,
            "paralysis_paresis": 1,
            "recently_bedridden": 1,
            "localized_tenderness": 1,
            "entire_leg_swollen": 1,
            "calf_swelling_3cm": 1,
            "pitting_edema": 1,
            "collateral_veins": 1,
            "previous_dvt": 1,
            "alternative_diagnosis": -2,
        }
        for key, expected_pts in expected.items():
            result = calculate_dvt({key: True})
            self.assertEqual(
                result["score"], expected_pts,
                f"Criterion '{key}' should give {expected_pts} pts, "
                f"got {result['score']}"
            )


class TestDVTAlternativeDiagnosis(unittest.TestCase):
    """The alternative diagnosis criterion subtracts 2 points."""

    def test_alternative_alone(self):
        result = calculate_dvt({"alternative_diagnosis": True})
        self.assertEqual(result["score"], -2)
        self.assertEqual(len(result["criteria_met"]), 1)
        self.assertEqual(result["criteria_met"][0]["points"], -2)

    def test_alternative_with_high_score(self):
        """5 positive criteria + alternative → 5 - 2 = 3 → still high."""
        result = calculate_dvt({
            "active_cancer": True,
            "paralysis_paresis": True,
            "recently_bedridden": True,
            "localized_tenderness": True,
            "entire_leg_swollen": True,
            "alternative_diagnosis": True,
        })
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["two_tier"]["category"], "High probability")

    def test_alternative_drops_to_moderate(self):
        """3 positive + alternative → 3 - 2 = 1 → moderate."""
        result = calculate_dvt({
            "active_cancer": True,
            "paralysis_paresis": True,
            "recently_bedridden": True,
            "alternative_diagnosis": True,
        })
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["three_tier"]["category"], "Moderate probability")


class TestPEUnlikely(unittest.TestCase):
    """PE score <= 4 → PE unlikely (12% prevalence)."""

    def test_no_criteria(self):
        result = calculate_pe({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["two_tier"]["category"], "PE unlikely")
        self.assertEqual(result["two_tier"]["prevalence_pct"], 12)

    def test_score_1(self):
        """Hemoptysis alone → 1 → unlikely."""
        result = calculate_pe({"hemoptysis": True})
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["two_tier"]["category"], "PE unlikely")

    def test_score_4(self):
        """Heart rate + immobilization → 1.5 + 1.5 = 3 → unlikely."""
        result = calculate_pe({
            "heart_rate_100": True,
            "immobilization_surgery": True,
        })
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["two_tier"]["category"], "PE unlikely")

    def test_score_exactly_4(self):
        """HR + immobilization + hemoptysis + malignancy → 1.5+1.5+1+1 = 5 → likely."""
        """HR + immobilization + previous DVT/PE → 1.5+1.5+1.5 = 4.5 → likely."""
        result = calculate_pe({
            "heart_rate_100": True,
            "immobilization_surgery": True,
            "previous_dvt_pe": True,
        })
        self.assertEqual(result["score"], 4.5)
        self.assertEqual(result["two_tier"]["category"], "PE likely")

    def test_score_4_exact_boundary(self):
        """Score exactly 4 → unlikely (threshold is <= 4)."""
        """HR + hemoptysis + malignancy → 1.5 + 1 + 1 = 3.5 → unlikely."""
        result = calculate_pe({
            "heart_rate_100": True,
            "hemoptysis": True,
            "malignancy": True,
        })
        self.assertEqual(result["score"], 3.5)
        self.assertEqual(result["two_tier"]["category"], "PE unlikely")


class TestPELikely(unittest.TestCase):
    """PE score > 4 → PE likely (37% prevalence)."""

    def test_score_5(self):
        """DVT signs + hemoptysis → 3 + 1 = 4 → unlikely (boundary)."""
        """DVT signs + HR + hemoptysis → 3 + 1.5 + 1 = 5.5 → likely."""
        result = calculate_pe({
            "clinical_dvt_signs": True,
            "heart_rate_100": True,
            "hemoptysis": True,
        })
        self.assertEqual(result["score"], 5.5)
        self.assertEqual(result["two_tier"]["category"], "PE likely")
        self.assertEqual(result["two_tier"]["prevalence_pct"], 37)

    def test_pe_most_likely_plus_dvt(self):
        """PE #1 + DVT signs → 3 + 3 = 6 → likely."""
        result = calculate_pe({
            "pe_most_likely": True,
            "clinical_dvt_signs": True,
        })
        self.assertEqual(result["score"], 6)
        self.assertEqual(result["two_tier"]["category"], "PE likely")

    def test_all_criteria(self):
        """All 7 criteria → 3+3+1.5+1.5+1.5+1+1 = 12.5 → likely."""
        result = calculate_pe({
            "clinical_dvt_signs": True,
            "pe_most_likely": True,
            "heart_rate_100": True,
            "immobilization_surgery": True,
            "previous_dvt_pe": True,
            "hemoptysis": True,
            "malignancy": True,
        })
        self.assertEqual(result["score"], 12.5)
        self.assertEqual(result["two_tier"]["category"], "PE likely")


class TestPEThreeTier(unittest.TestCase):
    """PE three-tier: <=0 low, 1-6 moderate, >=7 high."""

    def test_low(self):
        result = calculate_pe({})
        self.assertEqual(result["three_tier"]["category"], "Low probability")
        self.assertEqual(result["three_tier"]["prevalence_pct"], 3)

    def test_moderate(self):
        result = calculate_pe({"hemoptysis": True})
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["three_tier"]["category"], "Moderate probability")
        self.assertEqual(result["three_tier"]["prevalence_pct"], 20)

    def test_high(self):
        result = calculate_pe({
            "clinical_dvt_signs": True,
            "pe_most_likely": True,
            "heart_rate_100": True,
            "immobilization_surgery": True,
            "previous_dvt_pe": True,
        })
        self.assertEqual(result["score"], 10.5)
        self.assertEqual(result["three_tier"]["category"], "High probability")
        self.assertEqual(result["three_tier"]["prevalence_pct"], 65)


class TestPEIndividualCriteria(unittest.TestCase):
    """Each PE criterion contributes the correct number of points."""

    def test_each_criterion_points(self):
        expected = {
            "clinical_dvt_signs": 3.0,
            "pe_most_likely": 3.0,
            "heart_rate_100": 1.5,
            "immobilization_surgery": 1.5,
            "previous_dvt_pe": 1.5,
            "hemoptysis": 1.0,
            "malignancy": 1.0,
        }
        for key, expected_pts in expected.items():
            result = calculate_pe({key: True})
            self.assertEqual(
                result["score"], expected_pts,
                f"Criterion '{key}' should give {expected_pts} pts, "
                f"got {result['score']}"
            )


class TestModifiedPE(unittest.TestCase):
    """Modified Wells PE — same criteria, verify it works identically."""

    def test_unlikely(self):
        result = calculate_modified_pe({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["two_tier"]["category"], "PE unlikely")

    def test_likely(self):
        result = calculate_modified_pe({
            "clinical_dvt_signs": True,
            "pe_most_likely": True,
        })
        self.assertEqual(result["score"], 6)
        self.assertEqual(result["two_tier"]["category"], "PE likely")


class TestGenevaScore(unittest.TestCase):
    """Revised Geneva Score for PE."""

    def test_no_criteria(self):
        result = calculate_geneva({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["two_tier"]["category"], "PE unlikely")

    def test_low_probability(self):
        """Age >65 alone → 1 → low."""
        result = calculate_geneva({"age_over_65": True})
        self.assertEqual(result["score"], 1)
        self.assertEqual(result["three_tier"]["category"], "Low probability")
        self.assertEqual(result["three_tier"]["prevalence_pct"], 8)

    def test_moderate_probability(self):
        """Hemoptysis + active cancer → 2+2 = 4 → moderate."""
        result = calculate_geneva({
            "hemoptysis": True,
            "active_cancer": True,
        })
        self.assertEqual(result["score"], 4)
        self.assertEqual(result["three_tier"]["category"], "Moderate probability")
        self.assertEqual(result["three_tier"]["prevalence_pct"], 22)

    def test_high_probability(self):
        """Multiple high-value criteria → score >= 6 → high."""
        result = calculate_geneva({
            "previous_dvt_pe": True,
            "heart_rate_95_plus": True,
            "pain_on_palpation": True,
            "unilateral_leg_pain": True,
        })
        self.assertEqual(result["score"], 15)
        self.assertEqual(result["three_tier"]["category"], "High probability")
        self.assertEqual(result["three_tier"]["prevalence_pct"], 65)

    def test_each_criterion_points(self):
        expected = {
            "previous_dvt_pe": 3.0,
            "heart_rate_75_94": 3.0,
            "heart_rate_95_plus": 5.0,
            "surgery_fracture_1mo": 2.0,
            "hemoptysis": 2.0,
            "active_cancer": 2.0,
            "unilateral_leg_pain": 3.0,
            "pain_on_palpation": 4.0,
            "age_over_65": 1.0,
        }
        for key, expected_pts in expected.items():
            result = calculate_geneva({key: True})
            self.assertEqual(
                result["score"], expected_pts,
                f"Geneva criterion '{key}' should give {expected_pts} pts, "
                f"got {result['score']}"
            )

    def test_all_criteria(self):
        """All Geneva criteria → 3+3+5+2+2+2+3+4+1 = 25."""
        result = calculate_geneva({
            "previous_dvt_pe": True,
            "heart_rate_75_94": True,
            "heart_rate_95_plus": True,
            "surgery_fracture_1mo": True,
            "hemoptysis": True,
            "active_cancer": True,
            "unilateral_leg_pain": True,
            "pain_on_palpation": True,
            "age_over_65": True,
        })
        self.assertEqual(result["score"], 25)
        self.assertEqual(result["two_tier"]["category"], "PE likely")


class TestDDimerGuidance(unittest.TestCase):
    """D-dimer integration guidance is provided."""

    def test_dvt_low_dimer_guidance(self):
        result = calculate_dvt({})
        self.assertIn("D-dimer", result["ddimer_guidance"])
        self.assertIn("negative", result["ddimer_guidance"])

    def test_dvt_moderate_dimer_guidance(self):
        result = calculate_dvt({"active_cancer": True})
        self.assertIn("D-dimer", result["ddimer_guidance"])

    def test_dvt_high_dimer_guidance(self):
        result = calculate_dvt({
            "active_cancer": True,
            "paralysis_paresis": True,
            "recently_bedridden": True,
        })
        self.assertIn("not recommended", result["ddimer_guidance"])

    def test_pe_unlikely_dimer_guidance(self):
        result = calculate_pe({})
        self.assertIn("D-dimer", result["ddimer_guidance"])

    def test_pe_likely_dimer_guidance(self):
        result = calculate_pe({
            "clinical_dvt_signs": True,
            "pe_most_likely": True,
        })
        self.assertIn("not recommended", result["ddimer_guidance"])


class TestClinicalScenarios(unittest.TestCase):
    """Realistic clinical patient presentations."""

    def test_scenario_postoperative_patient(self):
        """65yo post-hip replacement, leg swelling, bedridden 5 days.
        Expected: High probability DVT."""
        result = calculate_dvt({
            "recently_bedridden": True,
            "localized_tenderness": True,
            "entire_leg_swollen": True,
            "pitting_edema": True,
        })
        self.assertEqual(result["score"], 4)
        self.assertEqual(result["two_tier"]["category"], "High probability")

    def test_scenario_young_woman_leg_pain(self):
        """25yo woman with leg pain, no risk factors, alternative diagnosis
        (muscle strain) more likely. Expected: Low probability DVT."""
        result = calculate_dvt({
            "alternative_diagnosis": True,
        })
        self.assertEqual(result["score"], -2)
        self.assertEqual(result["two_tier"]["category"], "Low probability")

    def test_scenario_cancer_patient_dyspnea(self):
        """58yo with lung cancer, recent immobilization, tachycardia,
        hemoptysis. Expected: PE likely."""
        result = calculate_pe({
            "malignancy": True,
            "immobilization_surgery": True,
            "heart_rate_100": True,
            "hemoptysis": True,
        })
        self.assertEqual(result["score"], 5)
        self.assertEqual(result["two_tier"]["category"], "PE likely")

    def test_scenario_healthy_young_adult_dyspnea(self):
        """22yo with mild dyspnea after exercise, no risk factors.
        Expected: PE unlikely."""
        result = calculate_pe({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["two_tier"]["category"], "PE unlikely")
        self.assertEqual(result["three_tier"]["category"], "Low probability")

    def test_scenario_postop_with_dvt_signs_and_pe(self):
        """Post-surgical patient with DVT signs, PE equally likely,
        tachycardia. Expected: High probability PE."""
        result = calculate_pe({
            "clinical_dvt_signs": True,
            "pe_most_likely": True,
            "heart_rate_100": True,
            "immobilization_surgery": True,
        })
        self.assertEqual(result["score"], 9)
        self.assertEqual(result["two_tier"]["category"], "PE likely")
        self.assertEqual(result["three_tier"]["category"], "High probability")

    def test_scenario_previous_dvt_with_new_symptoms(self):
        """Patient with previous DVT, now calf swelling and tenderness.
        Expected: High probability DVT."""
        result = calculate_dvt({
            "previous_dvt": True,
            "localized_tenderness": True,
            "calf_swelling_3cm": True,
        })
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["two_tier"]["category"], "High probability")

    def test_scenario_geneva_postop_elderly(self):
        """70yo post-surgery with tachycardia and leg pain.
        Geneva: age>65(1) + surgery(2) + HR>=95(5) + leg pain(3) = 11 → high."""
        result = calculate_geneva({
            "age_over_65": True,
            "surgery_fracture_1mo": True,
            "heart_rate_95_plus": True,
            "unilateral_leg_pain": True,
        })
        self.assertEqual(result["score"], 11)
        self.assertEqual(result["two_tier"]["category"], "PE likely")
        self.assertEqual(result["three_tier"]["category"], "High probability")


class TestEdgeCases(unittest.TestCase):
    """Edge cases and boundary conditions."""

    def test_dvt_boundary_score_0(self):
        """Score exactly 0 → low (two-tier) and low (three-tier)."""
        result = calculate_dvt({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["two_tier"]["category"], "Low probability")
        self.assertEqual(result["three_tier"]["category"], "Low probability")

    def test_dvt_boundary_score_1(self):
        """Score exactly 1 → high (two-tier, since 1 > 0) and moderate (three-tier)."""
        result = calculate_dvt({"active_cancer": True})
        self.assertEqual(result["score"], 1)
        # Two-tier: <=0 is low, >0 is high
        self.assertEqual(result["two_tier"]["category"], "High probability")
        # Three-tier: 1-2 is moderate
        self.assertEqual(result["three_tier"]["category"], "Moderate probability")

    def test_pe_boundary_score_4(self):
        """HR + immobilization + hemoptysis → 1.5+1.5+1 = 4 → PE unlikely."""
        result = calculate_pe({
            "heart_rate_100": True,
            "immobilization_surgery": True,
            "hemoptysis": True,
        })
        self.assertEqual(result["score"], 4.0)
        self.assertEqual(result["two_tier"]["category"], "PE unlikely")

    def test_criteria_listing_dvt(self):
        """list_dvt_criteria returns correct count."""
        criteria = list_dvt_criteria()
        self.assertEqual(len(criteria), 10)

    def test_criteria_listing_pe(self):
        """list_pe_criteria returns correct count."""
        criteria = list_pe_criteria()
        self.assertEqual(len(criteria), 7)

    def test_criteria_listing_geneva(self):
        """list_geneva_criteria returns correct count."""
        criteria = list_geneva_criteria()
        self.assertEqual(len(criteria), 9)

    def test_dvt_criteria_constants_match_list(self):
        """DVT_CRITERIA has 10 entries."""
        self.assertEqual(len(DVT_CRITERIA), 10)

    def test_pe_criteria_constants_match_list(self):
        """PE_CRITERIA has 7 entries."""
        self.assertEqual(len(PE_CRITERIA), 7)

    def test_result_structure_dvt(self):
        """DVT result has all expected keys."""
        result = calculate_dvt({})
        for key in ("score", "criteria_met", "two_tier", "three_tier",
                     "ddimer_guidance"):
            self.assertIn(key, result)

    def test_result_structure_pe(self):
        """PE result has all expected keys."""
        result = calculate_pe({})
        for key in ("score", "criteria_met", "two_tier", "three_tier",
                     "ddimer_guidance"):
            self.assertIn(key, result)

    def test_result_structure_geneva(self):
        """Geneva result has all expected keys."""
        result = calculate_geneva({})
        for key in ("score", "criteria_met", "two_tier", "three_tier"):
            self.assertIn(key, result)

    def test_criteria_met_descriptions(self):
        """criteria_met entries have descriptions."""
        result = calculate_dvt({"active_cancer": True, "previous_dvt": True})
        self.assertEqual(len(result["criteria_met"]), 2)
        for c in result["criteria_met"]:
            self.assertIn("description", c)
            self.assertIn("points", c)
            self.assertIn("key", c)

    def test_string_input_parsing(self):
        """String 'true'/'yes' values are parsed correctly."""
        result = calculate_dvt({"active_cancer": "yes", "previous_dvt": "true"})
        self.assertEqual(result["score"], 2)

    def test_integer_input_parsing(self):
        """Integer 1 values are parsed correctly."""
        result = calculate_pe({"heart_rate_100": 1, "hemoptysis": 1})
        self.assertEqual(result["score"], 2.5)


class TestCLISmoke(unittest.TestCase):
    """Smoke tests for the CLI module."""

    def test_criteria_command(self):
        """CLI criteria command runs without error."""
        from cli import main
        ret = main(["criteria"])
        self.assertEqual(ret, 0)

    def test_dvt_json(self):
        """CLI dvt --json works."""
        from cli import main
        criteria = json.dumps({"active_cancer": True, "previous_dvt": True})
        ret = main(["dvt", "--json", criteria])
        self.assertEqual(ret, 0)

    def test_pe_json(self):
        """CLI pe --json works."""
        from cli import main
        criteria = json.dumps({"clinical_dvt_signs": True, "pe_most_likely": True})
        ret = main(["pe", "--json", criteria])
        self.assertEqual(ret, 0)

    def test_geneva_json(self):
        """CLI geneva --json works."""
        from cli import main
        criteria = json.dumps({"age_over_65": True, "heart_rate_95_plus": True})
        ret = main(["geneva", "--json", criteria])
        self.assertEqual(ret, 0)

    def test_no_command(self):
        """CLI with no command returns 1."""
        from cli import main
        ret = main([])
        self.assertEqual(ret, 1)


if __name__ == "__main__":
    unittest.main()
