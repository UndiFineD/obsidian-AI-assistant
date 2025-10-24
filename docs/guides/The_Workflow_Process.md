# The OpenSpec Workflow Process

## Table of Contents

1. [Overview](#overview)
2. [Workflow Stages (13 Steps)](#workflow-stages-13-steps)
3. [File Structure](#file-structure)
4. [Tools & Technologies](#tools--technologies)
5. [Entry Points](#entry-points)
6. [Configuration & Setup](#configuration--setup)
7. [Integration Points](#integration-points)
8. [Error Handling & Validation](#error-handling--validation)
9. [Checkpoints & Resumption](#checkpoints--resumption)
10. [Advanced Features](#advanced-features)

---

## Overview

The OpenSpec Workflow is a **13-stage automated process**
for managing code changes in the Obsidian AI Agent project.
It enforces structured change management from initial proposal
through implementation, testing, documentation, and pull request creation.

### Key Principles

- **Governance**: All changes follow a strict workflow with mandatory documentation
- **Traceability**: Every stage is tracked with checkpoints and TODO lists
- **Automation**: Python and PowerShell scripts automate repetitive tasks
- **Integration**: GitHub, Git, pytest, and CI/CD tools are deeply integrated
- **Validation**: Multi-stage validation ensures quality and compliance

### Workflow Lanes (Fast-Track Options)

**NEW**: The workflow supports three lanes for different change types:

#### **Documentation Lane (Docs)**
- **Target**: Documentation-only changes (README, guides, etc.)
- **Execution Time**: <5 minutes (67% faster than standard)
- **Stages Executed**: 0, 2, 3, 4, 9, 10, 11, 12 (skips code validation stages)
- **Quality Gates**: Disabled (documentation doesn't require code validation)
- **Usage**: `python workflow.py --change-id my-change --lane docs`
- **Example**: Update CHANGELOG.md, README.md, documentation files

#### **Standard Lane (Default)**
- **Target**: Regular code and feature changes
- **Execution Time**: ~15 minutes
- **Stages Executed**: All 13 stages
- **Quality Gates**: Enabled with standard thresholds (80% test pass, 70% coverage)
- **Usage**: `python workflow.py --change-id my-change` (no lane specified defaults to standard)
- **Example**: Add new feature, fix bug, refactor code

#### **Heavy Lane (Strict Validation)**
- **Target**: Critical, production, or security-related changes
- **Execution Time**: ~20 minutes (more thorough validation)
- **Stages Executed**: All 13 stages
- **Quality Gates**: Enabled with strict thresholds (100% test pass, 85% coverage)
- **Usage**: `python workflow.py --change-id my-change --lane heavy`
- **Example**: Security fix, critical production change, major refactoring

### Project Structure

```
scripts/
├── workflow.py                      # Main Python orchestrator
├── workflow.ps1                     # PowerShell version
├── workflow2.ps1                    # Alternative PS version
├── workflow-step00.py through       # Individual step implementations
├── workflow-step12.py               #   (13 steps total: 0-12)
├── workflow-helpers.py              # Shared utilities
├── quality_gates.py                 # Quality validation (ruff, mypy, pytest, bandit)
├── progress_indicators.py           # Progress tracking
├── checkpoint_manager.py            # State management
├── workflow_visualizer.py           # Progress visualization
├── workflow_nested_progress_demo.py # Progress UI demo
└── version_manager.py               # Version handling

openspec/
├── changes/                         # Active change work directories
├── archive/                         # Completed/archived changes
├── templates/                       # File templates
│   ├── todo.md
│   ├── proposal.md
│   ├── spec.md
│   ├── tasks.md
│   ├── test_plan.md
│   └── ...
├── scripts/                         # OpenSpec validation scripts
│   ├── create-change.ps1
│   ├── apply-change.ps1
│   ├── archive-change.ps1
│   └── validate-all.ps1
└── PROJECT_WORKFLOW.md              # Workflow specification
```

---

## Workflow Stages (13 Steps)

### **Stage 0: Create TODOs** ✓

**File**: `workflow-step00.py`

**Purpose**: Initialize the change with a TODO checklist tracking all workflow stages.

**Tasks**:
- Load `openspec/templates/todo.md`
- Replace placeholders:
    - `<Change Title>` → Actual title
    - `<change-id>` → Change identifier
    - `@username` → Change owner
    - `YYYY-MM-DD` → Current date
- Mark Stage 0 as complete `[x]`
- Write `openspec/changes/<change-id>/todo.md`

**Output Files**:
- `todo.md` - Main workflow checklist

**Key Functions**:
```python
invoke_step0(
    change_path: Path,
    title: str,
    owner: str,
    dry_run: bool = False
) -> bool
```

---

### **Stage 1: Increment Release Version** ✓

**File**: `workflow-step01.py`

**Purpose**: Create version snapshot and optionally increment release version.

**Tasks**:
- Create version snapshot before changes
- Optionally increment version in:
    - `CHANGELOG.md`
    - `README.md`
    - `package.json`
    - `pyproject.toml` (if exists)
- Document version increment in `todo.md`
- Create release branch `release-x.y.z` (optional)

**Key Operations**:
- Git status capture for rollback capability
- Version regex matching and updating
- Semantic versioning enforcement (major.minor.patch)

**Output Files**:
- Updated version files
- Version snapshot documentation

---

### **Stage 2: Proposal** ✓

**File**: `workflow-step02.py`

**Purpose**: Create comprehensive proposal document defining the change.

**Content Required**:
```markdown
# Change Proposal: [Title]

## Why
[Rationale and motivation]

## What Changes
- **Affected specs**: [...components affected]
- **Affected files**: [...files modified]
- **Affected code**: [...functions/classes]

## Impact
- **Breaking changes**: [list if any]
- **Dependencies**: [new requirements]
- **Performance**: [performance implications]

## Goals
- Goal 1: [specific, measurable]
- Goal 2: [...]

## Context
[Background information]

## Stakeholders
- Owner: @username
- Reviewers: @reviewer1, @reviewer2
```

**Key Functions**:
```python
invoke_step2(change_path: Path) -> bool
```

**Output Files**:
- `proposal.md` - Complete change proposal

---

### **Stage 3: Specification** ✓

**File**: `workflow-step03.py`

**Purpose**: Define technical requirements and implementation details.

**Content Required**:
```markdown
# Specification: [Title]

## Acceptance Criteria
- [ ] Criterion 1: [testable requirement]
- [ ] Criterion 2: [...]

## Technical Design

### Data Models (if applicable)
- Model 1: [definition]
- Model 2: [...]

### API Changes (if applicable)
- Endpoint: GET /api/resource
- Parameters: [...]
- Response: [JSON schema]

### Security & Privacy
- [Authentication requirements]
- [Data protection measures]
- [Compliance notes]

## Performance Requirements
- Latency: [target milliseconds]
- Throughput: [requests/second]
- Memory: [target usage]

## Dependencies
- [External libraries needed]
- [Version constraints]

## Migration Path
- [Backward compatibility notes]
- [Upgrade instructions if needed]
```

**Key Functions**:
```python
invoke_step3(change_path: Path) -> bool
```

**Output Files**:
- `spec.md` - Technical specification

---

### **Stage 4: Task Breakdown** ✓

**File**: `workflow-step04.py`

**Purpose**: Break change into actionable tasks.

**Content Required**:
```markdown
# Tasks: [Title]

## Implementation Tasks

### Task 1: [Component/Feature]
- [ ] Subtask 1.1
- [ ] Subtask 1.2
- [ ] Subtask 1.3

### Task 2: [Component/Feature]
- [ ] Subtask 2.1
- [ ] Subtask 2.2

## Testing Tasks
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Documentation Tasks
- [ ] Update README
- [ ] Update API docs
- [ ] Add code comments

## Review Tasks
- [ ] Code review by @reviewer1
- [ ] Security review
- [ ] Performance review
```

**Key Features**:
- Hierarchical task organization
- Dependency tracking
- Progress monitoring

**Output Files**:
- `tasks.md` - Detailed task breakdown

---

### **Stage 5: Test Definition** ✓

**File**: `workflow-step05.py`

**Purpose**: Create comprehensive test plan and requirements.

**Content Required**:
```markdown
# Test Plan: [Title]

## Unit Tests
- [test_module_functionality]
- [test_edge_cases]
- [test_error_handling]

## Integration Tests
- [test_component_interaction]
- [test_api_endpoints]
- [test_database_operations]

## Acceptance Tests
- [Criterion 1 test]
- [Criterion 2 test]

## Performance Tests
- [Latency benchmarks]
- [Throughput tests]
- [Memory profiling]

## Security Tests
- [Authentication validation]
- [Input validation]
- [Authorization checks]

## Test Coverage Goals
- Target: [percentage]%
- Critical paths: 100%
- Edge cases: 80%+

## Test Environment
- [Requirements]
- [Setup instructions]
- [Data requirements]
```

**Pytest Integration**:
- Runs pytest to generate coverage
- Updates test statistics
- Validates test files exist

**Output Files**:
- `test_plan.md` - Complete test planning

---

### **Stage 6: Script Generation** ✓

**File**: `workflow-step06.py` (1,220 lines - Most Complex)

**Purpose**: Generate or update implementation and test scripts.

**Analyzes Requirements From**:
- `proposal.md` - What's being changed
- `spec.md` - How it's implemented
- `tasks.md` - What needs doing
- File patterns - What files are affected

**Generates Scripts For**:

#### Setup Scripts
```python
def generate_setup_script(change_path: Path) -> str
    # Creates setup.ps1 or setup.sh based on affected components
    # Handles dependencies, installations, configurations
```

#### Test Harnesses
```python
def generate_test_harness(change_path: Path) -> str
    # Creates test validation functions
    # Sets up test fixtures and mocks
    # Generates test templates
```

#### Implementation Scaffolding
```python
def generate_implementation_scaffold(change_path: Path) -> str
    # Creates file stubs with docstrings
    # Adds TODO markers for implementation
    # Includes error handling boilerplate
```

#### CI/CD Pipeline Updates
```python
def generate_cicd_pipeline(change_path: Path) -> str
    # Updates .github/workflows/ if needed
    # Adds new test stages
    # Configures quality checks
```

**Key Analysis Functions**:
```python
def _analyze_requirements(change_path: Path) -> Dict
    # Detects what needs to be generated
    # Returns:
    #   - needs_setup: bool
    #   - needs_test: bool
    #   - needs_validation: bool
    #   - needs_ci: bool
    #   - script_types: List[str]  # PowerShell, Bash, Python
    #   - purposes: List[str]
    #   - affected_files: List[str]

def _extract_test_requirements(spec_path: Path) -> List[str]
    # Pulls test criteria from spec.md
    # Returns test function signatures to generate

def _generate_test_validator(requirements: List[str]) -> str
    # Creates validation function for each requirement
    # Generates assertion statements
```

**Output Files**:
- Implementation script stubs
- Test harness files
- Setup/teardown scripts
- CI/CD workflow updates

---

### **Stage 7: Implementation** ✓

**File**: `workflow-step07.py`

**Purpose**: Execute the actual code changes.

**Tasks**:
- Implement changes based on proposal/spec/tasks
- Update affected files identified in proposal
- Add error handling and logging
- Include inline documentation
- Create/update unit tests

**Key Actions**:
- Modify source files
- Create new modules/classes/functions
- Update configuration files
- Add logging/monitoring

**Validation**:
- Syntax checking
- Import validation
- Type hints verification (mypy)
- Linting with ruff

**Output Files**:
- Updated source code files
- New modules/tests
- Configuration updates

---

### **Stage 8: Testing** ✓

**File**: `workflow-step08.py`

**Purpose**: Run all tests and validate quality metrics.

**Test Execution**:
```bash
# Run pytest suite
pytest tests/ -v --cov=agent --cov-report=html

# Results captured in:
# - test_results.txt
# - coverage.xml
# - htmlcov/ directory
```

**Validation Checks**:
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Code coverage meets target (70%+)
- ✅ No broken imports
- ✅ Type checking passes
- ✅ Linting passes
- ✅ Security scan (bandit) clear

**Quality Gates**:
```python
QUALITY_GATES = {
    'test_pass_rate': 100,      # All tests must pass
    'coverage_target': 70,      # Minimum coverage %
    'lint_errors': 0,           # No linting errors
    'type_errors': 0,           # No type errors
    'security_issues': 0        # No critical security issues
}
```

**Output Files**:
- `test_results.md` - Test report
- `coverage_report.md` - Coverage analysis
- `quality_metrics.json` - Metrics data

---

### **Stage 9: Documentation & Review** ✓

**File**: `workflow-step09.py`

**Purpose**: Update documentation and prepare for review.

**Documentation Updates**:

#### README.md
- New feature description
- Usage examples
- Updated table of contents

#### API Documentation
- New endpoints/classes
- Parameter documentation
- Return value documentation
- Example usage

#### CHANGELOG.md
- Entry: `## [Version] - Date`
- Added/Changed/Fixed/Deprecated sections
- Migration notes if needed

#### Code Comments
- Function docstrings (Google style)
- Complex logic explanations
- TODO/FIXME markers

#### Architecture Docs
- Diagram updates
- Flow documentation
- Integration points

**Key Operations**:
```python
def update_readme(change_path: Path) -> bool
    # Add feature to README
    # Update TOC if needed
    # Add examples

def update_api_docs(change_path: Path) -> bool
    # Extract docstrings
    # Generate API reference
    # Create examples

def update_changelog(change_path: Path) -> bool
    # Add new entry with version
    # Categorize changes
    # Add issue references
```

**Output Files**:
- Updated `README.md`
- Updated `CHANGELOG.md`
- API documentation
- Architecture diagrams

---

### **Stage 10: Git Operations** ✓

**File**: `workflow-step10.py`

**Purpose**: Prepare Git commit with all changes.

**Git Operations**:

```bash
# Stage changes
git add [affected files]

# Create commit with detailed message
git commit -m "feat: [Short description]

- Detailed change 1
- Detailed change 2
- Affected components: [list]
- Related to: [issue/PR references]"

# Create/push to feature branch
git checkout -b feature/[change-id]
git push origin feature/[change-id]
```

**Commit Message Format**:
```
<type>: <subject>

<body>

<footer>

Type: feat, fix, docs, style, refactor, test, chore, ci
Subject: Brief description (imperative mood)
Body: Detailed explanation
Footer: Issue references (Closes #123)
```

**Key Functions**:
```python
def stage_changes(change_path: Path) -> bool
    # git add affected files

def create_commit(
    change_path: Path,
    title: str,
    description: str
) -> bool
    # git commit with detailed message

def push_to_remote(branch: str) -> bool
    # git push origin branch
    # Returns success/failure
```

**Output Files**:
- Committed changes
- Feature branch created
- Git history updated

---

### **Stage 11: Archive Completed Change** ✓

**File**: `workflow-step11.py`

**Purpose**: Archive completed change for history.

**Archive Process**:

```
openspec/changes/<change-id>/
    ↓ (moved to)
openspec/archive/<timestamp>-<change-id>/
    ├── todo.md (completed checklist)
    ├── proposal.md
    ├── spec.md
    ├── tasks.md
    ├── test_plan.md
    ├── test_results.md
    ├── implementation_notes.md
    └── .checkpoints/
        └── checkpoint-<timestamp>-step<N>/
            └── (state at each step)
```

**Archiving Steps**:
1. Create archive directory with timestamp
2. Copy all documentation
3. Preserve checkpoints history
4. Remove temporary files
5. Generate archive manifest
6. Update archive index

**Archive Metadata**:
```json
{
  "change_id": "update-doc-readme",
  "title": "Update README Documentation",
  "owner": "@username",
  "status": "completed",
  "archived_date": "2025-10-22T15:30:00Z",
  "duration_days": 2,
  "git_commit": "abc123def456",
  "pr_number": 42,
  "test_coverage": 85.5
}
```

**Key Functions**:
```python
def archive_change(
    change_path: Path,
    destination: Path
) -> bool
    # Move change to archive
    # Preserve all history
    # Generate manifest

def generate_archive_manifest(archive_path: Path) -> dict
    # Index all files
    # Calculate statistics
    # Create summary
```

**Output Files**:
- Archived change directory
- Archive manifest
- Archive index updated

---

### **Stage 12: Create Pull Request** ✓

**File**: `workflow-step12.py` (483 lines)

**Purpose**: Create GitHub Pull Request for review and merging.

**PR Creation Process**:

```bash
# Uses GitHub CLI (gh)
gh pr create \
  --title "<Type>: <Title>" \
  --body "[detailed PR body]" \
  --base main \
  --head feature/[change-id]
```

**PR Body Template**:
```markdown
## Change Summary
[Extracted from proposal.md - title and why]

## What Changed
- **Affected specs**: [list from proposal]
- **Affected files**: [list from proposal]
- **Affected code**: [list from proposal]

## Verification Checklist
- [x] Code follows project style guide
- [x] Tests added and passing
- [x] Documentation updated
- [x] Coverage maintained above 70%
- [x] No breaking changes

## Test Results
- Tests Passed: X/X
- Coverage: Y%
- Performance: [measurements]

## Related Issues
Closes #[issue_number]

## Deployment Notes
- [Any special deployment instructions]
- [Database migrations if needed]
- [Configuration changes]

## Reviewers
@reviewer1 @reviewer2

## Documentation Links
- [Proposal](../proposal.md)
- [Specification](../spec.md)
- [Test Plan](../test_plan.md)
```

**Key Functions**:
```python
def extract_doc_info(proposal_path: Path) -> dict
    # Extract title, why, affected specs/files/code
    # Returns: {
    #   'title': str,
    #   'why': str,
    #   'affected_specs': str,
    #   'affected_files': str,
    #   'affected_code': str
    # }

def create_pr(
    branch: str,
    title: str,
    body: str,
    base: str = "main"
) -> int
    # Creates PR using gh CLI
    # Returns PR number

def get_test_results(change_path: Path) -> dict
    # Reads test results from stage 8
    # Returns: {
    #   'passed': int,
    #   'failed': int,
    #   'coverage': float
    # }
```

**GitHub CLI Integration**:
```bash
# Install gh if needed
# Set GitHub token: gh auth login

# Create PR
gh pr create --title "..." --body "..." --base main

# Check PR status
gh pr status

# Merge PR
gh pr merge --squash
```

**Output**:
- GitHub Pull Request created
- PR URL returned
- Merge ready for review

---

## File Structure

### Main Orchestrator Files

#### `workflow.py` (902 lines)
**Purpose**: Python version of workflow automation
**Key Features**:
- Dynamic step loading
- Checkpoint management
- Progress visualization
- Interactive or automated execution

**Main Function**:
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--change-id', required=True)
    parser.add_argument('--title', help='Change title')
    parser.add_argument('--owner', help='Change owner (@username)')
    parser.add_argument('--step', type=int, help='Specific step (0-12)')
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--archive', action='store_true')
    
    args = parser.parse_args()
    
    # Execute workflow...
```

**Usage**:
```bash
# List active changes
python workflow.py --list

# Create new change
python workflow.py --change-id my-feature --title "My Feature" --owner @username

# Run specific step
python workflow.py --change-id my-feature --step 5

# Dry run (preview only)
python workflow.py --change-id my-feature --step 8 --dry-run

# Validate change structure
python workflow.py --change-id my-feature --validate

# Archive completed change
python workflow.py --change-id my-feature --archive
```

#### `workflow.ps1` (2,910 lines)
**Purpose**: PowerShell version with Windows integration
**Advantages**:
- Direct Windows environment integration
- Registry access
- Windows event logging
- Scheduled task integration

**Usage**:
```powershell
# Run interactive workflow
.\scripts\workflow.ps1 -ChangeId "my-feature" -Title "My Feature" -Owner "@username"

# Run specific step
.\scripts\workflow.ps1 -ChangeId "my-feature" -Step 5

# List all changes
.\scripts\workflow.ps1 -List

# Validate
.\scripts\workflow.ps1 -ChangeId "my-feature" -Validate

# Archive
.\scripts\workflow.ps1 -ChangeId "my-feature" -Archive
```

#### `workflow2.ps1`
**Purpose**: Alternative PowerShell implementation
**Use Case**: Backup/fallback version

### Helper & Utility Files

#### `workflow-helpers.py` (737 lines)
**Purpose**: Shared utilities for all steps

**Key Functions**:
```python
# Output formatting
write_step(number, description)      # Print step header
write_info(message)                  # Info message (white)
write_success(message)               # Success message (green)
write_error(message)                 # Error message (red)
write_warning(message)               # Warning message (yellow)
write_error_hint(message, hint)     # Error with hint

# File operations
set_content_atomic(path, content)    # Write with atomic guarantees
get_content_safe(path)               # Read with error handling
validate_file_exists(path)           # Existence check

# Validation
validate_change_structure(change_path)  # Check directory layout
validate_documentation(change_path)     # Verify required files
validate_git_state(required_branch)     # Check git status

# Progress tracking
show_changes(changes_dir)            # Display all active changes
display_progress(change_path)        # Show workflow completion %
```

#### `progress_indicators.py`
**Purpose**: Terminal progress visualization

**Key Classes**:
```python
class StatusTracker:
    """Track status across steps"""
    def start_step(step: int, description: str)
    def update_progress(message: str, percent: int)
    def complete_step(status: bool)
    def get_summary() -> str

class ProgressSpinner:
    """Animated progress indicator"""
    def __init__(message: str, success_msg: str)
    def __enter__()
    def __exit__()
```

#### `checkpoint_manager.py`
**Purpose**: Workflow state persistence

**Key Functionality**:
```python
class CheckpointManager:
    """Manage workflow checkpoints"""
    
    def create_checkpoint(
        change_path: Path,
        step: int,
        state: dict
    ) -> str
        # Creates checkpoint directory
        # Saves state
        # Returns checkpoint ID
    
    def restore_checkpoint(
        change_path: Path,
        checkpoint_id: str
    ) -> dict
        # Restores saved state
        # Allows resumption at any step
        # Returns previous state
    
    def list_checkpoints(change_path: Path) -> List[str]
        # List all available checkpoints
```

#### `workflow_visualizer.py`
**Purpose**: Visual representation of workflow progress

**Features**:
- ASCII progress bars
- Step completion indicators
- Estimated time remaining
- Milestone tracking

#### `version_manager.py`
**Purpose**: Version number management

**Functions**:
```python
def get_current_version() -> str
def increment_version(part: str) -> str  # 'major', 'minor', 'patch'
def update_version_in_files(new_version: str) -> bool
def generate_version_tag(version: str) -> str
```

---

## Tools & Technologies

### Version Control: Git & GitHub

**Git Operations**:
```bash
git branch -b feature/<change-id>     # Create feature branch
git add <files>                        # Stage changes
git commit -m "<message>"              # Commit with message
git push origin feature/<change-id>    # Push to remote
git merge main                         # Merge with main
```

**GitHub Integration**:
```bash
gh pr create                           # Create pull request
gh pr review                           # Review PR
gh pr merge                            # Merge PR
gh issue create                        # Create issue
gh issue comment                       # Comment on issue
```

**Workflow in Git**:
- Feature branch per change: `feature/change-id`
- Commits: One logical commit per step
- PR: References issue, links documentation
- Merge strategy: Squash or rebase

### Python: Testing & Quality

#### pytest: Test Execution
```bash
# Run all tests
pytest tests/ -v

# Generate coverage
pytest tests/ --cov=agent --cov-report=html

# Run specific test
pytest tests/test_specific.py::TestClass::test_method

# Results:
# - test_results.txt: Test output
# - coverage.xml: Machine-readable coverage
# - htmlcov/: Interactive coverage report
```

#### ruff: Linting
```bash
# Check code quality
ruff check agent/
ruff format agent/

# Configuration in pyproject.toml:
[tool.ruff]
line-length = 88
target-version = "py311"
```

#### mypy: Type Checking
```bash
# Validate type hints
mypy agent/ --ignore-missing-imports

# Catches type errors before runtime
```

#### bandit: Security Scanning
```bash
# Scan for security vulnerabilities
bandit -r agent/ -f json -o bandit_report.json

# Detects:
# - Hardcoded passwords
# - SQL injection risks
# - Insecure imports
```

### Documentation Generation

#### Markdown Processing
- Template substitution
- Variable replacement
- Cross-reference linking
- Table generation

#### API Documentation
- Docstring extraction
- Parameter documentation
- Example generation
- Type hints to docs

#### Changelog Generation
```bash
# Automated changelog
git log --oneline | grep -E "^(feat|fix|docs)"
```

### OpenSpec: Change Governance

**Purpose**: Structured change management

**Key Components**:
```
openspec/
├── changes/              # Active work
│   └── <change-id>/
│       ├── todo.md
│       ├── proposal.md
│       ├── spec.md
│       ├── tasks.md
│       ├── test_plan.md
│       └── .checkpoints/
├── archive/              # Completed
│   └── <timestamp>-<change-id>/
├── templates/            # Reusable formats
└── PROJECT_WORKFLOW.md   # Specification
```

**Validation Scripts**:
```bash
# Validate all changes
./openspec/scripts/validate-all.ps1

# Create new change
./openspec/scripts/create-change.ps1 -ChangeId my-feature

# Apply change (move to active)
./openspec/scripts/apply-change.ps1 -ChangeId my-feature

# Archive change
./openspec/scripts/archive-change.ps1 -ChangeId my-feature
```

### GitHub Copilot Integration

**Purpose**: AI-assisted code generation

**Used In**:
- `workflow-step06.py`: Generate implementation scaffolding
- `workflow-step07.py`: Generate test templates
- Documentation generation

**Triggers**:
- Code completion (`Ctrl+Space`)
- Line completion (`Ctrl+Enter`)
- Chat interface (GitHub Copilot Chat)

---

## Entry Points

### Interactive CLI Usage

#### Python
```bash
cd scripts

# List all active changes
python workflow.py --list

# Start new change
python workflow.py \
  --change-id feature-docs-update \
  --title "Update Documentation" \
  --owner "@johndoe"

# Run specific step
python workflow.py --change-id feature-docs-update --step 2

# Preview without changes
python workflow.py --change-id feature-docs-update --step 5 --dry-run

# Validate change directory
python workflow.py --change-id feature-docs-update --validate

# Archive after completion
python workflow.py --change-id feature-docs-update --archive
```

#### PowerShell
```powershell
cd scripts

# List changes
.\workflow.ps1 -List

# Interactive workflow
.\workflow.ps1 -ChangeId "feature-docs-update" -Title "Update Documentation" -Owner "@johndoe"

# Specific step
.\workflow.ps1 -ChangeId "feature-docs-update" -Step 2

# Validate
.\workflow.ps1 -ChangeId "feature-docs-update" -Validate

# Archive
.\workflow.ps1 -ChangeId "feature-docs-update" -Archive
```

### Programmatic Usage

```python
from workflow import load_step_module
from pathlib import Path

# Load and execute a step
step_module = load_step_module(2)  # Stage 2: Proposal

change_path = Path("openspec/changes/my-feature")
success = step_module.invoke_step2(change_path)

if success:
    print("Step 2 completed successfully!")
```

### GitHub Actions Integration

```yaml
name: Workflow Stage
on: [workflow_dispatch]

jobs:
  run-workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Workflow Step
        run: |
          cd scripts
          python workflow.py \
            --change-id ${{ github.event.inputs.change_id }} \
            --step ${{ github.event.inputs.step }}
```

---

## Configuration & Setup

### Environment Variables

```bash
# Git configuration
export GIT_USER_NAME="Your Name"
export GIT_USER_EMAIL="your@email.com"

# GitHub authentication
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Workflow configuration
export WORKFLOW_STEP_TIMEOUT=300        # 5 minutes per step
export WORKFLOW_AUTO_CHECKPOINT=true    # Auto-save after step
export WORKFLOW_VERBOSE=true            # Verbose logging

# Python environment
export PYTHONPATH="./scripts"
```

### pyproject.toml Configuration

```toml
[project]
name = "obsidian-ai-agent"
version = "0.1.38"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=agent --cov-report=html --cov-report=term"
```

### Git Configuration

```bash
# Configure git
git config user.name "Your Name"
git config user.email "your@email.com"

# Git hooks for workflow validation
.git/hooks/pre-commit    # Validate before commit
.git/hooks/pre-push      # Validate before push

# Feature branch naming
git checkout -b feature/change-id
```

### GitHub CLI Configuration

```bash
# Authenticate with GitHub
gh auth login

# Set default repository
gh repo set-default owner/repo

# Configure PR template
# Create .github/pull_request_template.md
```

---

## Integration Points

### With pytest

**Execution in Step 8**:
```python
def run_tests(change_path: Path) -> tuple[bool, dict]:
    """Run tests and return results"""
    
    result = subprocess.run(
        ["pytest", "tests/", 
         "--cov=agent", 
         "--cov-report=html",
         "--cov-report=term",
         "-v"],
        capture_output=True,
        text=True
    )
    
    return result.returncode == 0, {
        'passed': count_passed(result.stdout),
        'failed': count_failed(result.stdout),
        'coverage': extract_coverage(result.stdout)
    }
```

### With GitHub

**PR Creation in Step 12**:
```python
def create_github_pr(branch: str, title: str, body: str) -> int:
    """Create PR using GitHub CLI"""
    
    result = subprocess.run([
        "gh", "pr", "create",
        "--title", title,
        "--body", body,
        "--base", "main",
        "--head", branch
    ], capture_output=True, text=True)
    
    # Extract PR number from output
    return extract_pr_number(result.stdout)
```

### With Git

**Commit in Step 10**:
```python
def commit_changes(change_path: Path, message: str) -> bool:
    """Stage and commit changes"""
    
    # Stage files
    subprocess.run(["git", "add", "."], cwd=change_path.parent.parent)
    
    # Create commit
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=change_path.parent.parent
    )
    
    # Push to remote
    subprocess.run(
        ["git", "push", "origin", "feature/..."],
        cwd=change_path.parent.parent
    )
    
    return True
```

### With OpenSpec

**Governance Integration**:
- Validates change structure before workflow
- Enforces documentation requirements
- Tracks governance compliance
- Generates compliance reports

### With Copilot

**Code Generation in Step 6**:
```python
def generate_with_copilot(prompt: str) -> str:
    """Generate code using Copilot"""
    
    # Can integrate with Copilot API
    # For now, uses templates + variables
    
    template = get_template("test_scaffold.py")
    return template.render(
        module_name=extract_module(prompt),
        test_functions=extract_tests(prompt)
    )
```

---

## Error Handling & Validation

### Validation Layers

#### 1. Pre-Stage Validation
```python
def validate_before_step(
    change_path: Path,
    step: int
) -> tuple[bool, str]:
    """Validate state before starting step"""
    
    # Check required files exist
    if step > 2 and not (change_path / "proposal.md").exists():
        return False, "proposal.md not found"
    
    # Check previous step completed
    todo_path = change_path / "todo.md"
    if not is_step_marked_complete(todo_path, step - 1):
        return False, f"Step {step - 1} not marked complete"
    
    # Check required git state
    if step > 10 and not has_feature_branch():
        return False, "Feature branch not created"
    
    return True, "All checks passed"
```

#### 2. Post-Stage Validation
```python
def validate_after_step(
    change_path: Path,
    step: int
) -> tuple[bool, str]:
    """Validate step output"""
    
    if step == 2:  # After proposal
        files_created = [
            (change_path / "proposal.md").exists(),
        ]
        return all(files_created), "Proposal files verified"
    
    if step == 8:  # After testing
        tests_passed = check_test_results(change_path)
        return tests_passed, "Tests validation complete"
    
    return True, "Step validation complete"
```

#### 3. Quality Gates (Lane-Specific)

The workflow enforces lane-specific quality thresholds through `scripts/quality_gates.py`:

**Standard Lane Thresholds** (Regular Changes)
```python
QUALITY_GATES_STANDARD = {
    'ruff': {'max_errors': 0, 'description': '0 linting errors'},
    'mypy': {'max_errors': 0, 'description': '0 type errors'},
    'pytest': {
        'min_pass_rate': 0.80,     # 80% of tests must pass
        'min_coverage': 0.70,      # 70% coverage minimum
        'description': '≥80% pass rate, ≥70% coverage'
    },
    'bandit': {
        'max_high_severity': 0,
        'description': '0 high-severity security issues'
    },
}
```

**Heavy Lane Thresholds** (Critical/Production Changes)
```python
QUALITY_GATES_HEAVY = {
    'ruff': {'max_errors': 0, 'description': '0 linting errors'},
    'mypy': {'max_errors': 0, 'description': '0 type errors'},
    'pytest': {
        'min_pass_rate': 1.0,      # 100% of tests must pass
        'min_coverage': 0.85,      # 85% coverage minimum
        'description': '100% pass rate, ≥85% coverage'
    },
    'bandit': {
        'max_high_severity': 0,
        'description': '0 high-severity security issues'
    },
}
```

**Docs Lane** (Documentation-Only Changes)
```python
# Docs lane: Quality gates are DISABLED
# No code validation required for documentation-only changes
QUALITY_GATES_DOCS = {}
```

**Execution**:
```bash
# Run quality gates for standard lane
python scripts/quality_gates.py /path/to/project --lane standard

# Run quality gates for heavy lane (stricter)
python scripts/quality_gates.py /path/to/project --lane heavy --output quality_metrics.json

# Output includes: quality_metrics.json, htmlcov/index.html, bandit_report.json
```

**Stage 8 Integration**: When Step 8 executes, quality gates are automatically run with the lane-specific thresholds. Workflow stops if thresholds aren't met (unless `--skip-quality-gates` flag is used for local testing).

### Error Recovery

#### Checkpoint System
```python
def handle_step_error(
    change_path: Path,
    step: int,
    error: Exception
) -> bool:
    """Handle step errors with recovery"""
    
    # Create error checkpoint
    error_state = {
        'step': step,
        'error': str(error),
        'timestamp': datetime.now().isoformat(),
        'file_state': capture_file_state(change_path)
    }
    
    checkpoint_manager.save_error_checkpoint(
        change_path, step, error_state
    )
    
    # Prompt for recovery
    print(f"Error in step {step}: {error}")
    print("Options:")
    print("  1. Retry step")
    print("  2. Restore from checkpoint")
    print("  3. Skip to next step (risky)")
    print("  4. Abort workflow")
    
    # User choice determines recovery path
    return recover_from_error(choice)
```

#### Rollback Capability
```python
def rollback_to_checkpoint(
    change_path: Path,
    checkpoint_id: str
) -> bool:
    """Restore files and state from checkpoint"""
    
    checkpoint = checkpoint_manager.load_checkpoint(checkpoint_id)
    
    for filepath, content in checkpoint['files'].items():
        (change_path / filepath).write_text(content)
    
    return restore_complete
```

---

## Checkpoints & Resumption

### Checkpoint Structure

```
openspec/changes/my-change/
└── .checkpoints/
    ├── checkpoint-20251022-143000-step00/
    │   ├── state.json           # Step state
    │   ├── todo.md              # Files at checkpoint
    │   ├── proposal.md          # ...
    │   └── manifest.json        # What was saved
    │
    ├── checkpoint-20251022-145030-step01/
    │   └── (same structure)
    │
    └── checkpoint-20251022-150500-step02/
        └── (same structure)
```

### Resumption Process

```python
def resume_workflow(change_id: str):
    """Resume from last checkpoint"""
    
    change_path = CHANGES_DIR / change_id
    
    # Find last checkpoint
    checkpoints = checkpoint_manager.list_checkpoints(change_path)
    if not checkpoints:
        print("No checkpoints found, starting from beginning")
        return start_workflow(change_id)
    
    last_checkpoint = checkpoints[-1]
    last_step = extract_step_number(last_checkpoint)
    
    # Restore state
    checkpoint_manager.restore_checkpoint(change_path, last_checkpoint)
    
    # Ask user
    print(f"Found checkpoint at step {last_step}")
    print("Continue from here? (y/n)")
    
    if input().lower() == 'y':
        return continue_workflow(change_id, last_step + 1)
    else:
        return restart_workflow(change_id)
```

---

## Advanced Features

### Parallel Step Execution

**Supported Parallelization**:
- Steps 2-6 can run in parallel (documentation generation)
- Steps 10-12 can run in parallel (git + PR creation)

```python
from concurrent.futures import ThreadPoolExecutor

def run_parallel_steps(
    change_path: Path,
    steps: List[int]
) -> List[bool]:
    """Execute steps in parallel"""
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_step, change_path, step): step
            for step in steps
        }
        
        results = {}
        for future in concurrent.futures.as_completed(futures):
            step = futures[future]
            results[step] = future.result()
    
    return [results[s] for s in steps]
```

### Dry-Run Mode

```python
def run_step_dry_run(
    change_path: Path,
    step: int
) -> str:
    """Preview what step would do"""
    
    preview = f"""
    === DRY RUN: Step {step} ===
    
    Would create files:
    - {change_path / 'file1.md'}
    - {change_path / 'file2.py'}
    
    Would modify files:
    - agent/backend.py (+50 lines)
    
    Would run commands:
    - pytest tests/ --cov
    - git commit -m "..."
    
    Would create:
    - Branch: feature/change-id
    - PR: to main
    
    Run with --step {step} to execute
    """
    
    return preview
```

### Conditional Step Execution

```python
def should_execute_step(
    change_path: Path,
    step: int
) -> bool:
    """Determine if step should execute"""
    
    proposal = (change_path / "proposal.md").read_text()
    
    if step == 6:  # Script generation
        # Skip if proposal says "no scripts needed"
        return "no scripts needed" not in proposal.lower()
    
    if step == 7:  # Implementation
        # Skip if it's documentation-only change
        return not proposal.lower().startswith("doc only:")
    
    return True
```

### Multi-Branch Workflows

```python
def create_multi_branch_workflow(
    change_ids: List[str]
) -> dict:
    """Run workflow for multiple changes"""
    
    results = {}
    for change_id in change_ids:
        branch = f"feature/{change_id}"
        
        # Create branch
        subprocess.run(["git", "checkout", "-b", branch])
        
        # Run workflow
        results[change_id] = run_workflow(change_id)
        
        # Switch back
        subprocess.run(["git", "checkout", "main"])
    
    return results
```

### Custom Hooks

```python
# pre_step_hooks: Run before each step
PRE_STEP_HOOKS = {
    1: validate_git_user,
    6: check_disk_space,
    12: verify_github_token
}

# post_step_hooks: Run after each step
POST_STEP_HOOKS = {
    2: notify_reviewers,
    8: upload_test_results,
    12: post_to_slack
}

def run_with_hooks(change_path: Path, step: int) -> bool:
    # Run pre-hooks
    for hook in PRE_STEP_HOOKS.get(step, []):
        if not hook():
            return False
    
    # Run step
    success = run_step(change_path, step)
    
    # Run post-hooks
    if success:
        for hook in POST_STEP_HOOKS.get(step, []):
            hook()
    
    return success
```

---

## Summary

The OpenSpec Workflow is a comprehensive, **13-stage automated process** that manages code changes from inception to production. It integrates:

- ✅ **Git & GitHub**: Version control and PR management
- ✅ **pytest**: Test automation and quality gates
- ✅ **OpenSpec**: Change governance and documentation
- ✅ **Python/PowerShell**: Cross-platform automation
- ✅ **Checkpoints**: State persistence and recovery
- ✅ **Validation**: Multi-layer quality assurance

Each stage has clear responsibilities, validation gates, and automated tooling. The system ensures that all changes are properly documented, tested, reviewed, and tracked for governance compliance.

### Quick Reference: Workflow Stages

| Step | Purpose | Duration | Key Tools |
|------|---------|----------|-----------|
| 0 | Create TODOs | 1 min | Templates |
| 1 | Version Bump | 5 min | Git, semantic-versioning |
| 2 | Proposal | 30 min | Markdown, templates |
| 3 | Specification | 1 hour | Design, architecture |
| 4 | Task Breakdown | 30 min | Planning, estimation |
| 5 | Test Definition | 1 hour | pytest, test planning |
| 6 | Script Generation | 1-2 hours | Code generation, templates |
| 7 | Implementation | 4-8 hours | Python, development |
| 8 | Testing | 1-2 hours | pytest, coverage, quality gates |
| 9 | Documentation | 1-2 hours | Markdown, API docs |
| 10 | Git Operations | 10 min | Git, branch management |
| 11 | Archive | 5 min | File organization |
| 12 | Pull Request | 20 min | GitHub CLI, PR templates |

**Total Time**: 12-16 hours per change (distributed over days)

---

**Document Generated**: October 22, 2025
**Version**: 1.0
**Status**: ✅ Complete
