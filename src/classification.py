from __future__ import annotations

from typing import Any


def apply_mappings(findings: list[dict[str, Any]], mapping_document: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply explicit human-reviewed rules; unmatched findings remain unverified."""
    for finding in findings:
        for mapping in mapping_document.get("mappings", []):
            if mapping.get("condition") != finding.get("condition"):
                continue
            criteria = mapping.get("match", {})
            if all(finding.get(key) == value for key, value in criteria.items()):
                finding["scenario_ids"] = list(mapping.get("scenario_ids", []))
                finding["classification"] = mapping["classification"]
                finding["classification_rationale"] = mapping.get("rationale", "")
    return findings

