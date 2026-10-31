from __future__ import annotations

from pathlib import Path
from typing import Any

from .classification import apply_mappings
from .config import ROOT
from .io_utils import read_json, write_json
from .metrics import calculate
from .parsers import parse_bola, parse_semgrep, parse_zap
from .validation import validate_findings, validate_ground_truth


def collect(root: Path = ROOT) -> list[dict[str, Any]]:
    raw = root / "results" / "raw"
    findings: list[dict[str, Any]] = []
    candidates = [
        (raw / "semgrep-s0.json", lambda path: parse_semgrep(path, "S0")),
        (raw / "semgrep-s1.json", lambda path: parse_semgrep(path, "S1")),
        (raw / "zap.json", parse_zap),
        (raw / "bola.json", parse_bola),
    ]
    for path, parser in candidates:
        if path.exists():
            findings.extend(parser(path))
        else:
            print(f"warning: raw result missing: {path}")
    return findings


def run(root: Path = ROOT) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ground_truth = read_json(root / "ground_truth" / "scenarios.json")
    validate_ground_truth(ground_truth)
    findings = collect(root)
    findings = apply_mappings(findings, read_json(root / "ground_truth" / "mappings.json"))
    validate_findings(findings)
    metrics = calculate(findings, ground_truth)
    write_json(root / "results" / "normalized" / "findings.json", {"findings": findings})
    write_json(root / "results" / "reports" / "metrics.json", metrics)
    return findings, metrics


def main() -> int:
    findings, metrics = run()
    print(f"Normalized {len(findings)} findings")
    for condition in ("S0", "S1", "D0", "D1"):
        row = metrics[condition]
        print(f"{condition}: {row['detected_scenarios']}/{row['eligible_scenarios']} scenarios detected")
    print(f"Combined: {metrics['combined']['detected_scenarios']} scenarios detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

