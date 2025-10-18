# Batch Archive OpenSpec Changes
# This script archives multiple completed changes at once

$ErrorActionPreference = "Stop"

# Changes to archive (completed documentation governance changes)
$changesToArchive = @(
    "update-doc-agents",
    "update-doc-claude",
    "update-doc-claude-commands-openspec-apply",
    "update-doc-claude-commands-openspec-archive",
    "update-doc-claude-commands-openspec-proposal",
    "update-doc-docs-audit-backend",
    "update-doc-docs-audit-coverage",
    "update-doc-docs-audit-plugin",
    "update-doc-docs-authentication-fix-summary",
    "update-doc-docs-clarification",
    "update-doc-docs-code-quality-improvements",
    "update-doc-docs-comprehensive-specification",
    "update-doc-docs-data-models-specification",
    "update-doc-docs-deployment-specification",
    "update-doc-docs-deployment-status"
)

Write-Host "Archiving $($changesToArchive.Count) OpenSpec changes..." -ForegroundColor Cyan

foreach ($changeId in $changesToArchive) {
    $sourcePath = "openspec\changes\$changeId"
    $archivePath = "openspec\archive\$changeId"
    
    if (Test-Path $sourcePath) {
        Write-Host "  Archiving $changeId..." -ForegroundColor Yellow
        
        # Copy to archive
        if (-not (Test-Path $archivePath)) {
            New-Item -ItemType Directory -Path $archivePath -Force | Out-Null
        }
        Copy-Item -Path "$sourcePath\*" -Destination $archivePath -Recurse -Force
        
        # Stage archive
        git add "openspec/archive/$changeId"
        
        # Remove from changes
        git rm -r "openspec/changes/$changeId"
        
        Write-Host "    ✓ Archived" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $changeId not found, skipping" -ForegroundColor DarkYellow
    }
}

# Commit all archives
Write-Host "`nCommitting batch archive..." -ForegroundColor Cyan
git commit -m "chore(openspec): batch archive completed documentation governance changes"

# Push to remote
Write-Host "Pushing to remote..." -ForegroundColor Cyan
git push

Write-Host "`n✓ Batch archive complete! Archived $($changesToArchive.Count) changes." -ForegroundColor Green
