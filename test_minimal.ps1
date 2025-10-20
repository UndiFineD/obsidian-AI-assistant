# Minimal test of Step4 and Step5 functions
function Invoke-Step4 {
    param([string]$ChangePath, [string]$Title)
    Write-Host "Step 4 executed"
    return $true
}

function Invoke-Step5 {
    param([string]$ChangePath, [string]$Title)
    $template = @"
# Test Plan: Test

## Estimated Effort
- [ ] Test item

## Content
Test content here
"@
    
    Write-Host "Template length: $($template.Length)"
    Write-Host "Step 5 executed"
    return $true
}

function Invoke-Step6 {
    param([string]$ChangePath)
    Write-Host "Step 6 executed"
    return $true
}

# Test the functions
Write-Host "Testing function definitions..." -ForegroundColor Cyan
foreach ($i in 4..6) {
    $cmd = Get-Command "Invoke-Step$i" -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "Invoke-Step${i} FOUND" -ForegroundColor Green
    } else {
        Write-Host "Invoke-Step${i} MISSING" -ForegroundColor Red
    }
}
