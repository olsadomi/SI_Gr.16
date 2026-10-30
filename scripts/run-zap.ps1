. (Join-Path $PSScriptRoot "common.ps1")
Import-DotEnv
Assert-Command docker
Assert-Command python
Assert-LocalUrl $env:CRAPI_BASE_URL

$crapiRoot = Get-CrapiRoot
$specDir = Join-Path $crapiRoot "openapi-spec"
$raw = Join-Path $ProjectRoot "results\raw"
New-Item -ItemType Directory -Force -Path $raw | Out-Null

$token = (& python -m src.get_token).Trim()
if (-not $token) { throw "Could not obtain crAPI authentication token." }

$zapOptions = "-silent -config replacer.full_list(0).description=crapi-auth -config replacer.full_list(0).enabled=true -config replacer.full_list(0).matchtype=REQ_HEADER -config replacer.full_list(0).matchregex=false -config replacer.full_list(0).matchstr=Authorization -config replacer.full_list(0).replacement=Bearer%20$token"
$watch = [Diagnostics.Stopwatch]::StartNew()
docker run --rm `
    --add-host=host.docker.internal:host-gateway `
    -v "${specDir}:/zap/wrk/openapi:ro" `
    -v "${raw}:/zap/wrk/results:rw" `
    $env:ZAP_IMAGE zap-api-scan.py `
    -t /zap/wrk/openapi/crapi-openapi-spec.json `
    -f openapi `
    -O http://host.docker.internal:8888 `
    -J /zap/wrk/results/zap.json `
    -r /zap/wrk/results/zap.html `
    -T $env:SCAN_TIMEOUT_MINUTES `
    -I `
    -z $zapOptions
$exit = $LASTEXITCODE
$watch.Stop()
if ($exit -notin @(0, 1, 2)) { throw "ZAP scan failed with exit code $exit" }
@{condition="D0"; duration_seconds=$watch.Elapsed.TotalSeconds; exit_code=$exit; image=$env:ZAP_IMAGE} |
    ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $raw "zap-metadata.json")
Write-Host "ZAP scan complete."

