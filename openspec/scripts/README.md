# OpenSpec Automation Scripts

PowerShell scripts to streamline the OpenSpec governance workflow.

## Available Scripts

### create-change.ps1

**Purpose**: Scaffold a new OpenSpec change proposal with standard structure.

**Usage**:

```powershell
# Interactive mode (prompts for all inputs)
.\create-change.ps1

# Command-line mode
.\create-change.ps1 -ChangeId "add-api-governance" `
                    -Title "Add governance for API documentation" `
                    -Description "Govern API_REFERENCE.md changes" `
                    -Capability "project-documentation"
```

**What it creates**:
- `changes/<id>/proposal.md` - Why/What/Impact template
- `changes/<id>/tasks.md` - Checklist of implementation tasks
- `changes/<id>/specs/<capability>/spec.md` - Delta template (ADDED/MODIFIED/REMOVED)

**Parameters**:
- `-ChangeId` (required): Kebab-case identifier (e.g., "add-api-governance")
- `-Title` (required): Human-readable title
- `-Description` (optional): Detailed description
- `-Capability` (optional): Target capability (default: "project-documentation")

---

### validate-all.ps1

**Purpose**: Batch validation of all changes and specs.

**Usage**:

```powershell
# Validate everything (all changes + baseline specs)
.\validate-all.ps1

# Validate only pending changes
.\validate-all.ps1 -ChangesOnly

# Validate only baseline specs
.\validate-all.ps1 -SpecsOnly

# Validate specific change
.\validate-all.ps1 -ChangeId "add-api-governance"

# JSON output for CI/CD
.\validate-all.ps1 -Json

# Quiet mode (summary only)
.\validate-all.ps1 -Quiet
```

**Exit codes**:
- `0`: All validations passed
- `1`: One or more validations failed

**CI/CD integration**:

```yaml
# GitHub Actions example
- name: Validate OpenSpec
  run: |
    cd openspec
    .\scripts\validate-all.ps1 -Json > validation-results.json
    if ($LASTEXITCODE -ne 0) { exit 1 }
```

---

### apply-change.ps1

**Purpose**: Apply a change to the baseline specification with safety checks.

**Usage**:

```powershell
# Standard apply (validates before and after)
.\apply-change.ps1 -ChangeId "add-api-governance"

# Dry run (show what would change)
.\apply-change.ps1 -ChangeId "add-api-governance" -DryRun

# Force apply (skip validation)
.\apply-change.ps1 -ChangeId "add-api-governance" -Force
```

**What it does**:
1. Pre-validates the change with `openspec validate --strict`
2. Applies deltas to baseline spec with `openspec apply`
3. Post-validates the updated baseline spec
4. Reports success/failure with actionable guidance

**Parameters**:
- `-ChangeId` (required): Change to apply
- `-DryRun`: Show proposed changes without applying
- `-Force`: Skip pre-validation (use with caution)

---

### archive-change.ps1

**Purpose**: Archive an applied change with backup and verification.

**Usage**:

```powershell
# Standard archive (validates before archiving)
.\archive-change.ps1 -ChangeId "add-api-governance"

# Keep original in changes/ after archiving
.\archive-change.ps1 -ChangeId "add-api-governance" -KeepOriginal

# Force archive (skip validation)
.\archive-change.ps1 -ChangeId "add-api-governance" -Force
```

**What it does**:
1. Verifies change has been applied (checks baseline specs exist)
2. Creates timestamped backup in `backups/`
3. Archives change with `openspec archive`
4. Optionally removes original from `changes/`
5. Verifies archive location

**Parameters**:
- `-ChangeId` (required): Change to archive
- `-KeepOriginal`: Don't remove from changes/ after archiving
- `-Force`: Skip validation checks

---

## Complete Workflow Example

### 1. Create a new change proposal

```powershell
.\create-change.ps1 -ChangeId "add-api-docs-governance" `
                    -Title "Add governance for API documentation" `
                    -Description "Govern material changes to docs/API_REFERENCE.md"
```

**Output**:
- ✅ Change scaffolded successfully!
- 📁 Location: `changes/add-api-docs-governance/`
- 📝 Files: `proposal.md`, `tasks.md`, `specs/project-documentation/spec.md`

### 2. Edit the generated files

```powershell
# Edit proposal (Why/What/Impact)
code changes\add-api-docs-governance\proposal.md

# Edit capability spec (ADDED/MODIFIED/REMOVED deltas)
code changes\add-api-docs-governance\specs\project-documentation\spec.md

# Update task checklist
code changes\add-api-docs-governance\tasks.md
```

### 3. Validate your changes

```powershell
# Validate specific change
.\validate-all.ps1 -ChangeId "add-api-docs-governance"

# Or validate everything
.\validate-all.ps1
```

**Success output**:
- ✅ All validations passed!
- Passed: 1 / Total: 1

**Failure output**:
- ❌ Validation failed. See errors above.
- 💡 Troubleshooting tips with references to docs

### 4. Submit for review

```powershell
# Commit changes
git add changes/add-api-docs-governance/
git commit -m "Add governance for API documentation"

# Create pull request
git push origin feature/add-api-docs-governance
```

### 5. Apply to baseline (after approval)

```powershell
# Dry run first (recommended)
.\apply-change.ps1 -ChangeId "add-api-docs-governance" -DryRun

# Apply for real
.\apply-change.ps1 -ChangeId "add-api-docs-governance"
```

**Output**:
- 🔍 Validating change... ✅
- 📝 Applying change to baseline spec... ✅
- 🔍 Validating updated baseline spec... ✅
- 🎉 Change applied successfully!

### 6. Archive completed change

```powershell
.\archive-change.ps1 -ChangeId "add-api-docs-governance"
```

**Output**:
- 🔍 Verifying change has been applied... ✅
- 💾 Creating backup... ✅ (`backups/add-api-docs-governance-20250114-143022`)
- 📦 Archiving change... ✅
- 🗑️ Removing original change directory... ✅
- 🎉 Change archived successfully!

### 7. Commit updated baseline and archive

```powershell
git add specs/ archive/
git commit -m "Apply and archive: Add governance for API documentation"
git push
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: OpenSpec Validation

on:
  pull_request:
    paths:
      - 'openspec/**'

jobs:
  validate:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install OpenSpec CLI
        run: |
          # Install OpenSpec (adjust for your installation method)
          pip install openspec-cli

      - name: Validate OpenSpec Changes
        run: |
          cd openspec
          .\scripts\validate-all.ps1 -Json > validation-results.json
          if ($LASTEXITCODE -ne 0) {
            Write-Host "::error::OpenSpec validation failed"
            exit 1
          }

      - name: Upload Validation Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: openspec-validation
          path: openspec/validation-results.json
```

### Azure DevOps Example

```yaml
trigger:
  paths:
    include:
      - openspec/*

pool:
  vmImage: 'windows-latest'

steps:
  - task: PowerShell@2
    displayName: 'Validate OpenSpec'
    inputs:
      targetType: 'inline'
      script: |
        cd openspec
        .\scripts\validate-all.ps1 -Json | Out-File validation-results.json
        if ($LASTEXITCODE -ne 0) {
          Write-Host "##vso[task.logissue type=error]OpenSpec validation failed"
          exit 1
        }

  - task: PublishBuildArtifacts@1
    condition: always()
    inputs:
      pathToPublish: 'openspec/validation-results.json'
      artifactName: 'openspec-validation'
```

---

## Troubleshooting

### Script execution policy

If scripts won't run due to execution policy:

```powershell
# Check current policy
Get-ExecutionPolicy

# Set for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single command
powershell -ExecutionPolicy Bypass -File .\create-change.ps1
```

### OpenSpec CLI not found

Ensure OpenSpec is installed and in PATH:

```powershell
# Check if openspec is available
Get-Command openspec

# If not found, install OpenSpec CLI
pip install openspec-cli  # (adjust for your installation method)
```

### Validation errors

Common validation errors and solutions:

**"Requirement must contain SHALL or MUST keyword"**
- ✅ Fix: Add SHALL or MUST to requirement text (first sentence after heading)
- 📖 See: [docs/change-patterns.md](../docs/change-patterns.md#common-pitfalls)

**"Requirement must have at least one scenario"**
- ✅ Fix: Add `#### Scenario:` section with WHEN/THEN
- 📖 See: [docs/change-patterns.md](../docs/change-patterns.md#scenario-format-critical)

**"Change must have at least one delta operation"**
- ✅ Fix: Add `## ADDED`, `## MODIFIED`, `## REMOVED`, or `## RENAMED` section
- 📖 See: [docs/change-patterns.md](../docs/change-patterns.md#delta-types)

---

## Best Practices

### Creating changes

- ✅ **Use descriptive IDs**: `add-api-governance` not `change-1`
- ✅ **One concern per change**: Don't mix unrelated governance updates
- ✅ **Validate early and often**: Run `validate-all.ps1` as you edit
- ✅ **Use dry-run**: Test with `-DryRun` before applying

### Validation workflow

- ✅ **Validate before commit**: Catch errors before pushing
- ✅ **CI validation**: Add validation to PR checks
- ✅ **Fix all issues**: Don't merge with validation failures
- ✅ **Review output**: Read error messages carefully

### Apply and archive

- ✅ **Apply in order**: Respect change dependencies
- ✅ **Verify baseline**: Check specs/ after applying
- ✅ **Archive promptly**: Don't leave applied changes in changes/
- ✅ **Commit atomically**: Baseline + archive together

---

## See Also

- [../README.md](../README.md) - OpenSpec governance overview
- [../AGENTS.md](../AGENTS.md) - Complete governance workflow
- [../docs/change-patterns.md](../docs/change-patterns.md) - Delta pattern reference
- [../docs/contributor-guide.md](../docs/contributor-guide.md) - Onboarding guide _(planned)_
- [../docs/troubleshooting.md](../docs/troubleshooting.md) - Error solutions _(planned)_
