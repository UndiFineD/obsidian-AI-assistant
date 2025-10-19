$syntaxErrorActionPreference = 'Stop'
Write-Host "Running OpenSpec validation suites..."
& python -m pytest tests -q
