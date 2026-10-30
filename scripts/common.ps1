$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Import-DotEnv {
    param([string]$Path = (Join-Path $ProjectRoot ".env"))
    if (-not (Test-Path $Path)) {
        throw "Missing .env. Run: Copy-Item .env.example .env"
    }
    foreach ($line in Get-Content $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) { continue }
        $key, $value = $trimmed.Split("=", 2)
        [Environment]::SetEnvironmentVariable($key.Trim(), $value.Trim().Trim('"').Trim("'"), "Process")
    }
}

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found in PATH."
    }
}

function Get-CrapiRoot {
    return Join-Path $ProjectRoot ".cache\crapi"
}

function Get-CrapiComposeFile {
    return Join-Path (Get-CrapiRoot) "deploy\docker\docker-compose.yml"
}

function Assert-LocalUrl {
    param([string]$Url)
    $uri = [Uri]$Url
    if ($uri.Host -notin @("localhost", "127.0.0.1", "host.docker.internal")) {
        throw "Refusing non-local target: $Url"
    }
}

