from src.classification import apply_mappings


def test_only_explicit_mapping_changes_classification():
    findings = [
        {"condition": "D1", "rule_id": "bola", "classification": "unverified", "scenario_ids": []},
        {"condition": "D0", "rule_id": "other", "classification": "unverified", "scenario_ids": []},
    ]
    mappings = {"mappings": [{
        "condition": "D1",
        "match": {"rule_id": "bola"},
        "scenario_ids": ["A"],
        "classification": "true_positive",
    }]}
    result = apply_mappings(findings, mappings)
    assert result[0]["classification"] == "true_positive"
    assert result[1]["classification"] == "unverified"

