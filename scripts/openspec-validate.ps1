$ErrorActionPreference = 'Stop'

Write-Host "Running OpenSpec validation suites..."

# Invoke pytest with argument splatting
& python -m pytest tests -q
