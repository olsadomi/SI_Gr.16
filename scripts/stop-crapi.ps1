. (Join-Path $PSScriptRoot "common.ps1")
Import-DotEnv
$compose = Get-CrapiComposeFile
if (Test-Path $compose) {
    docker compose -f $compose down
}

