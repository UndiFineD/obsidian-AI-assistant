$path = Join-Path $PSScriptRoot 'workflow.ps1'
$errors = @()
$tokens = @()
try {
  [void][System.Management.Automation.PSParser]::Tokenize((Get-Content $path -Raw), [ref]$tokens, [ref]$errors)
} catch {
  Write-Host "Parser invocation failed: $_" -ForegroundColor Yellow
}
if ($null -ne $errors -and $errors.Count -gt 0) {
  foreach ($e in $errors) {
    Write-Host ("{0} at {1}:{2}" -f $e.Message, $e.Extent.StartLineNumber, $e.Extent.StartColumnNumber) -ForegroundColor Red
    $line = (Get-Content $path)[($e.Extent.StartLineNumber-1)]
    Write-Host ("  > " + $line)
  }
} else {
  Write-Host "No parser errors detected" -ForegroundColor Green
}