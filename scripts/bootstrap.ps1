. (Join-Path $PSScriptRoot "common.ps1")
Import-DotEnv
Assert-Command git
Assert-Command docker
Assert-Command python

docker version | Out-Null
docker compose version | Out-Null

$crapiRoot = Get-CrapiRoot
if (-not (Test-Path (Join-Path $crapiRoot ".git"))) {
    New-Item -ItemType Directory -Force -Path (Split-Path $crapiRoot) | Out-Null
    git clone $env:CRAPI_REPOSITORY $crapiRoot
}

git -C $crapiRoot fetch --tags origin
git -C $crapiRoot checkout --detach $env:CRAPI_REF
$resolved = (git -C $crapiRoot rev-parse HEAD).Trim()
if ($resolved -ne $env:CRAPI_REF) { throw "crAPI checkout mismatch: expected $($env:CRAPI_REF), got $resolved" }

$semgrepRulesRoot = Join-Path $ProjectRoot ".cache\semgrep-rules"
if (-not (Test-Path (Join-Path $semgrepRulesRoot ".git"))) {
    git clone $env:SEMGREP_RULES_REPOSITORY $semgrepRulesRoot
}
git -C $semgrepRulesRoot fetch --tags origin
git -C $semgrepRulesRoot checkout --detach $env:SEMGREP_RULES_REF
$resolvedRules = (git -C $semgrepRulesRoot rev-parse HEAD).Trim()
if ($resolvedRules -ne $env:SEMGREP_RULES_REF) { throw "Semgrep rules mismatch: expected $($env:SEMGREP_RULES_REF), got $resolvedRules" }

$metadata = @{
    crapi_repository = $env:CRAPI_REPOSITORY
    crapi_commit = $resolved
    semgrep_rules_commit = $resolvedRules
    semgrep_image = $env:SEMGREP_IMAGE
    zap_image = $env:ZAP_IMAGE
    bootstrapped_at_utc = [DateTime]::UtcNow.ToString("o")
} | ConvertTo-Json
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "results\raw") | Out-Null
$metadata | Set-Content -Encoding utf8 (Join-Path $ProjectRoot "results\raw\environment.json")

docker pull $env:SEMGREP_IMAGE
docker pull $env:ZAP_IMAGE
docker compose -f (Get-CrapiComposeFile) pull

# Capture immutable local image identifiers because the upstream crAPI compose file
# currently uses a moving "latest" tag. The recorded IDs define the actual pilot.
$imageLock = docker compose -f (Get-CrapiComposeFile) images --format json
$imageLock | Set-Content -Encoding utf8 (Join-Path $ProjectRoot "results\raw\crapi-images.jsonl")
docker image inspect $env:SEMGREP_IMAGE $env:ZAP_IMAGE --format '{{json .}}' |
    Set-Content -Encoding utf8 (Join-Path $ProjectRoot "results\raw\tool-images.jsonl")
Write-Host "Bootstrap complete at crAPI commit $resolved"

