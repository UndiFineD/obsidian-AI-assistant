# Extract and analyze Invoke-Step5 function
$content = Get-Content .\scripts\workflow.ps1 -Raw

# Find the function start
$step5Start = $content.IndexOf('function Invoke-Step5 {')
if ($step5Start -lt 0) {
    Write-Host "Could not find Invoke-Step5" -ForegroundColor Red
    exit 1
}

# Find the next function start (Invoke-Step6)
$step6Start = $content.IndexOf('function Invoke-Step6 {', $step5Start + 1)
if ($step6Start -lt 0) {
    Write-Host "Could not find Invoke-Step6" -ForegroundColor Red
    exit 1
}

# Extract Step5 function
$step5Function = $content.Substring($step5Start, $step6Start - $step5Start)

Write-Host "Invoke-Step5 function extracted ($($step5Function.Length) chars)" -ForegroundColor Cyan
Write-Host ""

# Count braces
$openBraces = ($step5Function.ToCharArray() | Where-Object { $_ -eq '{' }).Count
$closeBraces = ($step5Function.ToCharArray() | Where-Object { $_ -eq '}' }).Count

Write-Host "Open braces: $openBraces" -ForegroundColor Yellow
Write-Host "Close braces: $closeBraces" -ForegroundColor Yellow

if ($openBraces -ne $closeBraces) {
    Write-Host "MISMATCH! Function has unbalanced braces" -ForegroundColor Red
} else {
    Write-Host "Braces are balanced" -ForegroundColor Green
}

# Try to parse just this function
Write-Host ""
Write-Host "Attempting to parse function..." -ForegroundColor Cyan
$errors = $null
$tokens = $null
[void][System.Management.Automation.Language.Parser]::ParseInput($step5Function, [ref]$tokens, [ref]$errors)

if ($errors -and $errors.Count -gt 0) {
    Write-Host "Parse Errors Found:" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  $($err.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "Function parses successfully!" -ForegroundColor Green
}
