. (Join-Path $PSScriptRoot "common.ps1")
Import-DotEnv
Assert-Command python

& (Join-Path $PSScriptRoot "start-crapi.ps1")
if ($LASTEXITCODE -ne 0) { throw "crAPI startup failed" }

& (Join-Path $PSScriptRoot "run-semgrep.ps1")
if ($LASTEXITCODE -ne 0) { throw "Semgrep experiment failed" }

& (Join-Path $PSScriptRoot "run-zap.ps1")
if ($LASTEXITCODE -ne 0) { throw "ZAP experiment failed" }

python -m src.bola_harness --config ground_truth/bola_cases.json
if ($LASTEXITCODE -ne 0) { throw "BOLA harness failed" }

python -m src.pipeline
if ($LASTEXITCODE -ne 0) { throw "Analysis pipeline failed" }
Write-Host "Experiment complete. See results/reports/metrics.json"

