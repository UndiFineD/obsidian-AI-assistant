# Validate PowerShell syntax
$errors = $null
$tokens = $null
$content = Get-Content .\scripts\workflow.ps1 -Raw

[void][System.Management.Automation.PSParser]::Tokenize($content, [ref]$tokens, [ref]$errors)

if ($errors -and $errors.Count -gt 0) {
    Write-Host "Syntax Errors Found:" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "Line $($err.Token.StartLine): $($err.Message)" -ForegroundColor Yellow
    }
    exit 1
} else {
    Write-Host "No syntax errors detected" -ForegroundColor Green
    exit 0
}
