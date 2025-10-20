# Temporary debug script to check workflow function availability
. .\scripts\workflow.ps1

Write-Host "Testing Invoke-Step function availability..." -ForegroundColor Cyan
for ($i = 0; $i -le 12; $i++) {
    $cmd = Get-Command "Invoke-Step$i" -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "Invoke-Step${i} FOUND" -ForegroundColor Green
    } else {
        Write-Host "Invoke-Step${i} MISSING" -ForegroundColor Red
    }
}

