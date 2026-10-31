"""Regression test for the custom BOLA Semgrep rule.

Runs only when the `semgrep` binary is available (local dev); skipped in minimal
CI. Verifies the rule flags the vulnerable fixture and leaves the safe one alone.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "sast" / "rules" / "crapi-java-authorization.yml"
FIXTURES = ROOT / "sast" / "fixtures"

pytestmark = pytest.mark.skipif(shutil.which("semgrep") is None, reason="semgrep not installed")


def _scan(target: Path):
    proc = subprocess.run(
        ["semgrep", "scan", "--metrics=off", "--config", str(RULE), "--json", str(target)],
        capture_output=True, text=True, timeout=180,
    )
    return json.loads(proc.stdout)["results"]


def test_rule_flags_vulnerable_fixture():
    results = _scan(FIXTURES / "vulnerable")
    assert len(results) == 1, "rule should flag the unprotected controller once"


def test_rule_ignores_safe_fixture():
    results = _scan(FIXTURES / "safe")
    assert results == [], "rule must not flag a controller that checks ownership"