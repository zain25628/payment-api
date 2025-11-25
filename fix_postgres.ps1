# fix_postgres.ps1
# Robust script to fix PostgreSQL authentication and create 'payment_gateway'

$ErrorActionPreference = "Stop"

Write-Host "Starting PostgreSQL repair script..."

# Technical configuration (do not change unless necessary)
$pgBin = "C:\Program Files\PostgreSQL\16\bin"
$dataDir = "C:\PostgreSQL\data"
$pgHba = Join-Path $dataDir "pg_hba.conf"
$backupSuffix = ".bak_fix_script"

function Restore-Backup {
    param(
        [string]$pgHbaPath
    )
    $bak = "$pgHbaPath$backupSuffix"
    if (Test-Path $bak) {
        try {
            Copy-Item $bak $pgHbaPath -Force
            Write-Host "Restored original pg_hba.conf from backup."
        } catch {
            Write-Warning "Failed to restore pg_hba.conf from backup: $_"
        }
    } else {
        Write-Warning "Backup not found; cannot restore pg_hba.conf: $bak"
    }
}

try {
    # Verify binaries folder
    if (-not (Test-Path -Path $pgBin -PathType Container)) {
        Write-Error "PostgreSQL binaries not found at $pgBin. Aborting."
        exit 1
    }

    # Verify data dir and postgresql.conf
    $postConf = Join-Path $dataDir "postgresql.conf"
    if (-not (Test-Path -Path $postConf -PathType Leaf)) {
        Write-Error "postgresql.conf not found at $postConf. Aborting."
        exit 1
    }

    #  Stop any running PostgreSQL processes
    Write-Host "Stopping existing PostgreSQL processes if any..."
    Stop-Process -Name postgres -Force -ErrorAction SilentlyContinue
    Stop-Process -Name pg_ctl -Force -ErrorAction SilentlyContinue

    # Ensure pg_hba exists
    if (-not (Test-Path -Path $pgHba -PathType Leaf)) {
        Write-Error "pg_hba.conf not found at $pgHba. Aborting."
        exit 1
    }

    # Backup pg_hba.conf if not already backed up
    $backupPath = "$pgHba$backupSuffix"
    if (-not (Test-Path $backupPath)) {
        Copy-Item $pgHba $backupPath
        Write-Host "Backed up pg_hba.conf to $backupPath"
    } else {
        Write-Host "Backup already exists at $backupPath"
    }

    # Read and modify pg_hba.conf to allow TRUST from localhost
    Write-Host "Modifying pg_hba.conf to allow TRUST from 127.0.0.1/32..."
    $lines = Get-Content -Path $pgHba -ErrorAction Stop
    $modified = @()
    foreach ($line in $lines) {
        if ($line -match "^\s*#") {
            $modified += $line
            continue
        }
        if ($line -match "\bhost\b" -and $line -match "127\.0\.0\.1/32") {
            # comment out the existing host 127.0.0.1/32 line
            $modified += ("# " + $line)
        } else {
            $modified += $line
        }
    }
    # Append the trust line if not already present
    $trustLine = "host    all             all             127.0.0.1/32            trust"
    if (-not ($modified -contains $trustLine)) {
        $modified += $trustLine
        Write-Host "Appended TRUST line to pg_hba.conf"
    } else {
        Write-Host "TRUST line already present in pg_hba.conf"
    }
    # Write back
    try {
        Set-Content -Path $pgHba -Value $modified -Force
        Write-Host "pg_hba.conf updated successfully."
    } catch {
        Write-Error "Failed to write pg_hba.conf: $_"
        Restore-Backup -pgHbaPath $pgHba
        exit 1
    }

    # Start PostgreSQL in normal mode (now with TRUST rule)
    Write-Host "Starting PostgreSQL in normal mode using data directory $dataDir..."
    $pgCtl = Join-Path $pgBin 'pg_ctl.exe'
    $logFile = Join-Path $dataDir "fix_script_log.txt"
    & "$pgCtl" start -D $dataDir -l $logFile | Out-Null
    Start-Sleep -Seconds 4

    # Test connection using TRUST auth
    Write-Host "Testing connection as postgres with TRUST auth..."
    $psql = Join-Path $pgBin 'psql.exe'
    try {
        & "$psql" -U postgres -h 127.0.0.1 -d postgres -c "SELECT version();"
    } catch {
        Write-Warning "Connection test failed: $_"
        Write-Host "Stopping PostgreSQL and restoring original pg_hba.conf..."
        & "$pgCtl" stop -D $dataDir -m fast | Out-Null
        Start-Sleep -Seconds 3
        Restore-Backup -pgHbaPath $pgHba
        exit 1
    }

    # Alter postgres password
    Write-Host "Altering postgres password..."
    try {
        & "$psql" -U postgres -h 127.0.0.1 -d postgres -c "ALTER USER postgres WITH PASSWORD 'password';"
    } catch {
        Write-Warning "Failed to alter password: $_"
        Write-Host "Stopping PostgreSQL and restoring original pg_hba.conf..."
        & "$pgCtl" stop -D $dataDir -m fast | Out-Null
        Start-Sleep -Seconds 3
        Restore-Backup -pgHbaPath $pgHba
        exit 1
    }

    # Stop PostgreSQL after password reset
    Write-Host "Stopping PostgreSQL after password reset..."
    & "$pgCtl" stop -D $dataDir -m fast | Out-Null
    Start-Sleep -Seconds 3

    # Restore original pg_hba.conf
    Write-Host "Restoring original pg_hba.conf..."
    try {
        Copy-Item "$pgHba$backupSuffix" $pgHba -Force
    } catch {
        Write-Warning "Failed to restore pg_hba.conf from backup: $_"
        exit 1
    }

    # Start PostgreSQL again (normal mode)
    Write-Host "Starting PostgreSQL with restored pg_hba.conf..."
    $logFileFinal = Join-Path $dataDir "fix_script_log_final.txt"
    & "$pgCtl" start -D $dataDir -l $logFileFinal | Out-Null
    Start-Sleep -Seconds 4

    # Create database payment_gateway using the new password
    Write-Host "Creating database 'payment_gateway' if it does not exist..."
    $createdb = Join-Path $pgBin 'createdb.exe'
    $env:PGPASSWORD = "password"
    try {
        & "$createdb" -U postgres -h 127.0.0.1 payment_gateway
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "createdb returned exit code $LASTEXITCODE. Database may already exist or creation failed."
        } else {
            Write-Host "Database 'payment_gateway' created (or already existed)."
        }
    } catch {
        Write-Warning "createdb failed: $_"
    } finally {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }

    # Final validation: connect to payment_gateway with new password
    $env:PGPASSWORD = "password"
    Write-Host "Validating connection to 'payment_gateway'..."
    try {
        & "$psql" -U postgres -h 127.0.0.1 -d payment_gateway -c "SELECT current_database();"
        $validateExit = $LASTEXITCODE
    } catch {
        $validateExit = 1
    } finally {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    }

    if ($validateExit -ne 0) {
        Write-Error "Validation failed: could not connect to payment_gateway with the new password."
        exit 1
    }

    Write-Host "PostgreSQL password reset and 'payment_gateway' database are ready to use." -ForegroundColor Green

} catch {
    Write-Error "An unexpected error occurred: $_"
    try {
        Restore-Backup -pgHbaPath $pgHba
    } catch {
        Write-Warning "Failed to restore backup during error handling: $_"
    }
    exit 1
}
