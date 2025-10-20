# Test dot-sourcing the workflow script with error details
try {
    . .\scripts\workflow.ps1
    Write-Host "Script loaded successfully" -ForegroundColor Green
    
    # Check for Invoke-Step5
    $step5 = Get-Command Invoke-Step5 -ErrorAction SilentlyContinue
    if ($step5) {
        Write-Host "Invoke-Step5: FOUND" -ForegroundColor Green
    } else {
        Write-Host "Invoke-Step5: MISSING" -ForegroundColor Red
        Write-Host "All functions loaded:" -ForegroundColor Yellow
        Get-Command Invoke-Step* | Select-Object -ExpandProperty Name
    }
} catch {
    Write-Host "ERROR loading script:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
}
