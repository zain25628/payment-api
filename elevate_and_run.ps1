try {
    $script = Join-Path $PSScriptRoot 'dev_start_stack.ps1'
    if (-not (Test-Path $script)) {
        Write-Host "Cannot find dev_start_stack.ps1 in project root: $script" -ForegroundColor Red
        exit 1
    }

    Write-Host "Requesting elevation to run dev_start_stack.ps1..."
    $arg = "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
    Start-Process -FilePath "powershell.exe" -ArgumentList $arg -Verb RunAs -WorkingDirectory $PSScriptRoot -Wait
} catch {
    Write-Host "Failed to request elevation or run script: $_" -ForegroundColor Red
    exit 1
}
