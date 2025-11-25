Write-Host "=== FastAPI Dev Setup & Run ==="

# Ensure script runs from project root
if ($PSScriptRoot) {
    Set-Location $PSScriptRoot
} else {
    Write-Host "Warning: Could not determine script directory. Running in current directory."
}

# Check venv
if (-not (Test-Path -Path ".\venv" -PathType Container)) {
    Write-Error "Virtual environment 'venv' not found. Create it with: python -m venv venv"
    exit 1
}

# Activate virtual environment (PowerShell)
$activatePath = Join-Path -Path (Join-Path $PWD "venv") -ChildPath "Scripts\Activate.ps1"
if (-not (Test-Path $activatePath)) {
    Write-Error "Activation script not found at $activatePath"
    exit 1
}

try {
    Write-Host "Activating virtual environment..."
    . $activatePath
} catch {
    Write-Error "Failed to activate virtual environment: $_"
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..."
try {
    python -m pip install --upgrade pip
} catch {
    Write-Warning "Failed to upgrade pip: $_"
}

# Install requirements
if (-not (Test-Path -Path ".\requirements.txt" -PathType Leaf)) {
    Write-Error "requirements.txt not found in project root. Cannot install dependencies."
    exit 1
}

Write-Host "Installing dependencies from requirements.txt..."
try {
    pip install -r requirements.txt
} catch {
    Write-Error "Failed to install dependencies: $_"
    exit 1
}

# Verify DATABASE_URL via app.config (loads .env)
Write-Host "Verifying DATABASE_URL via app.config (Pydantic)..."
try {
    python -c "from app.config import get_settings; import sys
try:
    settings = get_settings()
    print('DATABASE_URL =', repr(settings.DATABASE_URL))
    if not settings.DATABASE_URL:
        print('ERROR: DATABASE_URL is empty. Please configure .env before running the app.')
        sys.exit(2)
except Exception as e:
    print('ERROR while loading settings:', e)
    sys.exit(1)"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Settings check failed (see output above). Aborting."
        exit 1
    }
} catch {
    Write-Warning "Could not run settings check: $_"
}

# Check for uvicorn import
Write-Host "Checking uvicorn availability..."
& python -c "import importlib,sys
try:
    importlib.import_module('uvicorn')
except Exception as e:
    sys.exit(2)";
if ($LASTEXITCODE -ne 0) {
    Write-Warning "uvicorn import failed. Ensure fastapi and uvicorn are listed in requirements.txt."
}

Write-Host "Starting uvicorn (reload mode). Use Ctrl+C to stop." -ForegroundColor Cyan
try {
    uvicorn app.main:app --reload
} catch {
    Write-Error "Failed to start uvicorn: $_"
    Write-Host "Tip: Run 'python -c "import uvicorn"' inside the venv to verify installation." 
    exit 1
}
