<#
    archive_project.ps1

    Create a clean ZIP snapshot of the project on the current user's Desktop.

    How to run (from PowerShell):
      cd "C:\Users\zaink\OneDrive\Desktop\api"
      .\archive_project.ps1

    The script will not modify any files. It excludes virtualenvs, VCS and editor
    folders, caches, compiled files, logs, executables and the real `.env` file.
#>

Param()

$ErrorActionPreference = 'Stop'

# Project root (assumed)
$ProjectPath = "C:\Users\zaink\OneDrive\Desktop\api"

# User Desktop
$DesktopPath = [Environment]::GetFolderPath("Desktop")

if (-not (Test-Path $ProjectPath)) {
    Write-Host "Project path not found: $ProjectPath" -ForegroundColor Red
    exit 1
}

Push-Location $ProjectPath
try {
    # Timestamp and zip filename
    $timestamp = (Get-Date).ToString('yyyyMMdd_HHmm')
    $baseName = "api_snapshot_$timestamp"
    $zipFileName = "$baseName.zip"
    $zipPath = Join-Path $DesktopPath $zipFileName

    # If exists, append numeric suffix
    $suffix = 1
    while (Test-Path $zipPath) {
        $suffix++
        $zipFileName = "${baseName}_$suffix.zip"
        $zipPath = Join-Path $DesktopPath $zipFileName
    }

    Write-Host "Starting archive of project: $ProjectPath" -ForegroundColor Green
    Write-Host "Will create zip: $zipPath" -ForegroundColor Green

    # Exclusion lists
    $excludeDirs = @('venv', '.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.idea', '.vscode')
    $excludeFilePatterns = @('*.pyc', '*.pyo', '*.log', '*.exe')
    $rootEnvFile = Join-Path $ProjectPath '.env'

    Write-Host "Excluding directories: $($excludeDirs -join ', ')" -ForegroundColor Yellow
    Write-Host "Excluding file patterns: $($excludeFilePatterns -join ', ')" -ForegroundColor Yellow
    Write-Host "Excluding root file: $rootEnvFile" -ForegroundColor Yellow

    # Gather files recursively, excluding directories and patterns
    $allFiles = Get-ChildItem -Recurse -File -Force

    $filesToArchive = @()
    foreach ($f in $allFiles) {
        $full = $f.FullName

        # Exclude the root .env file exactly
        if ($full -eq $rootEnvFile) {
            continue
        }

        # Exclude by directory name anywhere in the path
        $skip = $false
        foreach ($d in $excludeDirs) {
            if ($full -like "*\$d\*" -or $full -like "*\$d") {
                $skip = $true
                break
            }
        }
        if ($skip) { continue }

        # Exclude by filename pattern
        foreach ($pat in $excludeFilePatterns) {
            if ($f.Name -like $pat) { $skip = $true; break }
        }
        if ($skip) { continue }

        # Keep the file (store as relative path)
        $rel = $full.Substring($ProjectPath.Length).TrimStart('\')
        # Prepend .\ to ensure Compress-Archive uses relative paths
        $filesToArchive += (Join-Path '.\' $rel)
    }

    if ($filesToArchive.Count -eq 0) {
        Write-Host "No files found to archive after exclusions." -ForegroundColor Yellow
        exit 0
    }

    Write-Host "Creating archive (this may take a moment)..." -ForegroundColor Green
    try {
        Compress-Archive -Path $filesToArchive -DestinationPath $zipPath -Force
    } catch {
        Write-Host "Failed to create archive: $_" -ForegroundColor Red
        exit 1
    }

    Write-Host "Archive created successfully: $zipPath" -ForegroundColor Green
} finally {
    Pop-Location
}

exit 0
