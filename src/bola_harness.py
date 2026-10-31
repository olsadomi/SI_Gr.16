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


def _build_variables() -> dict[str, str]:
    """Collect the known victim object identifiers from the environment.

    victim_vehicle_id is required (Challenge 1). Optional identifiers such as
    victim_report_id (Challenge 2) are only added when configured, so cases that
    do not need them still run.
    """
    variables = {"victim_vehicle_id": setting("CRAPI_VICTIM_VEHICLE_ID")}
    for env_name, var_name in (("CRAPI_VICTIM_REPORT_ID", "victim_report_id"),):
        value = setting(env_name, "")
        if value:
            variables[var_name] = value
    return variables


def _evaluate(case: dict[str, Any], variables: dict[str, str], baseline: Any, attack: Any) -> tuple[bool, dict[str, Any]]:
    """Return (vulnerable, oracle_detail) for a single case.

    Two oracle modes are supported:
      * identifier_disclosure (default): the attacker response must echo a known
        victim identifier (e.g. carId == victim_vehicle_id). Strong evidence.
      * cross_user_access: the attacker simply receives 200 for an object the
        victim owns. Used when the response has no stable identifier to match.
    """
    mode = case.get("oracle_mode", "identifier_disclosure")
    baseline_ok = baseline.status == 200
    attack_ok = attack.status == 200
    detail: dict[str, Any] = {
        "oracle_mode": mode,
        "baseline_access_confirmed": baseline_ok,
        "protected_status_expected": attack.status in case["protected_statuses"],
    }

    if mode == "cross_user_access":
        vulnerable = baseline_ok and attack_ok
        detail["cross_user_access_succeeded"] = vulnerable
        detail["vulnerable"] = vulnerable
        return vulnerable, detail

    # identifier_disclosure (default, backward compatible)
    attack_json: Any = None
    try:
        attack_json = attack.json()
    except Exception:
        pass
    expected_value = variables[case["expected_identifier_variable"]]
    leaked = (
        isinstance(attack_json, dict)
        and str(attack_json.get(case["expected_identifier_field"])) == str(expected_value)
    )
    vulnerable = baseline_ok and attack_ok and leaked
    detail["victim_identifier_disclosed"] = leaked
    detail["vulnerable"] = vulnerable
    return vulnerable, detail


def run(config_path: Path, output_path: Path) -> dict[str, Any]:
    base_url = setting("CRAPI_BASE_URL", "http://localhost:8888").rstrip("/")
    require_local_target(base_url)
    attacker_email = setting("CRAPI_ATTACKER_EMAIL")
    victim_email = setting("CRAPI_VICTIM_EMAIL")
    variables = _build_variables()
    started = time.perf_counter()

    attacker_token = login(base_url, attacker_email, setting("CRAPI_ATTACKER_PASSWORD"))
    victim_token = login(base_url, victim_email, setting("CRAPI_VICTIM_PASSWORD"))
    results: list[dict[str, Any]] = []

    for case in read_json(config_path)["cases"]:
        try:
            path = case["path"].format(**variables)
        except KeyError as missing:
            # A required victim identifier is not configured; record and skip.
            results.append(
                {
                    "scenario_id": case["scenario_id"],
                    "rule_id": "bola-ownership-swap",
                    "skipped": f"missing identifier variable {missing}; set it in .env",
                    "oracle": {"vulnerable": False, "oracle_mode": case.get("oracle_mode", "identifier_disclosure")},
                }
            )
            continue

        url = f"{base_url}{path}"
        baseline = request_json(case["method"], url, token=victim_token)
        attack = request_json(case["method"], url, token=attacker_token)
        vulnerable, oracle = _evaluate(case, variables, baseline, attack)

        attack_body: Any
        try:
            attack_body = attack.json()
        except Exception:
            attack_body = attack.body[:1000]

        results.append(
            {
                "scenario_id": case["scenario_id"],
                "rule_id": "bola-ownership-swap",
                "request": {"method": case["method"], "path": path, "acting_user": attacker_email},
                "baseline": {"status": baseline.status, "owner": victim_email},
                "attack": {"status": attack.status, "response": _redact(attack_body)},
                "oracle": oracle,
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