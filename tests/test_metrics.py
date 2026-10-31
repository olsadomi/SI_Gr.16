from src.metrics import calculate


def test_metrics_keep_condition_denominators_and_union():
    ground_truth = {"scenarios": [
        {"scenario_id": "A", "eligible_conditions": ["S0", "S1", "D0", "D1"]},
        {"scenario_id": "B", "eligible_conditions": ["S0", "S1", "D0", "D1"]},
    ]}
    findings = [
        {"condition": "S1", "classification": "true_positive", "scenario_ids": ["A"]},
        {"condition": "D0", "classification": "false_positive", "scenario_ids": []},
        {"condition": "D1", "classification": "true_positive", "scenario_ids": ["B"]},
    ]
    result = calculate(findings, ground_truth)
    assert result["S1"]["coverage"] == 0.5
    assert result["D0"]["precision"] == 0.0
    assert result["combined"]["detected_scenarios"] == 2
    assert result["combined"]["sast_only"] == ["A"]
    assert result["combined"]["dynamic_only"] == ["B"]

