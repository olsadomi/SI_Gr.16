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


def collect_durations(root: Path = ROOT) -> dict[str, float]:
    """Read wall-clock scan time per condition from the runner metadata files.

    Each runner records duration_seconds: Semgrep and ZAP into
    results/raw/<tool>-metadata.json, the BOLA harness into bola.json itself.
    """
    raw = root / "results" / "raw"
    sources = {
        "S0": raw / "semgrep-s0-metadata.json",
        "S1": raw / "semgrep-s1-metadata.json",
        "D0": raw / "zap-metadata.json",
        "D1": raw / "bola.json",
    }
    durations: dict[str, float] = {}
    for condition, path in sources.items():
        if path.exists():
            value = read_json(path).get("duration_seconds")
            if isinstance(value, (int, float)):
                durations[condition] = float(value)
    return durations


def run(root: Path = ROOT) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ground_truth = read_json(root / "ground_truth" / "scenarios.json")
    validate_ground_truth(ground_truth)
    findings = collect(root)
    findings = apply_mappings(findings, read_json(root / "ground_truth" / "mappings.json"))
    validate_findings(findings)
    metrics = calculate(findings, ground_truth, collect_durations(root))
    write_json(root / "results" / "normalized" / "findings.json", {"findings": findings})
    write_json(root / "results" / "reports" / "metrics.json", metrics)
    return findings, metrics


def main() -> int:
    findings, metrics = run()
    print(f"Normalized {len(findings)} findings")
    for condition in ("S0", "S1", "D0", "D1"):
        row = metrics[condition]
        seconds = row.get("duration_seconds")
        timing = f" in {seconds:.1f}s" if isinstance(seconds, (int, float)) else ""
        print(f"{condition}: {row['detected_scenarios']}/{row['eligible_scenarios']} scenarios detected{timing}")
    print(f"Combined: {metrics['combined']['detected_scenarios']} scenarios detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())