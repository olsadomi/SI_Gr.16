from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_utils import read_json, stable_id


SEVERITY = {
    "INFO": "info",
    "INFORMATIONAL": "info",
    "LOW": "low",
    "WARNING": "medium",
    "MEDIUM": "medium",
    "ERROR": "high",
    "HIGH": "high",
    "CRITICAL": "critical",
}


def parse_semgrep(path: Path, condition: str) -> list[dict[str, Any]]:
    document = read_json(path)
    findings = []
    for index, result in enumerate(document.get("results", [])):
        extra = result.get("extra", {})
        start = result.get("start", {})
        rule_id = result.get("check_id", "unknown")
        file_path = result.get("path", "")
        line = start.get("line")
        findings.append(
            {
                "finding_id": stable_id(condition, rule_id, file_path, line, index),
                "condition": condition,
                "tool": "semgrep",
                "rule_id": rule_id,
                "title": extra.get("message", rule_id),
                "description": extra.get("message", ""),
                "severity": SEVERITY.get(str(extra.get("severity", "")).upper(), "unknown"),
                "location": {"path": file_path, "line": line, "column": start.get("col")},
                "scenario_ids": [],
                "classification": "unverified",
                "raw_reference": f"{path.as_posix()}#/results/{index}",
            }
        )
    return findings


def _zap_alerts(document: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(document.get("alerts"), list):
        return document["alerts"]
    alerts: list[dict[str, Any]] = []
    for site in document.get("site", []):
        alerts.extend(site.get("alerts", []))
    return alerts


def parse_zap(path: Path) -> list[dict[str, Any]]:
    alerts = _zap_alerts(read_json(path))
    findings = []
    for index, alert in enumerate(alerts):
        instances = alert.get("instances") or [{}]
        instance = instances[0]
        rule_id = str(alert.get("pluginId") or alert.get("alertRef") or alert.get("alert", "unknown"))
        url = instance.get("uri") or alert.get("url") or ""
        findings.append(
            {
                "finding_id": stable_id("D0", rule_id, url, instance.get("method"), index),
                "condition": "D0",
                "tool": "zap",
                "rule_id": rule_id,
                "title": alert.get("name") or alert.get("alert") or rule_id,
                "description": alert.get("description", ""),
                "severity": SEVERITY.get(str(alert.get("riskdesc") or alert.get("risk", "")).split()[0].upper(), "unknown"),
                "location": {"url": url, "method": instance.get("method")},
                "scenario_ids": [],
                "classification": "unverified",
                "raw_reference": f"{path.as_posix()}#/alerts/{index}",
            }
        )
    return findings


def parse_bola(path: Path) -> list[dict[str, Any]]:
    document = read_json(path)
    findings = []
    for index, result in enumerate(document.get("results", [])):
        vulnerable = bool(result.get("oracle", {}).get("vulnerable"))
        scenario_id = result["scenario_id"]
        findings.append(
            {
                "finding_id": stable_id("D1", result.get("rule_id"), scenario_id, index),
                "condition": "D1",
                "tool": "bola-harness",
                "rule_id": result.get("rule_id", "bola-ownership-swap"),
                "title": "Cross-user object access succeeded" if vulnerable else "Cross-user object access blocked or inconclusive",
                "description": "Two-account ownership-swap oracle against the local crAPI target.",
                "severity": "high" if vulnerable else "info",
                "location": result.get("request", {}),
                "scenario_ids": [scenario_id] if vulnerable else [],
                "classification": "true_positive" if vulnerable else "informational",
                "raw_reference": f"{path.as_posix()}#/results/{index}",
            }
        )
    return findings

