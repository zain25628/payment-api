# Dev stack starter: local Postgres via pg_ctl, then venv python (no Docker)
$ErrorActionPreference = 'Stop'

# Paths and configuration
$pgCtlPath = 'C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe'
$psqlPath  = 'C:\Program Files\PostgreSQL\16\bin\psql.exe'
$dataDir   = 'C:\PostgreSQL\data'
$logFile   = 'C:\PostgreSQL\data\manual_start.log'

# Ensure working directory is the project root
try {
    Set-Location $PSScriptRoot
    Write-Host "Working directory: $PSScriptRoot" -ForegroundColor Green
} catch {
    Write-Host "Warning: couldn't set working directory to $($PSScriptRoot): $_" -ForegroundColor Yellow
}

# Helper: check DB connectivity using psql
function Test-PostgresReachable {
    if (-not (Test-Path $psqlPath)) { return $false }
    try {
        & $psqlPath -U postgres -h 127.0.0.1 -d payment_gateway -c "SELECT 1;" > $null 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

# 1) Start PostgreSQL if necessary
Write-Host "Checking for running postgres process..." -ForegroundColor Green
$postgresProc = Get-Process -Name postgres -ErrorAction SilentlyContinue
if ($postgresProc) {
    Write-Host "PostgreSQL process detected. Skipping pg_ctl start." -ForegroundColor Yellow
} elseif (Test-PostgresReachable) {
    Write-Host "PostgreSQL is reachable via psql. Skipping pg_ctl start." -ForegroundColor Yellow
} else {
    Write-Host "Starting PostgreSQL with pg_ctl..." -ForegroundColor Green
    if (-not (Test-Path $pgCtlPath)) {
        Write-Host "ERROR: pg_ctl not found at '$pgCtlPath'. Please install Postgres or correct the path." -ForegroundColor Red
        exit 1
    }

    try {
        & "$pgCtlPath" start -D "$dataDir" -l "$logFile"
    } catch {
        Write-Host "pg_ctl start failed: $_" -ForegroundColor Red
        Write-Host "Examine the log at $logFile for details." -ForegroundColor Red
        exit 1
    }

    Start-Sleep -Seconds 2
    if (Test-PostgresReachable) {
        Write-Host "PostgreSQL is up and reachable." -ForegroundColor Green
    } else {
        Write-Host "ERROR: PostgreSQL is not reachable after pg_ctl start. Check $logFile" -ForegroundColor Red
        exit 1
    }
}

# 2) Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
$activatePath = Join-Path $PSScriptRoot 'venv\\Scripts\\Activate.ps1'
if (Test-Path $activatePath) {
    try {
        . $activatePath
    } catch {
        Write-Host "Warning: failed to dot-source Activate.ps1: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: venv Activate.ps1 not found at $activatePath" -ForegroundColor Yellow
}

# Prefer venv python when available
$venvPython = Join-Path $PSScriptRoot 'venv\\Scripts\\python.exe'
if (Test-Path $venvPython) { $pythonExe = $venvPython } else { $pythonExe = 'python'; Write-Host "Using system python" -ForegroundColor Yellow }

# 3) Run Alembic migrations
Write-Host "Running migrations (alembic upgrade head)..." -ForegroundColor Green
try {
    & $pythonExe -m alembic upgrade head
} catch {
    Write-Host "Alembic migrations failed: $_" -ForegroundColor Red
    exit 1
}

# 4) Seed development data
Write-Host "Seeding development data..." -ForegroundColor Green
try {
    & $pythonExe -m app.seed_dev_data
} catch {
    Write-Host "Seeding failed: $_" -ForegroundColor Red
    exit 1
}

# 5) Start uvicorn with reload
Write-Host "Starting uvicorn (app.main:app) --reload" -ForegroundColor Green
try {
    & $pythonExe -m uvicorn app.main:app --reload
} catch {
    Write-Host "Failed to start uvicorn: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Dev stack is up. Open http://127.0.0.1:8000/docs" -ForegroundColor Green
