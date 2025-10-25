# GitHub Actions Lane Support Enhancement (INFRA-1)

**Objective**: Add GitHub Actions native lane support to enable automatic lane detection and execution in CI/CD.

**Status**: Ready for implementation (v0.1.37+)

---

## Overview

This enhancement adds lane-aware execution to GitHub Actions workflows, allowing:
1. **Automatic lane detection** based on changed files (markdown-only → docs lane)
2. **Conditional job execution** based on lane type
3. **Lane metrics tracking** for analytics and performance monitoring
4. **Fallback to standard lane** for mixed or ambiguous changes

---

## Implementation Strategy

### 1. Add Change Detection Step

Add a step early in CI/CD workflows to detect change type and determine lane:

```yaml
- name: Detect Changed Files and Determine Lane
  id: detect-lane
  run: |
    # Get list of changed files
    if [[ "${{ github.event_name }}" == "pull_request" ]]; then
      CHANGED_FILES=$(git diff --name-only origin/${{ github.base_ref }})
    else
      CHANGED_FILES=$(git diff --name-only ${{ github.event.before }}..${{ github.sha }})
    fi
    
    # Count file types
    MARKDOWN_FILES=$(echo "$CHANGED_FILES" | grep -E '\.(md|MD)$' | wc -l)
    CODE_FILES=$(echo "$CHANGED_FILES" | grep -vE '\.(md|MD|txt|LICENSE|yml|yaml)$' | wc -l)
    TOTAL_FILES=$(echo "$CHANGED_FILES" | wc -l)
    
    # Determine lane
    if [ "$CODE_FILES" -eq 0 ] && [ "$MARKDOWN_FILES" -gt 0 ]; then
      LANE="docs"
    elif [ "$TOTAL_FILES" -gt 20 ] || grep -q "core\|refactor" <<< "$CHANGED_FILES"; then
      LANE="heavy"
    else
      LANE="standard"
    fi
    
    echo "lane=$LANE" >> $GITHUB_OUTPUT
    echo "code_files=$CODE_FILES" >> $GITHUB_OUTPUT
    echo "markdown_files=$MARKDOWN_FILES" >> $GITHUB_OUTPUT
    echo "total_files=$TOTAL_FILES" >> $GITHUB_OUTPUT
    echo "::notice::Detected lane: $LANE (code: $CODE_FILES, markdown: $MARKDOWN_FILES, total: $TOTAL_FILES)"
  shell: bash
```

### 2. Conditional Job Execution

Use the detected lane to conditionally skip or run specific jobs:

```yaml
jobs:
  # Skip heavy jobs for docs-only changes
  code-quality:
    runs-on: ubuntu-latest
    if: steps.detect-lane.outputs.lane != 'docs'
    steps:
      # ... code quality checks ...
  
  # Always run tests, but with lane-specific thresholds
  tests:
    runs-on: ubuntu-latest
    needs: [code-quality]
    env:
      LANE: ${{ steps.detect-lane.outputs.lane }}
    steps:
      - name: Run tests with lane-specific thresholds
        run: |
          if [ "$LANE" == "docs" ]; then
            echo "Skipping tests for docs-only lane"
          elif [ "$LANE" == "heavy" ]; then
            pytest --cov=. --cov-report=term-missing -v --tb=short -x
          else
            pytest -v --tb=short
          fi
```

### 3. Pass Lane to Workflow Scripts

Set environment variable for workflow.py to use:

```yaml
  - name: Run OpenSpec Workflow
    env:
      LANE: ${{ steps.detect-lane.outputs.lane }}
    run: |
      python scripts/workflow.py \
        --change-id ci-${{ github.run_id }} \
        --title "CI/CD Run" \
        --owner "github-actions" \
        --lane "$LANE"
```

---

## Files to Modify

### 1. `.github/workflows/ci.yml`
**Changes**:
- Add `detect-lane` step with lane detection logic
- Add `if:` conditions to skip docs-specific jobs for docs lane
- Pass `LANE` environment variable to all relevant steps

**Estimated effort**: 30 minutes

### 2. `.github/workflows/test-backend.yml` (if exists)
**Changes**:
- Add lane detection
- Skip non-critical tests for docs lane
- Use lane-specific pytest thresholds

**Estimated effort**: 20 minutes

### 3. `.github/workflows/release.yml` (if exists)
**Changes**:
- Add lane detection
- Skip release steps for docs-only changes (no release needed)
- Log lane in release notes

**Estimated effort**: 15 minutes

### 4. `scripts/workflow.py`
**Changes**:
- Add support for `--lane` parameter from CI/CD environment
- Fallback to auto-detection if not provided
- Log detected lane in status.json

**Already done** ✅ - No changes needed

---

## Lane Detection Logic

### Docs Lane Criteria
- ✅ Only markdown files (*.md) changed
- ✅ No code files modified
- ✅ Typically <10 files
- ✅ Examples: README updates, guides, documentation

### Standard Lane Criteria
- ✅ Mixed changes (docs + code) or
- ✅ Code changes with <20 files or
- ✅ No specific indicators for heavy lane
- ✅ Examples: Bug fixes, small features, routine updates

### Heavy Lane Criteria
- ✅ Large change set (>20 files) or
- ✅ Changes to core modules (agent/, openspec/) or
- ✅ Keywords detected: "refactor", "migration", "breaking" or
- ✅ Multiple directories affected (5+)
- ✅ Examples: Major refactoring, architectural changes, large features

---

## Benefits

### Performance
- **Docs-only changes**: Skip 50% of CI/CD jobs, reduce run time from ~5min to ~1min
- **Standard changes**: Normal quality gates, ~3-4min runtime
- **Heavy changes**: Enhanced checks but targeted, ~5-6min runtime

### Developer Experience
- Faster feedback for documentation contributions
- Clear visibility into what's being checked
- Automatic lane selection reduces confusion

### Reliability
- Consistent lane selection across local and CI/CD
- Metrics tracked for all lane types
- Easy to audit lane decisions

---

## Implementation Steps

1. **Analyze current ci.yml** (15 min)
   - Identify all jobs that should respect lanes
   - Find timing bottlenecks that could be reduced for docs lane

2. **Create detect-lane step** (30 min)
   - Implement file change detection logic
   - Test with various change scenarios

3. **Add conditional execution** (30 min)
   - Add `if:` conditions to appropriate jobs
   - Ensure fallback behavior for ambiguous changes

4. **Update workflow.py integration** (20 min)
   - Test workflow.py with `--lane` parameter from CI/CD
   - Verify status.json includes lane information

5. **Test end-to-end** (30 min)
   - Create PR with docs-only change, verify docs lane runs
   - Create PR with code change, verify standard lane runs
   - Create PR with large change set, verify heavy lane runs

6. **Documentation** (15 min)
   - Document lane detection criteria
   - Add troubleshooting for ambiguous cases
   - Update contributor guide

**Total estimated time**: 2.5 hours

---

## Rollback Plan

If lane detection causes issues:
1. Remove lane detection step
2. Set `LANE=standard` as default
3. All workflows execute normally (standard lane behavior)
4. No functional impact, just lose performance optimization

---

## Success Criteria

- [ ] Docs-only PR runs <1 minute (was ~5 minutes)
- [ ] Standard PR runs ~3-4 minutes
- [ ] Heavy PR runs ~5-6 minutes
- [ ] All quality gates execute correctly for their lane
- [ ] Lane information logged in status.json for all runs
- [ ] Tests passing with lane-specific thresholds

---

## Future Enhancements

### v0.1.38
- **ML-based lane prediction**: Use commit message and file patterns for even better detection
- **Lane override flag**: Allow contributors to force a specific lane if detection is wrong

### v0.1.39
- **Cloud parallelization**: Use lane to determine if job can run on cheaper/faster runners
- **Metrics dashboard**: Track lane adoption, timing trends, success rates

### v0.1.40+
- **Enterprise lanes**: Add private/compliance lanes for organizations
- **Weighted lane selection**: Based on historical data for the project

---

## Related Documentation

- `openspec/changes/workflow-improvements/spec.md` - Overall specifications
- `docs/guides/The_Workflow_Process.md` - User-facing workflow documentation
- `.github/workflows/` - Current GitHub Actions workflows

