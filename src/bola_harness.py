from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import ROOT, require_local_target, setting
from .http_client import login, request_json
from .io_utils import read_json, write_json


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: ("<redacted>" if key.lower() in {"token", "authorization"} else _redact(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def run(config_path: Path, output_path: Path) -> dict[str, Any]:
    base_url = setting("CRAPI_BASE_URL", "http://localhost:8888").rstrip("/")
    require_local_target(base_url)
    attacker_email = setting("CRAPI_ATTACKER_EMAIL")
    victim_email = setting("CRAPI_VICTIM_EMAIL")
    variables = {"victim_vehicle_id": setting("CRAPI_VICTIM_VEHICLE_ID")}
    started = time.perf_counter()

    attacker_token = login(base_url, attacker_email, setting("CRAPI_ATTACKER_PASSWORD"))
    victim_token = login(base_url, victim_email, setting("CRAPI_VICTIM_PASSWORD"))
    results: list[dict[str, Any]] = []

    for case in read_json(config_path)["cases"]:
        path = case["path"].format(**variables)
        url = f"{base_url}{path}"
        baseline = request_json(case["method"], url, token=victim_token)
        attack = request_json(case["method"], url, token=attacker_token)
        attack_json: Any = None
        try:
            attack_json = attack.json()
        except Exception:
            pass
        expected_value = variables[case["expected_identifier_variable"]]
        leaked_identifier = (
            isinstance(attack_json, dict)
            and str(attack_json.get(case["expected_identifier_field"])) == str(expected_value)
        )
        vulnerable = baseline.status == 200 and attack.status == 200 and leaked_identifier
        results.append(
            {
                "scenario_id": case["scenario_id"],
                "rule_id": "bola-ownership-swap",
                "request": {"method": case["method"], "path": path, "acting_user": attacker_email},
                "baseline": {"status": baseline.status, "owner": victim_email},
                "attack": {"status": attack.status, "response": _redact(attack_json if attack_json is not None else attack.body[:1000])},
                "oracle": {
                    "baseline_access_confirmed": baseline.status == 200,
                    "victim_identifier_disclosed": leaked_identifier,
                    "protected_status_expected": attack.status in case["protected_statuses"],
                    "vulnerable": vulnerable,
                },
            }
        )

    envelope = {
        "tool": "bola-harness",
        "condition": "D1",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.perf_counter() - started, 6),
        "target": base_url,
        "results": results,
    }
    write_json(output_path, envelope)
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser(description="Run authorized two-account BOLA checks against local crAPI")
    parser.add_argument("--config", type=Path, default=ROOT / "ground_truth" / "bola_cases.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "raw" / "bola.json")
    args = parser.parse_args()
    result = run(args.config, args.output)
    vulnerable = sum(item["oracle"]["vulnerable"] for item in result["results"])
    print(f"BOLA checks complete: {vulnerable}/{len(result['results'])} vulnerable; output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

