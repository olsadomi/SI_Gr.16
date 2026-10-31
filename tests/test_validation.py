import pytest

from src.validation import validate_findings, validate_ground_truth


def test_duplicate_scenarios_are_rejected():
    scenario = {
        "scenario_id": "A", "title": "t", "category": "c", "endpoint": "/x",
        "method": "GET", "oracle": {}, "eligible_conditions": ["D1"],
    }
    with pytest.raises(ValueError, match="duplicate"):
        validate_ground_truth({"target_commit": "a" * 40, "scenarios": [scenario, scenario]})


def test_duplicate_findings_are_rejected():
    finding = {
        "finding_id": "same", "condition": "D1", "tool": "bola-harness",
        "title": "t", "severity": "high", "location": {}, "raw_reference": "x",
        "classification": "true_positive",
    }
    with pytest.raises(ValueError, match="duplicate"):
        validate_findings([finding, finding])

