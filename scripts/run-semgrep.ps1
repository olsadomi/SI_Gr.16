. (Join-Path $PSScriptRoot "common.ps1")
Import-DotEnv
Assert-Command docker

$crapiRoot = Get-CrapiRoot
if (-not (Test-Path $crapiRoot)) { throw "crAPI source missing. Run bootstrap.ps1." }
$baselineRules = Join-Path $ProjectRoot ".cache\semgrep-rules"
if (-not (Test-Path $baselineRules)) { throw "Pinned Semgrep rules missing. Run bootstrap.ps1." }
$raw = Join-Path $ProjectRoot "results\raw"
New-Item -ItemType Directory -Force -Path $raw | Out-Null

$standardRules = Get-Content (Join-Path $ProjectRoot "sast\configs\standard.txt") | Where-Object { $_.Trim() }
function Invoke-SemgrepCondition {
    param([string]$Condition, [bool]$IncludeCustom)
    $outputName = "semgrep-$($Condition.ToLower()).json"
    $arguments = @("run", "--rm", "-v", "${crapiRoot}:/src:ro", "-v", "${raw}:/out", "-v", "${baselineRules}:/baseline:ro", $env:SEMGREP_IMAGE, "semgrep", "scan", "--json", "--output", "/out/$outputName", "--metrics=off")
    foreach ($rule in $standardRules) { $arguments += @("--config", $rule) }
    if ($IncludeCustom) {
        $rules = Join-Path $ProjectRoot "sast\rules"
        $arguments = @("run", "--rm", "-v", "${crapiRoot}:/src:ro", "-v", "${raw}:/out", "-v", "${baselineRules}:/baseline:ro", "-v", "${rules}:/rules:ro", $env:SEMGREP_IMAGE, "semgrep", "scan", "--json", "--output", "/out/$outputName", "--metrics=off")
        foreach ($rule in $standardRules) { $arguments += @("--config", $rule) }
        $arguments += @("--config", "/rules")
    }
    $arguments += @("--exclude", "**/vendor/**", "--exclude", "**/node_modules/**", "/src/services")
    $watch = [Diagnostics.Stopwatch]::StartNew()
    & docker @arguments
    $exit = $LASTEXITCODE
    $watch.Stop()
    if ($exit -notin @(0, 1)) { throw "Semgrep $Condition failed with exit code $exit" }
    @{condition=$Condition; duration_seconds=$watch.Elapsed.TotalSeconds; exit_code=$exit; image=$env:SEMGREP_IMAGE} |
        ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $raw "semgrep-$($Condition.ToLower())-metadata.json")
}

Invoke-SemgrepCondition -Condition "S0" -IncludeCustom $false
Invoke-SemgrepCondition -Condition "S1" -IncludeCustom $true
Write-Host "Semgrep S0 and S1 complete."

