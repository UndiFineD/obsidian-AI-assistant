#!/usr/bin/env pwsh
Write-Host "=== Refactoring backend to agent ===" -ForegroundColor Cyan
Write-Host ""

$rootPath = 'c:\Users\kdejo\DEV\obsidian-llm-assistant\obsidian-AI-assistant'

# Get all Python and config files
$files = @()
$files += Get-ChildItem -Path $rootPath -Recurse -Include '*.py' -ErrorAction SilentlyContinue
$files += Get-ChildItem -Path $rootPath -Recurse -Include '*.md' -ErrorAction SilentlyContinue
$files += Get-ChildItem -Path $rootPath -Recurse -Include '*.yaml' -ErrorAction SilentlyContinue
$files += Get-ChildItem -Path $rootPath -Recurse -Include '*.yml' -ErrorAction SilentlyContinue
$files += Get-ChildItem -Path $rootPath -Recurse -Include '*.json' -ErrorAction SilentlyContinue

# Filter out excluded directories
$files = $files | Where-Object { $_.FullName -notmatch '\\\.git|\\node_modules|\\__pycache__|\\\.pytest_cache|\\\.venv|\\\.trunk|\\htmlcov' }

Write-Host "Processing $($files.Count) files..." -ForegroundColor Green

$updatedCount = 0
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $content) { continue }
    
    $newContent = $content -replace 'from backend\.', 'from agent.' -replace 'import backend\.', 'import agent.' -replace 'from backend import', 'from agent import' -replace 'import backend[^a-z]', 'import agent$&' -replace 'backend\.backend', 'agent.agent' -replace '"backend/', '"agent/' -replace "'backend/", "'agent/" -replace 'backend/', 'agent/' -replace 'backend_', 'agent_'
    
    if ($newContent -ne $content) {
        Set-Content $file.FullName -Value $newContent -NoNewline -ErrorAction SilentlyContinue
        $updatedCount++
    }
}

Write-Host "Updated $updatedCount files" -ForegroundColor Cyan

if (Test-Path "$rootPath\tests\backend") {
    Rename-Item -Path "$rootPath\tests\backend" -NewName "agent" -Force -ErrorAction SilentlyContinue
    Write-Host "Renamed tests/backend/ to tests/agent/" -ForegroundColor Green
}

Write-Host "=== Done ===" -ForegroundColor Cyan
