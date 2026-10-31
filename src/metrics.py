from __future__ import annotations

from collections import Counter
from typing import Any

CONDITIONS = ("S0", "S1", "D0", "D1")


def calculate(findings: list[dict[str, Any]], ground_truth: dict[str, Any]) -> dict[str, Any]:
    scenarios = {item["scenario_id"]: item for item in ground_truth["scenarios"]}
    detected: dict[str, set[str]] = {condition: set() for condition in CONDITIONS}
    metrics: dict[str, Any] = {}

    for finding in findings:
        if finding["classification"] == "true_positive":
            detected[finding["condition"]].update(finding.get("scenario_ids", []))

    for condition in CONDITIONS:
        eligible = {sid for sid, item in scenarios.items() if condition in item["eligible_conditions"]}
        counts = Counter(
            finding["classification"] for finding in findings if finding["condition"] == condition
        )
        tp, fp = counts["true_positive"], counts["false_positive"]
        precision = tp / (tp + fp) if tp + fp else None
        hit = detected[condition] & eligible
        metrics[condition] = {
            "eligible_scenarios": len(eligible),
            "detected_scenarios": len(hit),
            "scenario_ids_detected": sorted(hit),
            "scenario_ids_missed": sorted(eligible - hit),
            "coverage": len(hit) / len(eligible) if eligible else None,
            "finding_counts": dict(sorted(counts.items())),
            "precision": precision,
        }

    sast = detected["S1"]
    dynamic = detected["D0"] | detected["D1"]
    union = sast | dynamic
    intersection = sast & dynamic
    metrics["combined"] = {
        "scenario_ids_detected": sorted(union),
        "detected_scenarios": len(union),
        "sast_only": sorted(sast - dynamic),
        "dynamic_only": sorted(dynamic - sast),
        "both": sorted(intersection),
        "jaccard_overlap": len(intersection) / len(union) if union else None,
    }
    return metrics

