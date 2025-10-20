# PowerShell script to run workflow.py for each change-id in changelist.txt and wait for key press after each
$changelist = Get-Content "scripts\changelist.txt"
foreach ($change in $changelist) {
    Write-Host "Processing change-id: $change"
    python scripts\workflow.py --change-id "$change"
    Write-Host "Press any key to continue to the next change..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
