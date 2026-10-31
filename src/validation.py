from __future__ import annotations

from typing import Any

CONDITIONS = {"S0", "S1", "D0", "D1"}
CLASSIFICATIONS = {"true_positive", "false_positive", "unverified", "informational"}


def validate_ground_truth(document: dict[str, Any]) -> None:
    commit = document.get("target_commit", "")
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise ValueError("ground truth target_commit must be a 40-character lowercase Git SHA")
    seen: set[str] = set()
    for scenario in document.get("scenarios", []):
        required = {"scenario_id", "title", "category", "endpoint", "method", "oracle", "eligible_conditions"}
        missing = required - scenario.keys()
        if missing:
            raise ValueError(f"scenario missing fields: {sorted(missing)}")
        scenario_id = scenario["scenario_id"]
        if scenario_id in seen:
            raise ValueError(f"duplicate scenario_id: {scenario_id}")
        seen.add(scenario_id)
        invalid = set(scenario["eligible_conditions"]) - CONDITIONS
        if invalid:
            raise ValueError(f"invalid conditions for {scenario_id}: {sorted(invalid)}")


def validate_findings(findings: list[dict[str, Any]]) -> None:
    required = {"finding_id", "condition", "tool", "title", "severity", "location", "raw_reference", "classification"}
    seen: set[str] = set()
    for finding in findings:
        missing = required - finding.keys()
        if missing:
            raise ValueError(f"finding missing fields: {sorted(missing)}")
        if finding["finding_id"] in seen:
            raise ValueError(f"duplicate finding_id: {finding['finding_id']}")
        seen.add(finding["finding_id"])
        if finding["condition"] not in CONDITIONS:
            raise ValueError(f"invalid condition: {finding['condition']}")
        if finding["classification"] not in CLASSIFICATIONS:
            raise ValueError(f"invalid classification: {finding['classification']}")

