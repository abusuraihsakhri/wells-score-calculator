"""Clinical boundaries and safety regressions for public scoring interfaces."""
import pytest

from agents.base import AuditTrail
from agents.api import score_patient
from fastapi import HTTPException
from cli import main
from wells import calculate_dvt, calculate_pe, calculate_geneva, GENEVA_CRITERIA


def test_dvt_two_tier_boundary():
    assert calculate_dvt({"active_cancer": True})["two_tier"]["category"] == "DVT unlikely"
    assert calculate_dvt({"active_cancer": True, "previous_dvt": True})["two_tier"]["category"] == "DVT likely"


def test_pe_three_tier_boundaries():
    assert calculate_pe({"heart_rate_100": True})["three_tier"]["category"] == "Low probability"
    assert calculate_pe({"hemoptysis": True, "malignancy": True})["three_tier"]["category"] == "Moderate probability"
    assert calculate_pe({"clinical_dvt_signs": True, "pe_most_likely": True})["three_tier"]["category"] == "Moderate probability"
    assert calculate_pe({"clinical_dvt_signs": True, "pe_most_likely": True, "hemoptysis": True})["three_tier"]["category"] == "High probability"


def test_pe_two_tier_boundary():
    assert calculate_pe({"clinical_dvt_signs": True, "hemoptysis": True})["two_tier"]["category"] == "PE unlikely"
    assert calculate_pe({"clinical_dvt_signs": True, "heart_rate_100": True})["two_tier"]["category"] == "PE likely"


def test_geneva_boundaries_and_exclusive_heart_rate():
    assert calculate_geneva({"hemoptysis": True, "active_cancer": True})["three_tier"]["category"] == "Moderate probability"
    assert calculate_geneva({"heart_rate_95_plus": True, "pain_on_palpation": True})["three_tier"]["category"] == "Moderate probability"
    assert calculate_geneva({"heart_rate_95_plus": True, "pain_on_palpation": True, "active_cancer": True})["three_tier"]["category"] == "High probability"
    with pytest.raises(ValueError, match="mutually exclusive"):
        calculate_geneva({"heart_rate_75_94": True, "heart_rate_95_plus": True})
    assert calculate_geneva({k: True for k, _, _ in GENEVA_CRITERIA if k != "heart_rate_75_94"})["score"] == 22


@pytest.mark.parametrize("criteria", [[], {"hemoptysis": "maybe"}, {"hemoptysis": 9}, {"misspelled": True}])
def test_invalid_input_rejected(criteria):
    with pytest.raises(ValueError):
        calculate_pe(criteria)


def test_cli_rejects_non_object_json():
    assert main(["pe", "--json", "[]"]) == 1


def test_audit_hmac_verification_detects_tampering():
    audit = AuditTrail(secret_key="isolated-unit-test-key")
    audit.log("test", "unit", "event", {"status": "ok"})
    assert audit.verify_integrity()
    external = audit.get_trail()
    external[0]["actor"] = "tampered outside"
    assert audit.verify_integrity()  # Snapshot is not a mutable internal reference.
    audit.logs[0]["actor"] = "tampered inside"
    assert not audit.verify_integrity()


def test_api_score_routes_are_stateless():
    assert score_patient("dvt", {"active_cancer": True, "previous_dvt": True})["score"] == 2
    with pytest.raises(HTTPException) as exc:
        score_patient("pe", {"unexpected": True})
    assert exc.value.status_code == 422
    with pytest.raises(HTTPException) as exc:
        score_patient("bad_rule", {})
    assert exc.value.status_code == 404
