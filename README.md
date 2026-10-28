# Comparative SAST/DAST Evaluation for REST APIs

This repository implements a controlled comparison of Semgrep (SAST) and OWASP ZAP (DAST) against a pinned, local OWASP crAPI deployment. It also contains an explicit two-user BOLA test because a generic active scan cannot reliably infer object ownership.

## Research questions

1. Which eligible crAPI scenarios are detected by Semgrep and ZAP, and what scenario coverage and finding precision does each achieve?
2. To what extent do standard and project-extended static and dynamic configurations detect selected BOLA scenarios?
3. How much additional coverage is obtained by combining SAST and DAST, and what execution time does it require?

## Safety boundary

The scripts refuse non-local crAPI targets by default. Run active tests only against the Docker deployment created by this project. Never point them at a third-party or production system.

## Windows prerequisites

- Windows 10/11 with Docker Desktop running in Linux-container mode
- Git
- PowerShell 7 recommended (Windows PowerShell 5.1 also works for the main scripts)
- Python 3.11 or 3.12
- At least 8 GB RAM; 12-16 GB is preferable

Semgrep and ZAP are executed as containers; they do not need separate desktop installations.

## First run (PowerShell)

```powershell
Copy-Item .env.example .env
./scripts/bootstrap.ps1
./scripts/start-crapi.ps1
python -m src.bola_harness --config ground_truth/bola_cases.json
./scripts/run-semgrep.ps1
./scripts/run-zap.ps1
python -m src.pipeline
```

The first run downloads crAPI and container images. Reports are written under `results/`.

Run everything after bootstrap with:

```powershell
./scripts/run-experiment.ps1
```

Stop the lab with:

```powershell
./scripts/stop-crapi.ps1
```

## Experimental conditions

- **S0:** published Semgrep rules selected in `sast/configs/standard.txt`
- **S1:** S0 plus project rules in `sast/rules/`
- **D0:** authenticated ZAP API scan using the pinned OpenAPI document
- **D1:** D0 plus explicit two-account BOLA requests from `src/bola_harness.py`

S0 and S1 are saved independently. D1 is not described as a native ZAP discovery: it is a targeted dynamic authorization test and its traffic can be inspected through ZAP in later iterations.

## Reproducibility

The crAPI source commit, public Semgrep-rule commit, and Semgrep/ZAP multi-platform image digests are pinned in `.env.example`. `bootstrap.ps1` records the resolved commits and actual crAPI service image identifiers. The pipeline preserves raw output separately from normalized findings and generated metrics. Do not manually edit raw results.

## Tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Team ownership

- Member 1: crAPI bootstrap, ground truth, normalization, metrics and reporting
- Member 2: Semgrep runner, rule selection, custom rules and static-analysis validation
- Member 3: ZAP runner, authentication, BOLA harness and dynamic-analysis validation

Use feature branches and substantive pull requests. Commit count is not a scientific or fair measure of contribution; the contribution record is maintained in `docs/contribution-record.md`.

## Current scope

The checked-in ground truth begins with the reproducible vehicle-location BOLA scenario. Additional crAPI scenarios must be manually validated and added with explicit evidence before they enter metric denominators. This prevents undocumented assumptions from being presented as ground truth.

