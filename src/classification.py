from __future__ import annotations

from typing import Any


def _matches(finding: dict[str, Any], criteria: dict[str, Any]) -> bool:
    """A finding matches when every criterion matches.

    Supported criteria keys:
      * any finding field (e.g. rule_id, condition, tool): exact equality
      * rule_id_suffix: finding.rule_id ends with this value. Semgrep prefixes
        check_id with the config directory (e.g. "rules.<id>"), so matching on a
        suffix keeps mappings stable regardless of how the rule dir is mounted.
      * location_path_contains: this substring occurs in finding.location.path.
        Lets a mapping target one specific source file when a rule fires on
        several, so only the validated finding is labelled.
    """
    for key, value in criteria.items():
        if key == "rule_id_suffix":
            if not str(finding.get("rule_id", "")).endswith(value):
                return False
        elif key == "location_path_contains":
            if value not in str(finding.get("location", {}).get("path", "")):
                return False
        elif finding.get(key) != value:
            return False
    return True


def apply_mappings(findings: list[dict[str, Any]], mapping_document: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply explicit human-reviewed rules; unmatched findings remain unverified."""
    for finding in findings:
        for mapping in mapping_document.get("mappings", []):
            if mapping.get("condition") != finding.get("condition"):
                continue
            if _matches(finding, mapping.get("match", {})):
                finding["scenario_ids"] = list(mapping.get("scenario_ids", []))
                finding["classification"] = mapping["classification"]
                finding["classification_rationale"] = mapping.get("rationale", "")
    return findings