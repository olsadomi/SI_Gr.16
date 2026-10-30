. (Join-Path $PSScriptRoot "common.ps1")
Import-DotEnv
Assert-Command docker
Assert-LocalUrl $env:CRAPI_BASE_URL

$compose = Get-CrapiComposeFile
if (-not (Test-Path $compose)) { throw "crAPI is not bootstrapped. Run scripts/bootstrap.ps1 first." }

docker compose -f $compose up -d
$deadline = (Get-Date).AddMinutes(8)
do {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $env:CRAPI_BASE_URL -TimeoutSec 5
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
            Write-Host "crAPI is ready at $($env:CRAPI_BASE_URL)"
            exit 0
        }
    } catch { Start-Sleep -Seconds 5 }
} while ((Get-Date) -lt $deadline)

docker compose -f $compose ps
throw "crAPI did not become ready before the timeout. Inspect: docker compose -f `"$compose`" logs"

