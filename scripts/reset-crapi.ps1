. (Join-Path $PSScriptRoot "common.ps1")
Import-DotEnv
$compose = Get-CrapiComposeFile
if (-not (Test-Path $compose)) { throw "crAPI is not bootstrapped." }

# This intentionally deletes only Docker volumes belonging to the pinned local lab.
docker compose -f $compose down --volumes
& (Join-Path $PSScriptRoot "start-crapi.ps1")

