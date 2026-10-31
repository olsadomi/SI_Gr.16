"""Tests for the pipeline fixes: suffix mapping and per-condition timing."""
from src.classification import apply_mappings
from src.metrics import calculate


def test_rule_id_suffix_mapping_handles_semgrep_prefix():
    findings = [{
        "condition": "S1",
        "rule_id": "rules.crapi-controller-path-object-without-request-context",
        "classification": "unverified", "scenario_ids": [],
    }]
    mapping = {"mappings": [{
        "condition": "S1",
        "match": {"rule_id_suffix": "crapi-controller-path-object-without-request-context"},
        "scenario_ids": ["CRAPI-BOLA-VEHICLE-LOCATION"],
        "classification": "true_positive", "rationale": "x",
    }]}
    out = apply_mappings(findings, mapping)
    assert out[0]["classification"] == "true_positive"
    assert out[0]["scenario_ids"] == ["CRAPI-BOLA-VEHICLE-LOCATION"]


def test_metrics_attach_durations():
    gt = {"scenarios": [{"scenario_id": "A", "eligible_conditions": ["S0", "S1", "D0", "D1"]}]}
    findings = [{"condition": "D1", "classification": "true_positive", "scenario_ids": ["A"]}]
    result = calculate(findings, gt, {"S0": 12.5, "D1": 3.2})
    assert result["S0"]["duration_seconds"] == 12.5
    assert result["D1"]["duration_seconds"] == 3.2
    assert result["D0"]["duration_seconds"] is None
    assert result["combined"]["total_runtime_seconds"] == 15.7