# Interactive Lane Selector - User Guide

**Version**: 0.1.44  
**Status**: Production Ready  
**Last Updated**: October 24, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Interactive Features](#interactive-features)
5. [Lane Recommendation Engine](#lane-recommendation-engine)
6. [Usage Patterns](#usage-patterns)
7. [Advanced Options](#advanced-options)
8. [Troubleshooting](#troubleshooting)
9. [Integration Examples](#integration-examples)
10. [Best Practices](#best-practices)

---

## Overview

### What is the Interactive Lane Selector?

The **Interactive Lane Selector** (`scripts/interactive_lane_selector.py`) provides a user-friendly command-line interface for:

1. **Analyzing repository changes** - Automatically detects what files changed
2. **Recommending appropriate lanes** - Intelligent lane selection based on scope
3. **Visual guidance** - Rich terminal UI with colors and formatting
4. **Confirming execution** - Verification dialogs before running workflows
5. **Tracking progress** - Real-time progress indicators
6. **Summarizing results** - Clear success/failure feedback

### Why Use It?

**Before Interactive Selector**:
```bash
# Manual lane selection - prone to errors
./scripts/workflow.py --lane heavy --change-id my-change
# User must remember: What lane? How long? What gets checked?
```

**After Interactive Selector**:
```bash
python scripts/interactive_lane_selector.py
# Rich terminal UI guides through every decision
# Recommends lane based on actual changes
# Clear benefits and implications explained
```

### Key Benefits

- ✅ **Guided decisions** - Never guess which lane to use
- ✅ **Automatic analysis** - Detects scope automatically
- ✅ **Visual feedback** - Beautiful terminal UI with colors
- ✅ **Confidence scoring** - Knows when recommendations are reliable
- ✅ **Alternative options** - Suggests other lanes if appropriate
- ✅ **Flexible execution** - Supports automation and manual use

---

## Installation

### Prerequisites

- Python 3.11+
- Git repository initialized
- `scripts/interactive_lane_selector.py` in your project

### Optional: Install Rich for Better UI

```bash
pip install rich
```

**Without Rich**: Falls back to plain terminal output (still fully functional)  
**With Rich**: Beautiful colors, tables, panels, and formatted output

### Verify Installation

```bash
python scripts/interactive_lane_selector.py --help
```

Expected output shows all available options.

---

## Quick Start

### Basic Usage

```bash
# Interactive prompt through all decisions
python scripts/interactive_lane_selector.py

# With Rich library for beautiful output
pip install rich
python scripts/interactive_lane_selector.py
```

### Workflow

1. **Welcome Screen** - Introduction and environment info
2. **Change Analysis** - Detects what files changed
3. **Recommendation** - Suggests appropriate lane with reasoning
4. **Lane Selection** - Choose from DOCS, STANDARD, or HEAVY
5. **Benefits Display** - Shows why this lane is good
6. **Confirmation** - Verify before execution
7. **Execution** - Runs the workflow
8. **Summary** - Success/failure with timing

### Example Session

```
════════════════════════════════════════════════════════════════════════════════
🚀 Workflow Lane Selector
════════════════════════════════════════════════════════════════════════════════

Environment
Property          Value
──────────────────────────────────────────────────────────────────────────
Branch            feature/my-feature
Commits           3
Project Root      /Users/kdejo/project

Change Statistics
Metric                 Value
──────────────────────────────────────────────────────────────────────────
Total Files           6
Documentation         2
Code                  3
Tests                 1
Configuration         0
Total Size           14.5 KB

Recommendation
STANDARD LANE
Confidence: HIGH
Moderate scope with mixed changes and test coverage

Key Factors:
  • 6 files changed
  • 50% code changes
  • 17% test coverage

Select Lane:
  1. DOCS - Documentation changes
  2. STANDARD - Standard changes (recommended)
  3. HEAVY - Large/complex changes

Enter choice (1-3): 2

Benefits of STANDARD Lane:
  ✓ Balanced execution (15 min)
  ✓ Comprehensive checks
  ✓ Quality gate validation
  ✓ Standard CI/CD pipeline

Execute workflow in STANDARD lane? (y/n): y

Executing Workflow...

✓ Workflow Completed Successfully
Lane: STANDARD
Duration: 12m 34s
```

---

## Interactive Features

### 1. Change Analysis

The selector automatically analyzes:

```
┌─ Change Statistics ────────────────────┐
│ Total Files:       6                   │
│ Documentation:     2 (33%)             │
│ Code:              3 (50%)             │
│ Tests:             1 (17%)             │
│ Configuration:     0                   │
│ Total Size:        14.5 KB             │
└───────────────────────────────────────┘
```

**What it detects**:
- File extensions (.py, .md, .json, etc.)
- Change categories (docs, code, tests, config)
- File counts per category
- Total size of changes

### 2. Lane Recommendation

The selector recommends with confidence:

```
┌─ Recommendation ──────────────────────┐
│ STANDARD LANE                         │
│ Confidence: HIGH                      │
│                                       │
│ Moderate scope with mixed changes     │
│ and test coverage                     │
│                                       │
│ Key Factors:                          │
│ • 6 files changed                     │
│ • 50% code changes                    │
│ • 17% test coverage                   │
└───────────────────────────────────────┘
```

**Confidence Levels**:
- 🟢 **HIGH** - Recommendation is very reliable
- 🟡 **MEDIUM** - Recommendation is reasonable but could vary
- 🔴 **LOW** - User should review carefully

### 3. Lane Selection

Interactive menu with visual indicators:

```
Select Lane:
  1. 🟢 DOCS - Documentation changes
  2. 🟡 STANDARD - Standard changes (recommended)
  3. 🔴 HEAVY - Large/complex changes
```

User can override recommendation if needed.

### 4. Benefits Display

Shows why the selected lane is appropriate:

```
Benefits of STANDARD Lane:
  ✓ Balanced execution (15 min)
  ✓ Comprehensive checks
  ✓ Quality gate validation
  ✓ Standard CI/CD pipeline
```

### 5. Confirmation Dialog

Before execution, user confirms:

```
Execute workflow in STANDARD lane? (y/n): y
```

### 6. Progress Tracking

Real-time progress during execution:

```
Executing Workflow...

Testing documentation...  ✓
Running quality gates...  ✓
Executing tests...        ✓
Verifying deployment...   ✓
```

### 7. Summary Report

Clear success/failure with timing:

```
✓ Workflow Completed Successfully
Lane: STANDARD
Duration: 12m 34s
```

---

## Lane Recommendation Engine

### Decision Logic

The recommendation engine uses this logic:

#### DOCS Lane
**Recommended when**:
- ≤2 files changed
- ≥90% are documentation
- No code changes
- ≥70% docs AND ≤20% code AND ≤5 files

**Confidence**: HIGH (pure docs) to MEDIUM (mostly docs)

**Example triggers**:
- README update
- API documentation changes
- User guide improvements
- Configuration documentation

**Benefits**:
- Fastest execution (<5 min)
- Minimal resource usage
- Documentation focus
- Immediate feedback

#### STANDARD Lane
**Recommended when**:
- ≤10 files changed
- Mixed code and test changes
- Test coverage present
- Not a pure documentation update

**Confidence**: HIGH (with tests) to MEDIUM (without tests)

**Example triggers**:
- Feature implementation with tests
- Bug fix with test coverage
- API enhancement with documentation
- Configuration update with validation

**Benefits**:
- Balanced execution (15 min)
- Comprehensive checks
- Quality gate validation
- Standard CI/CD pipeline

#### HEAVY Lane
**Recommended when**:
- >10 files changed
- >50% code changes
- Code changes without test coverage
- Configuration changes
- Complex architectural changes

**Confidence**: HIGH

**Example triggers**:
- Major refactoring
- Large feature with many files
- Infrastructure changes
- Performance optimization
- Significant documentation restructuring

**Benefits**:
- Thorough validation (20 min)
- Stress testing included
- Performance benchmarks
- High confidence merge

### Recommendation Algorithm

```
Algorithm: SelectLane(stats)
  1. IF files ≤ 2 AND docs ≥ 90% AND code = 0:
     RETURN DOCS (HIGH confidence)
  
  2. ELSE IF files ≤ 5 AND docs ≥ 70% AND code ≤ 20%:
     RETURN DOCS (MEDIUM confidence)
  
  3. ELSE IF files ≤ 10 AND tests > 0 AND code > 0:
     RETURN STANDARD (HIGH/MEDIUM confidence)
  
  4. ELSE IF files > 10 OR code > 50% OR (code > 5 AND tests = 0):
     RETURN HEAVY (HIGH confidence)
  
  5. ELSE:
     RETURN STANDARD (MEDIUM confidence)
```

### Confidence Scoring

Confidence is determined by:

- **File count alignment** - Does it match lane criteria?
- **Test coverage** - Are changes tested?
- **Change distribution** - Are changes balanced?
- **Risk indicators** - Are there risky patterns?
- **Historical patterns** - Do changes match lane description?

---

## Usage Patterns

### Pattern 1: Simple Interactive Selection

**Use case**: First-time user, unsure about lane selection

```bash
python scripts/interactive_lane_selector.py
# Rich UI guides through every step
# User sees analysis, recommendation, and benefits
# High confidence in decision
```

**Duration**: ~2 minutes  
**Best for**: Manual execution, team workflows  

### Pattern 2: Automated with Auto-Confirm

**Use case**: CI/CD pipeline, automated workflows

```bash
python scripts/interactive_lane_selector.py --auto-confirm
# Analyzes changes
# Gets recommendation
# Auto-confirms with recommended lane
# Executes automatically
# No user interaction needed
```

**Duration**: <1 minute  
**Best for**: GitHub Actions, CI/CD pipelines  

### Pattern 3: Forced Lane Selection

**Use case**: Specific lane required, skip recommendation

```bash
python scripts/interactive_lane_selector.py --lane heavy
# Skips analysis and recommendation
# Uses specified lane directly
# Still shows confirmation (unless --auto-confirm)
# Executes immediately
```

**Duration**: <1 minute  
**Best for**: Testing, specific lane requirements  

### Pattern 4: Dry Run for Testing

**Use case**: Preview without executing

```bash
python scripts/interactive_lane_selector.py --dry-run
# Shows recommendation
# Displays what would happen
# Doesn't execute workflow
# Useful for testing lane selection
```

**Duration**: <30 seconds  
**Best for**: Testing, verification  

### Pattern 5: JSON Output for Integration

**Use case**: Integrate with other tools

```bash
python scripts/interactive_lane_selector.py --json
# Interactive selection as normal
# Outputs results as JSON
# Can be parsed by other tools
# Enables programmatic workflows
```

**Output format**:
```json
{
  "success": true,
  "lane": "standard",
  "duration": 754,
  "timestamp": "2025-10-24T14:30:45.123456",
  "output": "Test results...",
  "error_message": null
}
```

### Pattern 6: Verbose Logging for Debugging

**Use case**: Troubleshooting, detailed analysis

```bash
python scripts/interactive_lane_selector.py --verbose
# Shows detailed logging
# Includes all analysis steps
# Logs each decision point
# Useful for debugging
```

---

## Advanced Options

### Command-Line Arguments

```bash
python scripts/interactive_lane_selector.py [OPTIONS]
```

**Options**:

| Option | Type | Description |
|--------|------|-------------|
| `--auto-confirm` | flag | Skip confirmation dialogs |
| `--json` | flag | Output results as JSON |
| `--verbose` | flag | Enable verbose logging |
| `--lane LANE` | string | Use specific lane (docs, standard, heavy) |
| `--dry-run` | flag | Show what would happen without executing |
| `--project-root ROOT` | path | Override project root path |
| `--help` | flag | Show help message |

### Option Combinations

**Fully automated (CI/CD)**:
```bash
python scripts/interactive_lane_selector.py \
  --auto-confirm \
  --json \
  --project-root /path/to/project
```

**Testing with logging**:
```bash
python scripts/interactive_lane_selector.py \
  --dry-run \
  --verbose \
  --lane heavy
```

**Development mode**:
```bash
python scripts/interactive_lane_selector.py \
  --verbose \
  --project-root ./
```

---

## Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'rich'"

**Symptom**: Script runs but output is plain text

**Cause**: Rich library not installed

**Solution**:
```bash
pip install rich
```

**Workaround**: Script still works without Rich (automatic fallback)

### Issue 2: "No changes detected"

**Symptom**: Analysis shows 0 files changed

**Cause**: Changes not staged or committed to git

**Solution**:
```bash
# Stage changes
git add .

# Or commit changes
git commit -m "Your commit message"

# Then run selector
python scripts/interactive_lane_selector.py
```

### Issue 3: "Permission denied" on script

**Symptom**: `permission denied: scripts/interactive_lane_selector.py`

**Cause**: Script not executable

**Solution**:
```bash
chmod +x scripts/interactive_lane_selector.py

# Or run with python
python scripts/interactive_lane_selector.py
```

### Issue 4: Recommendation seems wrong

**Symptom**: Lane recommendation doesn't match expectation

**Cause**: Algorithm analyzing different metrics than expected

**Solution**:
```bash
# Run with verbose to see analysis
python scripts/interactive_lane_selector.py --verbose

# Override with specific lane
python scripts/interactive_lane_selector.py --lane heavy

# Review change statistics in output
```

### Issue 5: Workflow times out

**Symptom**: "Workflow execution timed out"

**Cause**: Workflow execution exceeds 30 minute timeout

**Solution**:
```bash
# Run with dry-run first
python scripts/interactive_lane_selector.py --dry-run

# Check if lane choice is appropriate
# Might need higher lane if too many changes

# Or increase timeout in code (development)
```

### Troubleshooting Checklist

- ✓ Check Python version: `python --version` (need 3.11+)
- ✓ Verify git repository: `git status`
- ✓ Ensure changes exist: `git diff --name-only`
- ✓ Install Rich: `pip install rich`
- ✓ Check file permissions: `ls -la scripts/interactive_lane_selector.py`
- ✓ Enable verbose logging: `--verbose` flag
- ✓ Test with dry-run: `--dry-run` flag

---

## Integration Examples

### Example 1: GitHub Actions Workflow

```yaml
name: Interactive Lane Selection

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  select-lane:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install rich pytest ruff mypy bandit

      - name: Run Interactive Lane Selector
        run: |
          python scripts/interactive_lane_selector.py \
            --auto-confirm \
            --json \
            --project-root ${{ github.workspace }} \
            > lane_selection.json

      - name: Save results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: lane-selection-results
          path: lane_selection.json
```

### Example 2: Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running interactive lane selector..."
python scripts/interactive_lane_selector.py \
  --dry-run \
  --verbose

if [ $? -eq 0 ]; then
    echo "✓ Lane selection validated"
    exit 0
else
    echo "✗ Lane selection failed"
    exit 1
fi
```

### Example 3: Manual Workflow Script

```bash
#!/bin/bash
# scripts/run-workflow.sh

set -e

echo "Starting workflow process..."

# Step 1: Run interactive selector
python scripts/interactive_lane_selector.py

# Step 2: Get lane from previous step
LANE=$(cat .last_selected_lane)

# Step 3: Execute other tasks
./scripts/quality_gates.sh --lane "$LANE"
./scripts/tests.sh --lane "$LANE"

echo "✓ Workflow complete!"
```

### Example 4: Development Workflow

```python
#!/usr/bin/env python3
# scripts/dev-workflow.py

import subprocess
import json
from pathlib import Path

def run_interactive_selector():
    """Run selector and get results."""
    result = subprocess.run(
        ['python', 'scripts/interactive_lane_selector.py', '--json'],
        capture_output=True,
        text=True
    )
    
    return json.loads(result.stdout)

def main():
    # Run selector
    results = run_interactive_selector()
    
    if results['success']:
        lane = results['lane']
        print(f"✓ Selected lane: {lane}")
        print(f"Duration: {results['duration']}s")
    else:
        print(f"✗ Selection failed: {results['error_message']}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
```

---

## Best Practices

### 1. Always Review Recommendations

Even with high confidence, review the recommendation before confirming.

```bash
# Run normally to see recommendation
python scripts/interactive_lane_selector.py

# Review the analysis, factors, and benefits
# Then confirm (or select different lane)
```

### 2. Use Dry-Run for Complex Changes

For large or complex changes, test first without executing.

```bash
# Test recommendation without executing
python scripts/interactive_lane_selector.py --dry-run

# Review the output, then run for real if appropriate
python scripts/interactive_lane_selector.py
```

### 3. Stage Changes Before Selection

Ensure changes are properly staged/committed before running selector.

```bash
# Stage all changes
git add .

# Or create a commit with changes
git commit -m "My feature"

# Then run selector
python scripts/interactive_lane_selector.py
```

### 4. Use Verbose Mode for Debugging

When something seems off, enable verbose logging.

```bash
# See detailed analysis and reasoning
python scripts/interactive_lane_selector.py --verbose
```

### 5. Consider Override for Special Cases

Sometimes the recommended lane might not be ideal. Override when needed.

```bash
# If you know you need heavy lane despite low file count
python scripts/interactive_lane_selector.py --lane heavy

# Or force another lane for testing
python scripts/interactive_lane_selector.py --lane docs
```

### 6. Integrate with Workflow System

Use selector output to drive other tools.

```bash
# Get lane recommendation
LANE=$(python scripts/interactive_lane_selector.py --auto-confirm --json | jq .lane)

# Use lane in other scripts
./scripts/run-tests.sh --lane "$LANE"
```

### 7. Monitor Execution Times

Track actual execution vs SLA targets.

```bash
# SLA targets per lane:
# DOCS: <5 min (300s)
# STANDARD: <15 min (900s)
# HEAVY: <20 min (1200s)

python scripts/interactive_lane_selector.py
# Check output duration against SLA target
```

---

## Success Criteria

✅ **Lane selection completed**: User confirmed selection or auto-confirmed  
✅ **Workflow executed**: No errors during execution  
✅ **Within SLA**: Execution completed within lane's SLA target  
✅ **Clear feedback**: User sees success/failure status  
✅ **Reproducible**: Same changes produce same recommendations  
✅ **Testable**: Dry-run mode allows pre-execution testing  

---

## Related Documentation

- [Workflow Lanes Guide](WORKFLOW_LANES_GUIDE.md) - Complete lane reference
- [CI/CD Integration](CI_CD_LANE_DETECTION_GUIDE.md) - Automated lane detection
- [POST Deployment Validation](POST_DEPLOYMENT_VALIDATION_GUIDE.md) - Validation framework
- [Analytics & Metrics](ANALYTICS_METRICS_FRAMEWORK.md) - Tracking and optimization

---

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Run with `--verbose` flag for detailed output
3. Try `--dry-run` to test without executing
4. Review [Best Practices](#best-practices) section
5. Check workflow system documentation

---

**Document Status**: Production Ready  
**Last Updated**: October 24, 2025  
**Version**: 0.1.44
